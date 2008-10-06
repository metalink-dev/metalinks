/** \mainpage Metalink mini downloader

  The mini downloader is a small metalink downloader.
  
  This metalink downloader has been created with the
  error-robustness in mind. The downloader does not
  use multiple connections to increase speed. Instead
  it focussus on increasing availablility to the user
  by automatically switching servers when needed and
  verifying data integrity.
  
  By keeping the downloader small, it can be sent to the
  user as a small download utility for every download.
  This will allow the user to benefit from a more secure
  and fail-proof download without having to install
  any special application.

  The documentation you are currently reading is meant for
  developers and does not contain information on the
  general use of the application. Please refer to http://metalinks.sf.net
  for more information.
  
  The windows frontend starts at: WinMain()
  
  There is currently no Linux version.
*/


#include "resources.h"
#include "Controller.h"
#include "downloader/downloader.h"
#include "metalink/metalink.h"
#include "util/tstr.h"
#include "logger.h"
#include "custom.h"

#include <windows.h>
#include <commctrl.h>
#include <fstream>
#include <string>
#include <sstream>
#include <exception>

using namespace std;
using namespace tstr;

const TCHAR g_szClassName[] = TEXT("myWindowClass");
const INT ID_BUTTON = 201;

LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    try {
        Controller* controller = reinterpret_cast<Controller*>(GetWindowLong(hwnd, GWLP_USERDATA));
        switch(msg)
        {
            case WM_CLOSE:
                controller->close_window();
            break;
            case WM_DESTROY:
                PostQuitMessage(0);
            break;
            case WM_COMMAND:
                if(LOWORD(wParam) == ID_BUTTON && HIWORD(wParam) == BN_CLICKED) {
                    controller->button_pressed();
                }
            case WM_DL_EVENT:
                controller->download_update();
            break;
            default:
                return DefWindowProc(hwnd, msg, wParam, lParam);
        }
    }
    catch(exception& e)
    {
        LOGWIN32(TSTR("Exception: ")+tstr::s2t(e.what()));
        MessageBox(NULL, tstr::s2t(e.what()).c_str(), TEXT("Error!"), MB_ICONEXCLAMATION | MB_OK);
    }
    return 0;
}

