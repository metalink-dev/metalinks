#include "custom.h"
#include "util/tstr.h"
#include <string>

using namespace std;
using namespace tstr;

namespace custom {

// The url to download (probably a metalink).
tstr::tstring get_url()
{
    // 256 chars long
    char text[] = "#URL#                                                                                                                                                                                                                                                          #";
    return s2t(text);
    //return TSTR("http://www.metalinker.org/samples/OOo/OOo_2.4.1_Win32Intel_install_wJRE_en-US.exe.metalink");
}

// The filename of the file.
tstr::tstring get_filename()
{
    // 100 chars long
    char text[] = "#FILENAME#                                                                                         #";
    return s2t(text);
    //return TSTR("OOo_2.4.1_Win32Intel_install_wJRE_en-US.exe.metalink");
}

// Welcome msg, to show when the app is started
tstr::tstring get_welcome_msg()
{
    // 100 chars long
    char text[] = "#WELCOME#                                                                                          #";
    return s2t(text);
    //return TSTR("Ready to download OpenOffice.org installer!");
}

// The title of the window.
tstr::tstring get_title()
{
    // 100 chars long
    char text[] = "#TITLE#                                                                                            #";
    return TSTR("Metalink Downloader - ") + s2t(text);
    //return TSTR("Metalink Downloader - OpenOffice.org 2.4.1");
}

// Should the file be launched, after the download has finished?
bool get_launch()
{
    // 8 chars long
    char text[] = "#LAUNCH#";
    if(string(text) == "YES") {
        return true;
    } else {
        return false;
    }
}

// Launch button msg.
tstr::tstring get_launch_button_msg()
{
    // 25 chars long
    char text[] = "#LAUNCHBTN#             #";
    return s2t(text);
    //return TSTR("Launch installer");
}

}
