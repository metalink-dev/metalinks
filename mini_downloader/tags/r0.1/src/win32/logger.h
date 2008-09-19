#ifndef WIN32LOG_H
#define WIN32LOG_H

#include "util/tstr.h"
#include <string>
#include <fstream>

#ifdef ENABLE_LOGGING
#define LOGWIN32(msg) logger::write_log_message_win32(__LINE__, __FILE__, msg);
#else
#define LOGWIN32(msg) 
#endif

namespace logger {

inline void write_log_message_win32(int line, const char* file, tstr::tstring msg)
{
    std::ofstream fout("log_gui.txt", std::ios_base::app | std::ios_base::binary);
    fout << file << ":" << line << " " << tstr::t2s(msg) << std::endl;
    fout.close();
}

}

#endif
