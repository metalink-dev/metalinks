#ifndef DOWNLOADTHREAD_H
#define DOWNLOADTHREAD_H

#include "DownloadThreadListener.h"
#include "CriticalSection.h"
#include "downloader/DownloadListener.h"
#include "util/tstr.h"
#include <windows.h>

class DownloadThread : public downloader::DownloadListener
{
public:
    DownloadThread();
    virtual ~DownloadThread();
    void set_listener(DownloadThreadListener* listener);
    void init();
    void download();
    void cancel();
    int get_progress();
    tstr::tstring get_status();
    int get_state();
    virtual bool download_cancel(); // From DownloadListener
    virtual void download_status(tstr::tstring status_msg, bool important); // From DownloadListener
    virtual void download_progress(int progress); // From DownloadListener
    enum {
    STATE_READY,
    STATE_ACTIVE,
    STATE_FINISHED,
    STATE_CANCELED,
    STATE_ERROR
    };
private:
    void _send_download_event(bool always_send = false);
    void _set_progress(int progress);
    void _set_state(int state);
    bool _get_cancel();
    void _lookup_country();
    CriticalSection _cs;
    DownloadThreadListener* _listener;
    tstr::tstring _country;
    bool _country_done;
    int _progress;
    tstr::tstring _status;
    DWORD _last_event_tick;
    bool _cancel;
    int _state;
};

#endif
