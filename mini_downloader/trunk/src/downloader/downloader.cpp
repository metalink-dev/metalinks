#include "downloader/downloader.h"
#include "CurlDownloader.h"
#include "metalink/metalink.h"
#include "util/tstr.h"
#include "util/logger.h"
#include <curl/curl.h>
#include <string>
#include <sstream>
#include <fstream>

using namespace std;

namespace downloader {

//  Used by the THROW_DOWNLOADER_EX macro, see downloader.h.
std::string format_exception_msg(char* file, int line, std::string msg)
{
    stringstream ss;
    ss << file << ":" << line << " " << msg;
    return ss.str();
}

// Used to init libcurl and then clean it up on exit.
class CurlInitializer
{
public:
    CurlInitializer()
    {
        LOG2FILE(TSTR("CurlInitializer::CurlInitializer()"));
        if(curl_global_init(CURL_GLOBAL_ALL) != 0)
            THROW_DOWNLOADER_EX("curl_global_init() failed!");
    }
    
    ~CurlInitializer()
    {
        LOG2FILE(TSTR("CurlInitializer::~CurlInitializer()"));
        curl_global_cleanup();
    }
};

// Init the downloader (ie libcurl). Can be called any number of times. There's no clean up function...
void init()
{
    LOG2FILE(TSTR("init()"));
    // This creates a static object, which initializes libcurl. It will be deleted automatically when the process exits.
    static CurlInitializer initializer;
}

// Download the files described by the metalink.
int download(DownloadListener& listener, metalink::Metalink source, tstr::tstring country)
{
    LOG2FILE(TSTR("download()"));
    init();
    listener.download_status(TSTR("Initializing download..."));
    listener.download_progress(0);
    CurlDownloader dl(listener);
    dl.set_country(country);
    dl.add_metalink(source);
    int result = dl.download();
    return result;
}

}
