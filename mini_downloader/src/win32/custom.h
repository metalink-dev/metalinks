#ifndef TEXT_H
#define TEXT_H

#include "util/tstr.h"

namespace custom {

// The url to download (probably a metalink).
tstr::tstring get_url();
// The filename of the file.
tstr::tstring get_filename();
// Welcome msg, to show when the app is started
tstr::tstring get_welcome_msg();
// The title of the window.
tstr::tstring get_title();
// Should the file be launched, after the download has finished?
bool get_launch();
// Launch button msg.
tstr::tstring get_launch_button_msg();

}

#endif
