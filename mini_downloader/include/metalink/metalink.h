#ifndef METALINK_H
#define METALINK_H

#include <boost/cstdint.hpp>
#include <exception>
#include <string>
#include <vector>
#include <map>

namespace metalink {

#ifdef UNICODE
    typedef std::wstring MetalinkStr;
#else
    typedef std::string MetalinkStr;
#endif

struct MetalinkUrl
{
    MetalinkUrl() : preference(-1) { }
    MetalinkStr url;
    MetalinkStr location;
    int preference;
};

struct MetalinkFile
{
    MetalinkFile() : size(0), piece_length(0) { }
    MetalinkStr filename;
    boost::uint64_t size;
    std::vector<MetalinkUrl> urls;
    // Hashes
    std::map<MetalinkStr, MetalinkStr> hashes; // key = type, value = hash
    MetalinkStr piece_type;
    unsigned int piece_length;
    std::vector<MetalinkStr> piece_hashes;
};

struct Metalink
{
    std::vector<MetalinkFile> files;
};

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

// Functions for parsing metalink files
Metalink load_file(std::string filename);

} // namespace metalink

#endif
