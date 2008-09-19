#include "DownloadThread.h"
#include "DownloadThreadListener.h"
#include "CriticalSection.h"
#include "downloader/downloader.h"
#include "metalink/metalink.h"
#include "util/tstr.h"
#include "util/logger.h"
#include "custom.h"
#include <boost/filesystem/operations.hpp>
#include <boost/algorithm/string.hpp>
#include <windows.h>
#include <fstream>

using namespace std;
using namespace tstr;
namespace fs = boost::filesystem;

DownloadThread::DownloadThread()
{
    _listener = 0;
    _state = STATE_READY;
    _country_done = false; // We haven't looked up the country yet.
    init();
}

DownloadThread::~DownloadThread()
{
}

void DownloadThread::set_listener(DownloadThreadListener* listener)
{
    CriticalSection::Lock lock(_cs);
    _listener = listener;
}

void DownloadThread::init()
{
    CriticalSection::Lock lock(_cs);
    if(_state == STATE_READY ||
        _state == STATE_CANCELED ||
        _state == STATE_ERROR)
    {
        _progress = 0;
        _last_event_tick = 0;
        _cancel = false;
        _state = STATE_READY;
    }
}

void DownloadThread::download()
{
    CriticalSection::MultiLock lock(_cs);
    
    lock.enter();
    if(_state != STATE_READY) return;
    _state = STATE_ACTIVE;
    _status = tstring();
    lock.leave();
    
    _lookup_country();
    
    metalink::Metalink ml;
    metalink::MetalinkFile ml_file;
    metalink::MetalinkUrl ml_url;
    ml_url.url = custom::get_url();
    ml_file.filename = custom::get_filename();
    ml_file.urls.push_back(ml_url);
    ml.files.push_back(ml_file);
    int result = downloader::download(*this, ml, _country);
    
    lock.enter();
    if(result == downloader::RESULT_CANCELED) {
        _state = STATE_CANCELED;
    }
    else if(result == downloader::RESULT_ERROR) {
        _state = STATE_ERROR;
    }
    else {
        _state = STATE_FINISHED;
    }
    _cancel = false;
    _send_download_event(true);
    lock.leave();
}

void DownloadThread::cancel()
{
    CriticalSection::Lock lock(_cs);
    _cancel = true;
}

int DownloadThread::get_progress()
{
    CriticalSection::Lock lock(_cs);
    int progress = _progress;
    return progress;
}

tstr::tstring DownloadThread::get_status()
{
    CriticalSection::Lock lock(_cs);
    tstring status(_status.c_str());
    return status;
}

int DownloadThread::get_state()
{
    CriticalSection::Lock lock(_cs);
    int state = _state;
    return state;
}

// Called by the downloader module
bool DownloadThread::download_cancel()
{
    CriticalSection::Lock lock(_cs);
    return _cancel;
}

// Called by the downloader module
void DownloadThread::download_status(tstr::tstring status_msg, bool important)
{
    CriticalSection::Lock lock(_cs);
    _status = status_msg;
    _send_download_event(important);
}

void DownloadThread::download_progress(int progress)
{
    CriticalSection::Lock lock(_cs);
    _progress = progress;
    _send_download_event();
}

void DownloadThread::_send_download_event(bool always_send)
{
    CriticalSection::Lock lock(_cs);
    DWORD this_tick = GetTickCount(); // Note: the time will wrap around to zero if the system is run continuously for 49.7 days.
    if(always_send || this_tick - _last_event_tick > 100 || this_tick < _last_event_tick) {
        _listener->download_event();
        _last_event_tick = this_tick;
    }
}

void DownloadThread::_set_progress(int progress)
{
    CriticalSection::Lock lock(_cs);
    _progress = progress;
}

void DownloadThread::_set_state(int state)
{
    CriticalSection::Lock lock(_cs);
    _state = state;
}

bool DownloadThread::_get_cancel()
{
    CriticalSection::Lock lock(_cs);
    bool cancel = _cancel;
    return cancel;
}

void DownloadThread::_lookup_country()
{
    // Only try to look it up once.
    if(_country_done == false) {
        // Don't do this more than once!
        _country_done = true;
        // Download country code
        metalink::Metalink ml;
        metalink::MetalinkFile ml_file;
        metalink::MetalinkUrl ml_url;
        ml_url.url = TSTR("http://hampus.vox.nu/country.php");
        ml_file.filename = TSTR(".country.tmp");
        ml_file.urls.push_back(ml_url);
        ml.files.push_back(ml_file);
        int result = downloader::download(*this, ml);
        // Read country code (on success).
        if(result == downloader::RESULT_OK) {
            ifstream file(TSTR(".country.tmp"), ios_base::in | ios_base::binary);
            char buf[1024];
            while(file.good())
            {
                // Read data
                file.read(buf, sizeof(buf));
                string data(buf, file.gcount());
                // Add data to the _country
                boost::to_lower(data);
                _country += s2t(data);
            }
            // Where there any read errors?
            if(file.fail() && !file.eof()) {
                LOG2FILE(TSTR("Read error, while reading '.country.tmp'."));
                _country = TSTR("");
            }
            LOG2FILE(TSTR("Country = '") + _country + TSTR("'"));
        }
        else {
            LOG2FILE(TSTR("Failed to retrieve country code."));
        }
        // Delete country file
        try {
            fs::remove(fs::path(".country.tmp"));
        }
        catch(fs::basic_filesystem_error<fs::path>) {
            LOG2FILE(TSTR("Failed to remove '.country.tmp'"));
        }
    }
}
