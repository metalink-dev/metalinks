#ifndef DOWNLOADLISTENER_H
#define DOWNLOADLISTENER_H

#include "util/tstr.h"

namespace downloader {

class DownloadListener
{
public:
    virtual bool download_cancel()=0;
    virtual void download_status(tstr::tstring status_msg, bool important=false)=0;
    virtual void download_progress(int progress)=0;
};

}

#endif
