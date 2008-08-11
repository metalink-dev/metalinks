#include "custom.h"
#include "util/tstr.h"
#include <string>

/*
This file let you customize a few text strings, which are used in the downloader. If CUSTOM_STRINGS are defined it will
create c-style strings, which can easily be modified after the file has been compiled by searching for and replace them.
*/

using namespace std;
using namespace tstr;

namespace custom {

// The url to download (probably a metalink).
tstr::tstring get_url()
{
#ifdef CUSTOM_STRINGS
    // 256 chars long
    char text[] = "#URL#                                                                                                                                                                                                                                                          #";
    return s2t(text);
#else
    return TSTR("http://hampus.vox.nu/mini_downloader/OOo_2.4.1_Win32Intel_install_wJRE_en-US.exe.metalink");
#endif
}

// The filename of the file.
tstr::tstring get_filename()
{
#ifdef CUSTOM_STRINGS
    // 100 chars long
    char text[] = "#FILENAME#                                                                                         #";
    return s2t(text);
#else
    return TSTR("OOo_2.4.1_Win32Intel_install_wJRE_en-US.exe.metalink");
#endif
}

// Welcome msg, to show when the app is started
tstr::tstring get_welcome_msg()
{
#ifdef CUSTOM_STRINGS
    // 100 chars long
    char text[] = "#WELCOME#                                                                                          #";
    return s2t(text);
#else
    return TSTR("Ready to download OpenOffice.org installer!");
#endif
}

// The title of the window.
tstr::tstring get_title()
{
#ifdef CUSTOM_STRINGS
    // 100 chars long
    char text[] = "#TITLE#                                                                                            #";
    return TSTR("Metalink Downloader - ") + s2t(text);
#else
    return TSTR("Metalink Downloader - OpenOffice.org 2.4.1");
#endif
}

// Should the file be launched, after the download has finished?
bool get_launch()
{
#ifdef CUSTOM_STRINGS
    // 8 chars long
    char text[] = "#LAUNCH#";
    if(string(text) == "YES") {
        return true;
    } else {
        return false;
    }
#else
    return true;
#endif
}

// Launch button msg.
tstr::tstring get_launch_button_msg()
{
#ifdef CUSTOM_STRINGS
    // 25 chars long
    char text[] = "#LAUNCHBTN#             #";
    return s2t(text);
#else
    return TSTR("Launch installer");
#endif
}

// The filename of the file to launch
tstr::tstring get_launch_filename()
{
#ifdef CUSTOM_STRINGS
    // 100 chars long
    char text[] = "#LAUNCHFILENAME#                                                                                   #";
    return s2t(text);
#else
    return TSTR("OOo_2.4.1_Win32Intel_install_wJRE_en-US.exe");
#endif
}

}
