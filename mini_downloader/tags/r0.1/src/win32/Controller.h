#ifndef WIN32CONTROLLER_H
#define WIN32CONTROLLER_H

#include "DownloadThread.h"
#include "DownloadThreadListener.h"
#include <windows.h>

#define WM_DL_EVENT (WM_USER+1)

class Controller : public DownloadThreadListener
{
public:
    Controller(HWND hwnd, HWND hwnd_btn, HWND hwnd_progress, HWND hwnd_status);
    virtual ~Controller();
    void button_pressed();
    void download_update();
    void close_window();
    virtual void download_event(); // Called from the download thread
private:
    void _set_status_text(LPCTSTR text);
    void _set_button_text(LPCTSTR text);
    void _set_progress(float progress);
    void _update_gui();
    HWND _hwnd;
    HWND _button;
    HWND _progress;
    HWND _status;
    DownloadThread _dt;
    bool _close;
    int _state;
    enum {
    STATE_READY,
    STATE_ACTIVE,
    STATE_CANCELING,
    STATE_FINISHED,
    STATE_CANCELED,
    STATE_FAILED
    };
};

#endif
