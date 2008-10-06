#ifndef LOG_H
#define LOG_H

#include "util/tstr.h"
#include <string>
#include <fstream>

#ifdef ENABLE_LOGGING
#define LOG2FILE(msg) logger::write_log_message(__LINE__, __FILE__, msg);
#else
#define LOG2FILE(msg) 
#endif

namespace logger {

/**
  Write a log message to the file "log.txt"
*/
inline void write_log_message(int line, const char* file, tstr::tstring msg)
{
    std::ofstream fout("log.txt", std::ios_base::app | std::ios_base::binary);
    fout << file << ":" << line << " " << tstr::t2s(msg) << std::endl;
    fout.close();
}

}

#endif
