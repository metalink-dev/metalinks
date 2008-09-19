#ifndef DOWNLOADER_H
#define DOWNLOADER_H

#include "DownloadListener.h"
#include "metalink/metalink.h"
#include "util/tstr.h"
#include <string>

namespace downloader {

// Inits the downloader. Should be called before more than one thread is created.
void init();

// Downloads the files from "source" to the working directory and returns one of the RESULT_* codes (see below).
int download(DownloadListener& listener, metalink::Metalink source, tstr::tstring country = TSTR(""));

// Return codes.
static const int RESULT_OK = 1;
static const int RESULT_ERROR = 2;
static const int RESULT_CANCELED = 3;

// Exception thrown by the downloader module on errors.
class Exception : public std::exception
{
public:
   explicit Exception(const std::string what) : _what(what) {}
   virtual ~Exception() throw() {}
   virtual const char* what() const throw()
   {
      return _what.c_str();
   }
private:
   const std::string _what;
};

// Some exception utilities (only to be used by the downloader module).
std::string format_exception_msg(char* file, int line, std::string msg);
#define THROW_DOWNLOADER_EX(msg) {throw Exception(format_exception_msg(__FILE__, __LINE__, msg));}

}

#endif