///The root of all... good stuff.
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance,
    LPSTR lpCmdLine, int nCmdShow)
{
    WNDCLASSEX wc;
    HWND hwnd;
    MSG Msg;
    LOGWIN32(TSTR("WinMain()"));
    
    try {
        // Should be done before we create any new threads.
        downloader::init();
        
        // Register a window class
        wc.cbSize        = sizeof(WNDCLASSEX);
        wc.style         = 0; //CS_DROPSHADOW;
        wc.lpfnWndProc   = WndProc;
        wc.cbClsExtra    = 0;
        wc.cbWndExtra    = 0;
        wc.hInstance     = hInstance;
        wc.hIcon         = LoadIcon(hInstance, MAKEINTRESOURCE(ID_OOICON));
        wc.hCursor       = LoadCursor(NULL, IDC_ARROW);
        wc.hbrBackground = (HBRUSH)(COLOR_BTNFACE+1);
        wc.lpszMenuName  = NULL;
        wc.lpszClassName = g_szClassName;
        wc.hIconSm       = LoadIcon(hInstance, MAKEINTRESOURCE(ID_OOICON));

        if(!RegisterClassEx(&wc))
        {
            MessageBox(NULL, TEXT("Window Registration Failed!"), TEXT("Error!"),
                MB_ICONEXCLAMATION | MB_OK);
            return 0;
        }

        // Create a window
        hwnd = CreateWindowEx(
            WS_EX_STATICEDGE,
            g_szClassName,
            custom::get_title().c_str(),
            WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
            CW_USEDEFAULT, CW_USEDEFAULT, 450, 135,
            NULL, NULL, hInstance, NULL);
        if(hwnd == NULL)
        {
            MessageBox(NULL, TEXT("Window Creation Failed!"), TEXT("Error!"),
                MB_ICONEXCLAMATION | MB_OK);
            return 0;
        }
        
        // Init common controls
        INITCOMMONCONTROLSEX ctrls;
        ctrls.dwSize = sizeof(ctrls);
        ctrls.dwICC = ICC_PROGRESS_CLASS;
        if(InitCommonControlsEx(&ctrls) != TRUE)
        {
            MessageBox(NULL, TEXT("InitCommonControlsEx failed!"), TEXT("Error!"),
                MB_ICONEXCLAMATION | MB_OK);
            return 0;
        }

        // Create progress bar 
        HWND hwnd_progress = CreateWindowEx(
            0,
            PROGRESS_CLASS,
            (LPTSTR) NULL, WS_CHILD | WS_VISIBLE,
            10, 40, 424, 15,
            hwnd, (HMENU) 0, hInstance, NULL);
        if(hwnd_progress == NULL)
        {
            MessageBox(NULL, TEXT("Progress bar creation failed!"), TEXT("Error!"),
                MB_ICONEXCLAMATION | MB_OK);
            return 0;
        }

        // Create button
        HWND hwnd_btn = CreateWindowEx(
            0,
            TEXT("BUTTON"),   // Predefined class; Unicode assumed. 
            TEXT("Start download"),       // Button text. 
            WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
            150, 65, 144, 25,
            hwnd, (HMENU)ID_BUTTON, hInstance, NULL);
        if(hwnd_btn == NULL)
        {
            MessageBox(NULL, TEXT("Button creation failed!"), TEXT("Error!"),
                MB_ICONEXCLAMATION | MB_OK);
            return 0;
        }
        
        // Create static
        HWND hwnd_status = CreateWindowEx(
            0,
            TEXT("STATIC"),
            custom::get_welcome_msg().c_str(),
            WS_VISIBLE | WS_CHILD | SS_CENTER | SS_WORDELLIPSIS,
            10, 15, 424, 25,
            hwnd, (HMENU) 0, hInstance, NULL);
        if(hwnd_status == NULL)
        {
            MessageBox(NULL, TEXT("Static creation failed!"), TEXT("Error!"),
                MB_ICONEXCLAMATION | MB_OK);
            return 0;
        }
        HFONT font = CreateFont(
          0, // height of font
          0, // average character width
          0, // angle of escapement
          0, // base-line orientation angle
          0, // font weight
          0, // italic attribute option
          0, // underline attribute option
          0, // strikeout attribute option
          0, // character set identifier
          0, // output precision
          0, // clipping precision
          0, // output quality
          0, // pitch and family
          0 //TEXT("Verdana") // typeface name
        );
        SendMessage(hwnd_status, WM_SETFONT, (WPARAM)font, (LPARAM)TRUE);

        
        // Set up application
        Controller controller(hwnd, hwnd_btn, hwnd_progress, hwnd_status);
        SetLastError(0);
        SetWindowLongPtr(hwnd, GWLP_USERDATA, reinterpret_cast<LONG_PTR>(&controller));
        if(GetLastError() != 0)
        {
            MessageBox(NULL, TEXT("SetWindowLongPtr failed!"), TEXT("Error!"),
                MB_ICONEXCLAMATION | MB_OK);
            return 0;
        }
        
        // Show window
        ShowWindow(hwnd, SW_SHOWDEFAULT);
        UpdateWindow(hwnd);

        // Enter message loop
        while(GetMessage(&Msg, NULL, 0, 0) > 0)
        {
            TranslateMessage(&Msg);
            DispatchMessage(&Msg);
        }
    }
    catch(exception& e)
    {
        LOGWIN32(TSTR("Exception: ")+tstr::s2t(e.what()));
        MessageBox(NULL, tstr::s2t(e.what()).c_str(), TEXT("Error!"), MB_ICONEXCLAMATION | MB_OK);
    }
    LOGWIN32(TSTR("leaving WinMain()"));
    return Msg.wParam;
}
