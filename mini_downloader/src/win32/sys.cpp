#include "util/sys.h"
#include "util/tstr.h"
#include "util/logger.h"
#include <boost/cstdint.hpp>
#include <windows.h>

namespace sys {

std::string last_error()
{
    LPVOID buf;
    std::string error;
    if (FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
        NULL,
        GetLastError(),
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
        (LPTSTR) &buf,
        0,
        NULL))
    {
        error = static_cast<char*>(buf);
        LocalFree(buf);
    }
    else {
        error = "Unkown error";
    }
    return error;
}


void truncate_file(tstr::tstring filename, boost::uint64_t size)
{
    BOOL result;
    // Open file
    HANDLE file = CreateFile(filename.c_str(), GENERIC_WRITE, 0, 0, OPEN_EXISTING, 0, 0);
    if(file == INVALID_HANDLE_VALUE) {
        LOG2FILE(TSTR("CreateFile() failed!"));
        LOG2FILE(tstr::s2t(last_error()));
        return;
    }
    // Truncate file
    LARGE_INTEGER pos;
    pos.QuadPart = size;
    result = SetFilePointerEx(file, pos, 0, FILE_BEGIN);
    if(result == 0) {
        LOG2FILE(TSTR("SetFilePointerEx() failed!"));
        LOG2FILE(tstr::s2t(last_error()));
        return;
    }
    result = SetEndOfFile(file);
    if(result == 0) {
        LOG2FILE(TSTR("SetEndOfFile() failed!"));
        LOG2FILE(tstr::s2t(last_error()));
        return;
    }
    // Close file
    result = CloseHandle(file);
    if(result == 0) {
        LOG2FILE(TSTR("CloseHandle() failed!"));
        LOG2FILE(tstr::s2t(last_error()));
        return;
    }
}

}
