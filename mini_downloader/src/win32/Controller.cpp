#include "Controller.h"
#include "DownloadThread.h"
#include "util/tstr.h"
#include "logger.h"
#include "custom.h"
#include <windows.h>
#include <windowsx.h>
#include <commctrl.h>
#include <process.h>
#include <fstream>
#include <exception>

using namespace tstr;

void start_download(void* download_thread)
{
    try {
        DownloadThread* dt = static_cast<DownloadThread*>(download_thread);
        dt->download();
    }
    catch(std::exception& e)
    {
        LOGWIN32(TSTR("Exception: ")+tstr::s2t(e.what()));
    }
}

void launch_installer()
{
    LOGWIN32(TSTR("launch_installer()"));
    STARTUPINFO si;
    PROCESS_INFORMATION pi;
    
    LOGWIN32(TSTR("ZeroMemory()"));
    ZeroMemory( &si, sizeof(si) );
    si.cb = sizeof(si);
    ZeroMemory( &pi, sizeof(pi) );

    tstring filename = TSTR("OOo_2.4.1_Win32Intel_install_wJRE_en-US.exe");
    
    // Start the child process. 
    if( !CreateProcess(filename.c_str(),   // No module name (use command line)
        NULL,           // Command line
        NULL,           // Process handle not inheritable
        NULL,           // Thread handle not inheritable
        FALSE,          // Set handle inheritance to FALSE
        0,              // No creation flags
        NULL,           // Use parent's environment block
        NULL,           // Use parent's starting directory 
        &si,            // Pointer to STARTUPINFO structure
        &pi )           // Pointer to PROCESS_INFORMATION structure
    ) 
    {
        MessageBox(NULL, TEXT("Failed to start the installer. You'll have to do so manually."), TEXT("Error!"), MB_ICONEXCLAMATION | MB_OK);
        return;
    }
    
    // Close process and thread handles. 
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
}

Controller::Controller(HWND hwnd, HWND hwnd_btn, HWND hwnd_progress, HWND hwnd_status)
    : _hwnd(hwnd), _button(hwnd_btn), _progress(hwnd_progress), _status(hwnd_status)
{
    LOGWIN32(TSTR("Controller::Controller()"));
    SendMessage(_progress, PBM_SETRANGE, 0, MAKELPARAM (0, 30000));
    _set_progress(0);
    _close = false;
    _state = STATE_READY;
    _dt.set_listener(this);
}

Controller::~Controller()
{
    LOGWIN32(TSTR("Controller::~Controller()"));
}

void Controller::button_pressed()
{
    LOGWIN32(TSTR("Controller::button_pressed()"));
    switch(_state)
    {
        case STATE_READY:
        case STATE_CANCELED:
        case STATE_FAILED:
            // Start download
            _dt.init();
            _beginthread(start_download, 0, &_dt);
            // Update state
            _state = STATE_ACTIVE;
        break;
        case STATE_ACTIVE:
            // Tell download thread to cancel as soon as possible
            _dt.cancel();
            // Update state
            _state = STATE_CANCELING;
        break;
        case STATE_FINISHED:
            // Launch the installer!
            if(custom::get_launch()) {
                launch_installer();
            }
            // Close the downloader
            DestroyWindow(_hwnd);
        break;
    }
    _update_gui();
}

void Controller::download_event()
{
    LOGWIN32(TSTR("Controller::download_event()"));
    PostMessage(_hwnd, WM_DL_EVENT, 0, 0);
}

void Controller::download_update()
{
    LOGWIN32(TSTR("Controller::download_update()"));
    if(_state == STATE_ACTIVE || _state == STATE_CANCELING) {
        // Update state
        if(_dt.get_state() == DownloadThread::STATE_FINISHED) {
            _state = STATE_FINISHED;
        }
        else if(_dt.get_state() == DownloadThread::STATE_CANCELED) {
            _state = STATE_CANCELED;
        }
        else if(_dt.get_state() == DownloadThread::STATE_ERROR) {
            _state = STATE_FAILED;
        }
        // Are we going to quit?
        if(_close && _dt.get_state() != DownloadThread::STATE_ACTIVE) {
            DestroyWindow(_hwnd);
        }
    }
    _update_gui();
}

void Controller::_update_gui()
{
    int progress;
    switch (_state)
    {
        case STATE_READY:
            _set_status_text(custom::get_welcome_msg().c_str());
            _set_button_text(TEXT("Start download"));
            Button_Enable(_button, true);
            _set_progress(0);
        break;
        case STATE_ACTIVE:
            _set_status_text(_dt.get_status().c_str());
            _set_button_text(TEXT("Cancel"));
            progress = _dt.get_progress();
            _set_progress(static_cast<float>(progress) / 1000.0f);
        break;
        case STATE_CANCELING:
            _set_status_text(TEXT("Cancelling download..."));
            Button_Enable(_button, false);
        break;
        case STATE_CANCELED:
            _set_status_text(TEXT("Download canceled."));
            _set_button_text(TEXT("Start download"));
            Button_Enable(_button, true);
            _set_progress(0);
        break;
        case STATE_FINISHED:
            _set_status_text(TEXT("Download finished!"));
            if(custom::get_launch()) {
                _set_button_text(custom::get_launch_button_msg().c_str());
            }
            else {
                _set_button_text(TEXT("Close"));
            }
            Button_Enable(_button, true);
            _set_progress(1.0f);
        break;
        case STATE_FAILED:
            _set_status_text(TEXT("Download failed..."));
            _set_button_text(TEXT("Start download"));
            Button_Enable(_button, true);
            _set_progress(0);
        break;
    }
}

void Controller::close_window()
{
    LOGWIN32(TSTR("Controller::close_window()"));
    if(_state != STATE_ACTIVE && _state != STATE_CANCELING) {
        DestroyWindow(_hwnd);
    }
    if(_state == STATE_ACTIVE) {
        button_pressed();
    }
    _close = true;
}

void Controller::_set_status_text(LPCTSTR text)
{
    SetWindowText(_status, text);
}

void Controller::_set_button_text(LPCTSTR text)
{
    LOGWIN32(TSTR("Controller::_set_button_text()"));
    SetWindowText(_button, text);
}

void Controller::_set_progress(float progress)
{
    SendMessage(_progress, PBM_SETPOS, static_cast<WPARAM>(30000*progress), 0);
}
