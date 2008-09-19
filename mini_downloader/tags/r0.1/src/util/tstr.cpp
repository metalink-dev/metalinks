#include "util/tstr.h"
#include <string>
#include <cstdlib>

using namespace std;

namespace tstr {

class CharBuffer
{
public:
    CharBuffer(int length)
    {
        _buf = new char[length];
        _length = length;
    }
    ~CharBuffer()
    {
        delete[] _buf;
    }
    char* get_buffer() { return _buf; }
    int get_length() { return _length; }
private:
    char* _buf;
    int _length;
};

std::wstring s2ws(std::string str_from)
{
    wstring result;
    wchar_t wbuf;
    while(str_from.length() > 0)
    {
        int num = mbtowc(&wbuf, str_from.c_str(), str_from.length());
        if(num == -1) {
            result += L"?";
        } else {
            result.push_back(wbuf);
        }
        str_from.erase(0, 1);
    }
    return result;
}

std::string ws2s(std::wstring str_from)
{
    string result;
    CharBuffer buf(MB_CUR_MAX);
    int num;
    for(size_t i = 0; i < str_from.length(); i++)
    {
#ifdef _MSC_VER
        wctomb_s(&num, buf.get_buffer(), buf.get_length(), str_from.at(i));
#else
        num = wctomb(buf.get_buffer(), str_from.at(i));
#endif
        if(num == -1) {
            result += "?";
        } else {
            result.append(buf.get_buffer(), num);
        }
    }
    return result;
}

tstring ws2t(std::wstring str_from)
{
#ifdef UNICODE
    return str_from;
#else
    return ws2s(str_from);
#endif
}

tstring s2t(std::string str_from)
{
#ifdef UNICODE
    return s2ws(str_from);
#else
    return str_from;
#endif
}

std::wstring t2ws(tstring str_from)
{
#ifdef UNICODE
    return str_from;
#else
    return s2ws(str_from);
#endif
}

std::string t2s(tstring str_from)
{
#ifdef UNICODE
    return ws2s(str_from);
#else
    return str_from;
#endif
}

tchar c2t(char c)
{
#ifdef UNICODE
    wchar_t wbuf;
    int num = mbtowc(&wbuf, &c, 1);
    if(num == -1) return '?'; // Error!
    return wbuf;
#else
    return c;
#endif
}

void trim(tstring& str)
{
    tstring::size_type pos = str.find_last_not_of(TSTR(' '));
    if(pos != tstring::npos) {
        str.erase(pos + 1);
        pos = str.find_first_not_of(TSTR(' '));
        if(pos != tstring::npos) str.erase(0, pos);
    }
    else {
        str.erase(str.begin(), str.end());
    }
}

tstr::tstring char2hex(const unsigned char num)
{
  tstring symbols = TSTR("0123456789abcdef");
  tstring strHex;
  strHex = symbols.at(num&15);
  char num2 = num >> 4;
  strHex = symbols.at(num2) + strHex;
  return strHex;
}

tstring string2hex(const std::string& str)
{
  tstring strHex;
  unsigned int i;
  for (i = 0; i < str.length(); i++) {
    strHex += char2hex(str.at(i));
  }
  return strHex;
}

tstring data2hex(const unsigned char* data, unsigned int length)
{
  tstring strHex;
  unsigned int i;
  for (i = 0; i < length; i++) {
    strHex += char2hex(data[i]);
  }
  return strHex;
}

}
