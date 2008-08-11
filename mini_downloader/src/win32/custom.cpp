#include "custom.h"
#include "util/tstr.h"

using namespace tstr;

namespace custom {

// The url to download (probably a metalink).
tstr::tstring get_url()
{
    return TSTR("http://www.metalinker.org/samples/OOo/OOo_2.4.1_Win32Intel_install_wJRE_en-US.exe.metalink");
}

// The filename of the file.
tstr::tstring get_filename()
{
    return TSTR("OOo_2.4.1_Win32Intel_install_wJRE_en-US.exe.metalink");
}

// Welcome msg, to show when the app is started
tstr::tstring get_welcome_msg()
{
    return TSTR("Ready to download OpenOffice.org installer!");
}

// The title of the window.
tstr::tstring get_title()
{
    return TSTR("Metalink Downloader - OpenOffice.org 2.4.0");
}

// Should the file be launched, after the download has finished?
bool get_launch()
{
    return true;
}

// Launch button msg.
tstr::tstring get_launch_button_msg()
{
    return TSTR("Launch installer");
}

}
