#include "CurlDownloader.h"
#include "downloader/DownloadListener.h"
#include "downloader/downloader.h"
#include "metalink/metalink.h"
#include "util/sys.h"
#include "util/sha1.h"
#include "util/tstr.h"
#include "util/logger.h"
#include <curl/curl.h>
#include <boost/random.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/filesystem/operations.hpp>
#include <boost/cstdint.hpp>
#include <boost/format.hpp>
#include <string>
#include <sstream>
#include <fstream>
#include <cmath>

using namespace std;
using namespace tstr;
using namespace boost::posix_time;
namespace fs = boost::filesystem;

namespace downloader {

static char g_libcurlerror[CURL_ERROR_SIZE];

// Constructor. "listener" is a DownloadListener, which will receive status messages and get asked about whether to cancel.
CurlDownloader::CurlDownloader(DownloadListener& listener) : _listener(listener)
{
    LOG2FILE(TSTR("CurlDownloader::CurlDownloader()"));
    // Init libcurl.
    _curl = curl_easy_init();
    if(!_curl) THROW_DOWNLOADER_EX("curl_easy_init() failed!");
    // Seed the random number generator, so that we won't connect to the same mirror every time,
    ptime time(microsec_clock::local_time());
    time_duration td = time.time_of_day();
    boost::uint32_t seed = static_cast<boost::uint32_t>(td.total_microseconds());
    _rng.seed(seed);
}

// Destructor.
CurlDownloader::~CurlDownloader()
{
    LOG2FILE(TSTR("CurlDownloader::~CurlDownloader()"));
    curl_easy_cleanup(_curl);
}

// Add the files in ml to the list of files to be downloaded. Call download() to actually download them.
void CurlDownloader::add_metalink(metalink::Metalink ml)
{
    LOG2FILE(TSTR("CurlDownloader::add_metalink()"));
    for(unsigned int i = 0; i < ml.files.size(); i++) {
        _ml.files.push_back(ml.files.at(i));
        LOG2FILE(TSTR("Adding ")+ml.files.at(i).filename);
    }
}

// Downloads all files in _ml and returns when done.
int CurlDownloader::download()
{
    LOG2FILE(TSTR("CurlDownloader::download()"));
    _state = STATE_READY;
    // Download each file in _ml, as long as the user don't cancel and nothing fails.
    while(_ml.files.size() > 0 &&
        _state != STATE_FILE_FAILED &&
        !_listener.download_cancel())
    {
        // Get the next file to download
        metalink::MetalinkFile file = _ml.files.back();
        _ml.files.pop_back();
        // Prepare the download
        _prepare_download(file);
        // Now download the file
        _download_file();
    }
    // The download failed.
    if(_state == STATE_FILE_FAILED) {
        LOG2FILE(TSTR("CurlDownloader::download(): download failed."));
        return RESULT_ERROR;
    }
    // The download was canceled.
    else if(_state == STATE_CANCELED) {
        LOG2FILE(TSTR("CurlDownloader::download(): download was canceled."));
        return RESULT_CANCELED;
    }
    // The download was finished successfully.
    else {
        LOG2FILE(TSTR("CurlDownloader::download(): download was successful."));
        return RESULT_OK;
    }
}

void CurlDownloader::set_country(tstr::tstring country)
{
    _country = country;
}

// Prepares "file" to be downloaded next.
void CurlDownloader::_prepare_download(metalink::MetalinkFile file)
{
    LOG2FILE(TSTR("CurlDownloader::_prepare_download()"));
    // Set the current file to be downloaded.
    _file = file;
    // Fill _mirrors with the correct mirrors for the new _file.
    _mirrors.clear();
    unsigned int i;
    for(i = 0; i < _file.urls.size(); i++) {
        Mirror new_mirror(_file.urls.at(i));
        _mirrors.push_back(new_mirror);
    }
    // Init hash checking
    _bytes_verified = 0;
    _sha1_bytes = 0;
    _sha1.init();
    // Send progress update to _listener
    _listener.download_progress(0);
}

// Downloads the current file. Will try indefinitely, until it succeeds.
void CurlDownloader::_download_file()
{
    LOG2FILE(TSTR("CurlDownloader::_download_file()"));
    _state = STATE_DOWNLOADING;
    // Try to download the file until the user cancels or the download finishes (successfully or with a fatal error).
    while(_state == STATE_DOWNLOADING && !_listener.download_cancel())
    {
        // Choose one of the mirrors and put it in _mirrors (removes it from the list).
        _choose_mirror();
        // Tell libcurl to download from this mirror
        _curl_download();
        // Add the mirror to the list again
        _mirrors.push_back(_mirror);
    }
    // The file was canceled.
    if(_state == STATE_DOWNLOADING && _listener.download_cancel()) {
        _state = STATE_CANCELED;
    }
    // The file was successfully downloaded!
    else if(_state == STATE_FILE_DONE) {
        // Try to parse the file, if it looks like a metalink.
        if(_file.filename.find(TSTR(".metalink")) != tstring::npos) {
            try {
                LOG2FILE(TSTR("Trying to parse ")+_file.filename+TSTR(" as a metalink."));
                // Try to load the "metalink" (we hope it is a metalink, at least).
                metalink::Metalink ml = metalink::load_file(t2s(_file.filename));
                LOG2FILE(TSTR("Parsing successful!"));
                // Add it to the download queue, if it worked.
                add_metalink(ml);
                throw exception();
            }
            catch(exception& e) {
                // It probably wasn't a metalink (or something else went wrong).
                LOG2FILE(TSTR("Parsing failed: ")+s2t(e.what()));
            }
        }
    }
}

// Chooses a mirror. This is the "brain" of the downloader. Uses a quite simple random strategy.
void CurlDownloader::_choose_mirror()
{
    LOG2FILE(TSTR("CurlDownloader::_choose_mirror()"));
    // Find out how good the best mirrors are
    list<Mirror>::iterator it;
    int min_errors = 1000;
    int max_preference = -1;
    int num_best = 0;
    bool country = false; // Is there a country in _country?
    for (it = _mirrors.begin(); it != _mirrors.end(); it++)
    {
        if((*it).errors < min_errors) {
            min_errors = (*it).errors;
            max_preference = (*it).preference;
            country = (_country == (*it).location) && (_country.length() > 0);
            num_best = 1;
        }
        else if((*it).errors == min_errors) {
            if(_country.length() > 0 && _country == (*it).location && !country) {
                country = true;
                max_preference = (*it).preference;
                num_best = 1;
            }
            else if(_country.length() == 0 ||
                (_country == (*it).location && country) ||
                (_country != (*it).location && !country))
            {
                if((*it).preference > max_preference) {
                    max_preference = (*it).preference;
                    num_best = 1;
                }
                else if((*it).preference == max_preference){
                    num_best++;
                }
            }
        }
    }
    // Choose one of the best mirrors
    boost::uniform_int<> mirror_range(1, num_best);
    boost::variate_generator<boost::mt19937&, boost::uniform_int<> > random_mirror(_rng, mirror_range);
    int mirror_id = random_mirror();
    // Find our random mirror and subtract min_errors from all mirrors at the same time
    list<Mirror>::iterator best_mirror;
    for (it = _mirrors.begin(); it != _mirrors.end(); it++)
    {
        if((*it).errors == min_errors && (*it).preference == max_preference &&
            (!country || _country == (*it).location))
        {
            mirror_id--;
            if(mirror_id == 0) best_mirror = it;
        }
        (*it).errors -= min_errors;
    }
    // Prepare the choosen mirror
    _mirror = *best_mirror;
    _mirrors.erase(best_mirror);
    LOG2FILE(TSTR("Chosen mirror: ") + _mirror.url);
}

// This callback function is called directly by libcurl when new data arrives. Calls curl_write() on the CurlDownloader object.
size_t curl_write_callback(void *ptr, size_t size, size_t nmemb, void *userdata)
{
    CurlDownloader* downloader = static_cast<CurlDownloader*>(userdata);
    string data = string(static_cast<char*>(ptr), size*nmemb);
    bool cancel = downloader->curl_write(data);
    if(cancel) return 0;
    return size*nmemb;
}

// This callback function is called directly by libcurl with progress info. Calls curl_progress() on the CurlDownloader object.
int curl_progress_callback(void *userdata, double dltotal, double dlnow, double ultotal, double ulnow)
{
    CurlDownloader* downloader = static_cast<CurlDownloader*>(userdata);
    bool cancel = downloader->curl_progress(dltotal, dlnow);
    return cancel;
}

// Makes a single transfer, using libcurl. Will return when the whole file is downloaded or the transfer either fails or is interrupted.
// It will take care of transfer errors, before returning, and will usually get called again using another mirror (ie if not successful).
void CurlDownloader::_curl_download()
{
    LOG2FILE(TSTR("CurlDownloader::_curl_download()"));
    // Update status and progress data
    _last_progress = ptime(microsec_clock::local_time());
    _last_downloaded = 0;
    _speed = 0;
    // Init the download (if possible resuming an old download).
    _downloaded = 0;
    double file_size = 0;
    fs::path target(t2s(_file.filename));
    // If file already exists.
    if(fs::exists(target) && fs::is_regular(target)) {
        // Get file size
        file_size = static_cast<double>(fs::file_size(target));
        LOG2FILE(_file.filename + TSTR(" exists. File size = ") + num2str(file_size));
        _start_size = file_size;
        if(_start_size > _file.size && _file.size > 0) {
            _start_size = static_cast<double>(_file.size);
        }
        // Check piece hashes
        _check_pieces();
        // Return if the user canceled the download.
        if(_listener.download_cancel()) return;
        // Truncate file, if necessary.
        if(file_size > _start_size) {
            LOG2FILE(TSTR("Truncating file."));
            sys::truncate_file(_file.filename, static_cast<boost::uint64_t>(_start_size));
        }
        // Check if the file is already completed.
        if(_start_size == _file.size && _file.size > 0) {
            LOG2FILE(_file.filename + TSTR(" is already downloaded."));
            // Check hashes.
            bool hash_failed = _check_hash();
            // Return if the user canceled the download.
            if(_listener.download_cancel()) return;
            // Was the hash check successful?
            if(hash_failed) {
                LOG2FILE(TSTR("Hash check failed!"));
                if(_bytes_verified == _file.size && _file.size > 0) {
                    LOG2FILE(TSTR("Interpretation: Fatal error!"));
                    _state = STATE_FILE_FAILED;
                    return;
                } else {
                    LOG2FILE(TSTR("Interpretation: non-fatal error. Trying again from the beginning."));
                    sys::truncate_file(_file.filename, static_cast<boost::uint64_t>(0));
                }
            } else {
                _state = STATE_FILE_DONE;
                return;
            }
        }
    }
    // If file don't exist.
    else {
        LOG2FILE(_file.filename + TSTR(" don't exist."));
        _start_size = 0;
        _bytes_verified = 0;
        _sha1_bytes = 0;
        _sha1.init();
    }
    // Open output file
    _outfile.open(t2s(_file.filename).c_str(), ios_base::app | ios_base::binary);
    if(_outfile.fail()) {
        LOG2FILE(TSTR("_outfile.open() failed!"));
        _state = STATE_FILE_FAILED;
        return;
    }
    // Set options
    curl_easy_setopt(_curl, CURLOPT_WRITEFUNCTION, curl_write_callback);
    curl_easy_setopt(_curl, CURLOPT_WRITEDATA, this);
    curl_easy_setopt(_curl, CURLOPT_NOPROGRESS, 0);
    curl_easy_setopt(_curl, CURLOPT_PROGRESSFUNCTION, curl_progress_callback);
    curl_easy_setopt(_curl, CURLOPT_PROGRESSDATA, this);
    curl_easy_setopt(_curl, CURLOPT_FAILONERROR, 1);
    curl_easy_setopt(_curl, CURLOPT_URL, t2s(_mirror.url).c_str());
    curl_easy_setopt(_curl, CURLOPT_AUTOREFERER, 1);
    curl_easy_setopt(_curl, CURLOPT_FOLLOWLOCATION, 1);
    curl_easy_setopt(_curl, CURLOPT_MAXREDIRS, 10);
    curl_easy_setopt(_curl, CURLOPT_CONNECTTIMEOUT, 10);
    curl_easy_setopt(_curl, CURLOPT_LOW_SPEED_LIMIT, 100);
    curl_easy_setopt(_curl, CURLOPT_LOW_SPEED_TIME, 20);
    curl_easy_setopt(_curl, CURLOPT_ERRORBUFFER, g_libcurlerror);
    curl_easy_setopt(_curl, CURLOPT_RESUME_FROM_LARGE, static_cast<curl_off_t>(_start_size));
    // Update status
    LOG2FILE(TSTR("Connecting to ") + _mirror.url);
    if(_file.size > 0) {
        _listener.download_progress(static_cast<int>(1000.0*_start_size/_file.size));
    } else {
        _listener.download_progress(static_cast<int>(0));
    }
    _listener.download_status(TSTR("Connecting to ") + _mirror.url, true);
    // Download using these options
    CURLcode result = curl_easy_perform(_curl);
    // Close output file
    _outfile.close();
    // Make sure the file is no larger than meant to be.
    file_size = static_cast<double>(fs::file_size(target));
    LOG2FILE(TSTR("Transfer of ") + _file.filename + TSTR(" stopped. File size = ") + num2str(file_size));
    if(file_size > _file.size && _file.size > 0) {
        LOG2FILE(TSTR("Truncating file."));
        sys::truncate_file(_file.filename, _file.size);
    }
    // Check file hash, if successful (so we know if it really was successful).
    bool hash_failed = false;
    if(result == CURLE_OK && _state != STATE_PIECE_FAILED) {
        hash_failed = _check_hash();
    }
    // Check result
    if(result != CURLE_OK || _state == STATE_PIECE_FAILED || hash_failed) {
        LOG2FILE(TSTR("CurlDownloader::_curl_download(): result != CURLE_OK || _state == STATE_PIECE_FAILED"));
        if((result == CURLE_WRITE_ERROR || result == CURLE_ABORTED_BY_CALLBACK) &&
            _state != STATE_PIECE_FAILED)
        {
            LOG2FILE(TSTR("CurlDownloader::_curl_download(): Reason: canceled."));
        }
        else {
            // Remember this error...
            _mirror.errors++;
            // A piece check failed. We'll continue trying, after truncating it,.
            if(_state == STATE_PIECE_FAILED) {
                LOG2FILE(TSTR("Piece failed. Truncating file."));
                sys::truncate_file(_file.filename, static_cast<boost::uint64_t>(_bytes_verified));
                _state = STATE_DOWNLOADING;
            }
            else if(hash_failed) {
                LOG2FILE(TSTR("Hash failed."));
                if(_bytes_verified == _file.size && _file.size > 0) {
                    LOG2FILE(TSTR("Interpretation: Fatal error!"));
                    _state = STATE_FILE_FAILED;
                } else {
                    LOG2FILE(TSTR("Interpretation: non-fatal error. Trying again from the beginning."));
                    sys::truncate_file(_file.filename, static_cast<boost::uint64_t>(0));
                }
            }
            else {
                LOG2FILE(TSTR("libcurl error: ")+s2t(g_libcurlerror));
            }
        }
    }
    else {
        LOG2FILE(TSTR("CurlDownloader::_curl_download(): result == CURLE_OK"));
        // Take note of our success!
        _state = STATE_FILE_DONE;
    }
}

// Checks unverified data, using piece hashes.
void CurlDownloader::_check_pieces()
{
    LOG2FILE(TSTR("CurlDownloader::_check_pieces()"));
    // Are there any piece hashes available?
    if(_file.piece_type != TSTR("sha1")) return;
    if(_file.piece_length <= 0) return;
    // Update status.
    _listener.download_progress(static_cast<int>(0));
    _listener.download_status(TSTR("Checking piece hashes..."), true);
    double num_pieces = ceil(static_cast<double>(_start_size)/_file.piece_length);
    // Start checking!
    ifstream fin(t2s(_file.filename).c_str(), ios_base::binary);
    if(fin.fail()) return;
    for(unsigned int i = 0; i < _file.piece_hashes.size(); i++) {
        // Check this piece, if at least a part of it has not yet been verified.
        if(_file.piece_length*(i+1) > _bytes_verified) {
            _bytes_verified = _file.piece_length*i;
            _sha1_bytes = 0;
            _sha1.init();
            char buf[1024];
            while(fin.good())
            {
                // Read some data (max the rest of the piece)
                double num_to_read = sizeof(buf);
                if(_sha1_bytes + num_to_read > _file.piece_length) {
                    num_to_read = _file.piece_length - _sha1_bytes;
                }
                if(_bytes_verified + _sha1_bytes + num_to_read > _start_size) {
                    num_to_read = _start_size - _bytes_verified - _sha1_bytes;
                }
                fin.read(buf, static_cast<std::streamsize>(num_to_read));
                string data(buf, fin.gcount());
                // Process data
                _sha1.update(data);
                _sha1_bytes += data.length();
                if(_sha1_bytes == _file.piece_length) break;
                if(_bytes_verified + _sha1_bytes == _start_size) break;
                // Stop if the user cancels.
                if(_listener.download_cancel()) break;
            }
            // Check hash
            if(_sha1_bytes == _file.piece_length ||
                (_bytes_verified + _sha1_bytes == _file.size && _file.size > 0))
            {
                // Hash check succeded
                if(_sha1.hex() == _file.piece_hashes[i]) {
                    _bytes_verified = _file.piece_length*(i+1);
                    LOG2FILE(TSTR("Piece OK: ")+num2str(i));
                }
                // Hash check failed
                else {
                    // The file will later get truncated (really important).
                    LOG2FILE(TSTR("Piece failed: ")+num2str(i));
                    LOG2FILE(TSTR("_sha1.hex() = ")+_sha1.hex());
                    LOG2FILE(TSTR("_file.piece_hashes[i] = ")+_file.piece_hashes[i]);
                    LOG2FILE(TSTR("_sha1_bytes = ")+num2str(_sha1_bytes));
                    LOG2FILE(TSTR("_file.piece_length = ")+num2str(_file.piece_length));
                    LOG2FILE(TSTR("_bytes_verified = ")+num2str(_bytes_verified));
                    LOG2FILE(TSTR("_file.size() = ")+num2str(_file.size));
                    _start_size = _bytes_verified;
                    _sha1.init();
                    _sha1_bytes = 0;
                    break;
                }
            }
            // Didn't read the whole hash (probably end of file). We'll have to continue downloading here.
            else {
                // The file will later get truncated, if needed (really important).
                _start_size = _bytes_verified + _sha1_bytes;
                LOG2FILE(TSTR("Partial piece: ")+num2str(i));
                break;
            }
        }
        // This piece has already been verified. Move one piece forward in the file, if possible.
        else if(_file.piece_length*(i+1) < _start_size) {
            fin.seekg(_file.piece_length, ios::cur);
        }
        // We have reached the end of the file. Stop checking.
        else {
            break;
        }
        _listener.download_progress(static_cast<int>(1000.0*(i+1)/num_pieces));
        // Stop if the user cancels.
        if(_listener.download_cancel()) break;
    }
    fin.close();
    _listener.download_progress(static_cast<int>(1000));
}

void CurlDownloader::_check_piece(std::string data)
{
    if(_file.piece_hashes.size() == 0) return;
    while(data.length() > 0)
    {
        // Extract max _file.piece_length number of bytes
        double num_to_hash = data.length();
        if(_sha1_bytes + num_to_hash > _file.piece_length) {
            num_to_hash = _file.piece_length - _sha1_bytes;
        }
        string hashdata = data.substr(0, static_cast<unsigned int>(num_to_hash));
        data = data.substr(static_cast<unsigned int>(num_to_hash));
        // Process data
        _sha1.update(hashdata);
        _sha1_bytes += hashdata.length();
        // Check that the data doesn't extend beyond the end of the file.
        if(_bytes_verified + _sha1_bytes > _file.size) {
            LOG2FILE(TSTR("Data beyond end of file! TRUNCATE!!"));
            _state = STATE_PIECE_FAILED;
            break;
        }
        // If we have completed a piece, we should check it.
        if(_sha1_bytes == _file.piece_length ||
            (_bytes_verified + _sha1_bytes == _file.size && _file.size > 0))
        {
            unsigned int piece_id = static_cast<unsigned int>(_bytes_verified/_file.piece_length);
            // The hash matched!
            if(_file.piece_hashes.size() > piece_id &&
                _sha1.hex() == _file.piece_hashes[piece_id])
            {
                _bytes_verified += _sha1_bytes;
                LOG2FILE(TSTR("Piece OK: ")+num2str(piece_id));
            }
            else {
                LOG2FILE(TSTR("Piece failed: ")+num2str(piece_id));
                LOG2FILE(TSTR("_sha1.hex() = ")+_sha1.hex());
                LOG2FILE(TSTR("_file.piece_hashes[piece_id] = ")+_file.piece_hashes[piece_id]);
                LOG2FILE(TSTR("_sha1_bytes = ")+num2str(_sha1_bytes));
                LOG2FILE(TSTR("_file.piece_length = ")+num2str(_file.piece_length));
                LOG2FILE(TSTR("_bytes_verified = ")+num2str(_bytes_verified));
                LOG2FILE(TSTR("_file.size() = ")+num2str(_file.size));
                _state = STATE_PIECE_FAILED;
                break;
            }
            _sha1.init();
            _sha1_bytes = 0;
        }
    }
}

// Check a full-file hash and return true on failure. Only supports SHA1, right now.
bool CurlDownloader::_check_hash()
{
    // Check that there's a sha1 hash available.
    if(_file.hashes.count(TSTR("sha1")) == 1) {
        LOG2FILE(TSTR("Calculating SHA-1 hash..."));
        // Open file
        ifstream file(t2s(_file.filename).c_str(), ios_base::in | ios_base::binary);
        if(file.fail()) {
            LOG2FILE(TSTR("Failed to open file!"));
            return true;
        }
        // Prepare hashing
        _sha1.init();
        double file_size = static_cast<double>(fs::file_size(_file.filename));
        double bytes_read = 0;
        _listener.download_progress(static_cast<int>(0));
        _listener.download_status(TSTR("Calculating SHA-1 hash..."), true);
        // Hash file
        char buf[1024];
        while(file.good())
        {
            // Read data
            file.read(buf, sizeof(buf));
            string data(buf, file.gcount());
            // Process data
            _sha1.update(data);
            // Update status.
            bytes_read += data.length();
            _listener.download_progress(static_cast<int>(1000.0*bytes_read/file_size));
            // Stop if the user cancels.
            if(_listener.download_cancel()) return false;
        }
        // Where there any read errors?
        if(file.fail() && !file.eof()) {
            LOG2FILE(TSTR("Read error."));
            return true;
        }
        // Check the generated hash
        if(_sha1.hex() != _file.hashes[TSTR("sha1")]) {
            LOG2FILE(TSTR("SHA-1 check failed!"));
            return true;
        }
        else {
            LOG2FILE(TSTR("SHA-1 check successful."));
        }
    }
    else {
        LOG2FILE(TSTR("No SHA-1 hash available."));
    }
    _listener.download_progress(static_cast<int>(1000));
    return false; // Succeeded!
}

// Called when data is received from libcurl. If true is returned the transfer is cancelled.
bool CurlDownloader::curl_write(std::string data)
{
    _outfile << data;
    _downloaded += data.length();
    _check_piece(data);
    return _listener.download_cancel() || _state == STATE_PIECE_FAILED;
}

string represent_size(double size)
{
    string sizeunit = "bytes";
    if(size >= 1024.0) {
        sizeunit = "KiB";
        size /= 1024.0;
    }
    if(size >= 1024.0) {
        sizeunit = "MiB";
        size /= 1024.0;
    }
    if(size >= 1024.0) {
        sizeunit = "GiB";
        size /= 1024.0;
    }
    string size_format = "%1$.1f %2%";
    if(sizeunit == "bytes") {
        size_format = "%1$.0f %2%";
    }
    else if(size < 10.0) {
        size_format = "%1$.2f %2%";
    }
    boost::format sizestr(size_format);
    sizestr % size % sizeunit;
    return sizestr.str();
}

string represent_speed(double speed)
{
    return represent_size(speed) + "/s";
}

// Called when progress info is received from libcurl. If true is returned the transfer is cancelled.
bool CurlDownloader::curl_progress(double dltotal, double dlnow)
{
    // Update file size.
    if(_file.size == 0 && dltotal > 0) {
        _file.size = static_cast<boost::uint64_t>(_start_size + dltotal);
    }
    // Calculate download speed
    ptime time_now = ptime(microsec_clock::local_time());
    time_duration td = time_now - _last_progress;
    double downloaded = dlnow - _last_downloaded;
    // Time to update speed calculation?
    if(td.total_milliseconds() > 1000) {
        // Update the current sums.
        _speed_downloaded += downloaded;
        _speed_time += td.total_milliseconds();
        // Store these values, so we can subtract them later.
        _speed_old_downloaded.push_back(downloaded);
        _speed_old_time.push_back(static_cast<double>(td.total_milliseconds()));
        // Time to subtract some old values?
        if(_speed_time - _speed_old_time.front() > 20000.0) { //  20 seconds.
            _speed_time -= _speed_old_time.front();
            _speed_downloaded -= _speed_old_downloaded.front();
            _speed_old_time.pop_front();
            _speed_old_downloaded.pop_front();
        }
        // Calculate speed.
        _speed = _speed_downloaded*1000.0/_speed_time;
        // Save this progress.
        _last_progress = time_now;
        _last_downloaded = dlnow;
    }
    // Calculate ETA
    tstring remaining;
    if(_file.size > 0 && _speed > 0 && _speed_time > 5000.0) { // Only if 5 secs of speed data is available.
        double secs_remaining = (_file.size - _start_size - dlnow) / _speed;
        double hours = floor(secs_remaining/3600.0);
        secs_remaining -= hours*3600;
        double mins = floor(secs_remaining/60.0);
        secs_remaining -= mins*60;
        double secs = floor(secs_remaining);
        if(hours > 0) {
            boost::format fmt(" (%d:%02d:%02d remaining)");
            fmt % hours % mins % secs;
            remaining = s2t(fmt.str());
        }
        else {
            boost::format fmt(" (%d:%02d remaining)");
            fmt % mins % secs;
            remaining = s2t(fmt.str());
        }
    }
    // Format status message
    double progress = 0;
    if(_file.size > 0) progress = (_start_size + dlnow)/_file.size;
    stringstream ss;
    ss << represent_size(_start_size + dlnow);
    ss << boost::format(" (%.0f%%)") % (100.0*progress);
    ss << " of " << represent_size(static_cast<double>(_file.size));
    ss << " @ "<< represent_speed(_speed);
    ss << t2s(remaining);
    // Send status and progress to _listener
    _listener.download_status(s2t(ss.str()));
    _listener.download_progress(static_cast<int>(1000*progress));
    return _listener.download_cancel();
}

}
