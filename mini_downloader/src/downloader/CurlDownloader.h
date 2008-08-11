#ifndef CURLDOWNLOADER_H
#define CURLDOWNLOADER_H

#include "downloader/DownloadListener.h"
#include "metalink/metalink.h"
#include "util/sha1.h"
#include "util/tstr.h"
#include <curl/curl.h>
#include <boost/cstdint.hpp>
#include <boost/random.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <fstream>
#include <list>

namespace downloader {

struct Mirror
{
    Mirror(metalink::MetalinkUrl ml_url) :
        url(ml_url.url), location(ml_url.location),
        preference(ml_url.preference), errors(0) {}
    Mirror() : preference(-1), errors(0) {}
    tstr::tstring url;
    tstr::tstring location;
    int preference;
    int errors;
};

class CurlDownloader
{
public:
    CurlDownloader(DownloadListener& listener);
    ~CurlDownloader();
    void add_metalink(metalink::Metalink ml);
    int download();
    void set_country(tstr::tstring country);
    bool curl_write(std::string data);
    bool curl_progress(double dltotal, double dlnow);
private:
    void _prepare_download(metalink::MetalinkFile file);
    void _download_file();
    void _choose_mirror();
    void _curl_download();
    void _check_pieces();
    void _check_piece(std::string data);
    bool _check_hash();
    DownloadListener& _listener; // A listener object, which we send the current status to and ask whether to cancel.
    metalink::Metalink _ml; // Contains all remaining files to be downloaded.
    metalink::MetalinkFile _file; // The file being downloaded for the moment.
    std::list<Mirror> _mirrors; // The mirrors where the current file can be found.
    Mirror _mirror; // Current mirror to download from.
    CURL* _curl; // Curl easy handle. Can be used for several transfers.
    boost::mt19937 _rng; // Random number generator.
    std::ofstream _outfile;
    boost::posix_time::ptime _last_progress; // The last time we measured the download speed.
    double _last_downloaded; // The amount we had downloaded at _last_progress.
    double _speed_downloaded; // Used to calculate the current speed
    double _speed_time; // Used to calculate the current speed
    std::list<double> _speed_old_downloaded; // Used to update _speed_downloaded.
    std::list<double> _speed_old_time; // Used to update _speed_time.
    double _speed; // Current speed
    double _start_size; // When starting a download, this is the initial amount downloaded.
    double _downloaded; // The number of bytes downloaded, since the download was started (_start_size + _downloaded = total downloaded).
    double _bytes_verified; // Total number of bytes verified.
    double _sha1_bytes; // The number of bytes hashed in the current piece.
    SHA1Gen _sha1; // The hash generator used to generate piece hashes.
    tstr::tstring _country;
    int _state;
    enum {
    STATE_READY,
    STATE_DOWNLOADING,
    STATE_FILE_DONE,
    STATE_FILE_FAILED,
    STATE_CANCELED,
    STATE_PIECE_FAILED
    };
};

}

#endif
