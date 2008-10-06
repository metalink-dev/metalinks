#ifndef TSTR_H
#define TSTR_H

#include <string>
#include <sstream>

namespace tstr {

#ifdef UNICODE
#   define TSTR(s) L##s
    typedef wchar_t tchar;
    typedef std::wstring tstring;
#else
#   define TSTR(s) s
    typedef char tchar;
    typedef std::string tstring;
#endif
///String to wide string (UNICODE)
std::wstring s2ws(std::string str_from);

std::string ws2s(std::wstring str_from);
tstring ws2t(std::wstring str_from);
tstring s2t(std::string str_from);
std::wstring t2ws(tstring str_from);
std::string t2s(tstring str_from);
tchar c2t(char c);

void trim(tstring& str);

tstring char2hex(const unsigned char num);
tstring string2hex(const std::string& str);
tstring data2hex(const unsigned char* data, unsigned int length);

template <class T>
tstring num2str(T num)
{
    std::stringstream ss;
    ss << num;
    return s2t(ss.str());
}

}

#endif
