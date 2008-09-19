#include "metalink/metalink.h"
#include "util/tstr.h"
#include <boost/algorithm/string/trim.hpp>
#include <fstream>
#include <string>
#include <sstream>
#include <map>
#include <cstdlib>

#if defined(UNICODE) && !defined(XML_UNICODE_WCHAR_T)
#define XML_UNICODE_WCHAR_T
#endif
#include <expat.h>

using namespace std;
using namespace tstr;

string get_exception_msg(char* file, int line, string msg)
{
    stringstream ss;
    ss << file << ":" << line << " " << msg;
    return ss.str();
}

#define THROW_EXCEPTION(msg) {throw Exception(get_exception_msg(__FILE__, __LINE__, msg));}

namespace metalink {

// METALINK PARSER

class MetalinkParser
{
public:
    MetalinkParser();
    ~MetalinkParser();
    Metalink get_metalink();
    void start_element(MetalinkStr name, map<MetalinkStr, MetalinkStr> atts);
    void end_element(MetalinkStr name);
    void character_data(MetalinkStr data);
    bool parse(string data);
    bool finished();
private:
    void _failed();
    Metalink _ml;
    MetalinkFile _file;
    MetalinkUrl _url;
    MetalinkStr _type;
    MetalinkStr _content;
    map<int, MetalinkStr> _pieces;
    int _piece_id;
    XML_Parser _parser;
    int _depth;
    int _state;
    enum {
    STATE_READY,
    STATE_DONE,
    STATE_ERROR,
    STATE_METALINK,
    STATE_FILES,
    STATE_FILE,
    STATE_FILE_SIZE,
    STATE_RESOURCES,
    STATE_RESOURCES_URL,
    STATE_VERIFICATION,
    STATE_VERIFICATION_HASH,
    STATE_VERIFICATION_PIECES,
    STATE_VERIFICATION_PIECE
    };
};

void StartElementHandler(void *userData, const XML_Char *name, const XML_Char **atts)
{
    MetalinkParser* parser = static_cast<MetalinkParser*>(userData);
    map<MetalinkStr, MetalinkStr> atts_map;
    const XML_Char** cur_attr = atts;
    while(*cur_attr != 0)
    {
        MetalinkStr attr_name = *cur_attr;
        MetalinkStr attr_value = *(cur_attr+1);
        atts_map[attr_name] = attr_value;
        cur_attr += 2;
    }
    parser->start_element(name, atts_map);
}

void EndElementHandler(void *userData, const XML_Char *name)
{
    MetalinkParser* parser = static_cast<MetalinkParser*>(userData);
    parser->end_element(name);
}

void CharacterDataHandler(void *userData, const XML_Char *s, int len)
{
    MetalinkParser* parser = static_cast<MetalinkParser*>(userData);
    MetalinkStr data(s, len);
    parser->character_data(data);
}

MetalinkParser::MetalinkParser()
{
    _parser = XML_ParserCreateNS(0, TSTR('\''));
    XML_SetElementHandler(_parser, StartElementHandler, EndElementHandler);
    XML_SetCharacterDataHandler(_parser, CharacterDataHandler);
    XML_SetUserData(_parser, this);
    _depth = 0;
    _state = STATE_READY;
}

MetalinkParser::~MetalinkParser()
{
    XML_ParserFree(_parser);
}

Metalink MetalinkParser::get_metalink()
{
    return _ml;
}

bool MetalinkParser::finished()
{
    return (_state == STATE_DONE);
}

void MetalinkParser::start_element(MetalinkStr name, map<MetalinkStr, MetalinkStr> atts)
{
    _depth++;
    switch(_state)
    {
        case STATE_READY:
            if(_depth == 1 && name == TSTR("http://www.metalinker.org/'metalink")) {
                if(atts.count(TSTR("version")) == 1 && atts[TSTR("version")] == TSTR("3.0")) {
                    _state = STATE_METALINK;
                }
                else {
                    _failed();
                }
            }
        break;
        case STATE_METALINK:
            if(_depth == 2 && name == TSTR("http://www.metalinker.org/'files")) {
                _state = STATE_FILES;
            }
        break;
        case STATE_FILES:
            if(_depth == 3 && name == TSTR("http://www.metalinker.org/'file")) {
                if(atts.count(TSTR("name")) == 1) {
                    _file = MetalinkFile();
                    _file.filename = atts[TSTR("name")];
                    // Only add this file if the filename doesn't contain any path separators ( / in unix and \ in win32).
                    // Done to ensure maximum security, so that nobody can fool us into saving a file in a vulnerable place.
                    if(_file.filename.find(TSTR("/")) == tstring::npos && _file.filename.find(TSTR("\\")) == tstring::npos) {
                        _state = STATE_FILE;
                    }
                }
                else {
                    _failed();
                }
            }
        break;
        case STATE_FILE:
            if(_depth == 4) {
                if(name == TSTR("http://www.metalinker.org/'size")) {
                    _state = STATE_FILE_SIZE;
                }
                else if(name == TSTR("http://www.metalinker.org/'resources")) {
                    _state = STATE_RESOURCES;
                }
                else if(name == TSTR("http://www.metalinker.org/'verification")) {
                    _state = STATE_VERIFICATION;
                }
            }
        break;
        case STATE_RESOURCES:
            if(_depth == 5 && name == TSTR("http://www.metalinker.org/'url")) {
                _url = MetalinkUrl();
                if(atts.count(TSTR("location")) == 1) {
                    _url.location = atts[TSTR("location")];
                }
                if(atts.count(TSTR("preference")) == 1) {
                    stringstream ss;
                    ss << t2s(atts[TSTR("preference")]);
                    ss >> _url.preference;
                }
                _state = STATE_RESOURCES_URL;
            }
        break;
        case STATE_VERIFICATION:
            if(_depth == 5) {
                if(name == TSTR("http://www.metalinker.org/'hash")) {
                    if(atts.count(TSTR("type")) == 1) {
                        _type = atts[TSTR("type")];
                        _state = STATE_VERIFICATION_HASH;
                    }
                }
                else if(name == TSTR("http://www.metalinker.org/'pieces")) {
                    if(atts.count(TSTR("type")) == 1 && atts.count(TSTR("length")) == 1) {
                        _file.piece_type = atts[TSTR("type")];
                        stringstream ss;
                        ss << t2s(atts[TSTR("length")]);
                        ss >> _file.piece_length;
                        _pieces.clear();
                        _state = STATE_VERIFICATION_PIECES;
                    }
                }
            }
        break;
        case STATE_VERIFICATION_PIECES:
            if(_depth == 6 && name == TSTR("http://www.metalinker.org/'hash")) {
                if(atts.count(TSTR("piece")) == 1) {
                    stringstream ss;
                    ss << t2s(atts[TSTR("piece")]);
                    ss >> _piece_id;
                    _state = STATE_VERIFICATION_PIECE;
                }
            }
        break;
    }
    _content = MetalinkStr();
}

void MetalinkParser::end_element(MetalinkStr name)
{
    trim(_content);
    switch(_state)
    {
        case STATE_METALINK:
            if(_depth == 1) {
                _state = STATE_DONE;
            }
        break;
        case STATE_FILES:
            if(_depth == 2) {
                _state = STATE_METALINK;
            }
        break;
        case STATE_FILE:
            if(_depth == 3) {
                _ml.files.push_back(_file);
                _state = STATE_FILES;
            }
        break;
        case STATE_FILE_SIZE:
            if(_depth == 4) {
                stringstream ss;
                ss << t2s(_content);
                ss >> _file.size;
                _state = STATE_FILE;
            }
        break;
        case STATE_RESOURCES:
            if(_depth == 4) {
                _state = STATE_FILE;
            }
        break;
        case STATE_RESOURCES_URL:
            if(_depth == 5) {
                _url.url = _content;
                _file.urls.push_back(_url);
                _state = STATE_RESOURCES;
            }
        break;
        case STATE_VERIFICATION:
            if(_depth == 4) {
                _state = STATE_FILE;
            }
        break;
        case STATE_VERIFICATION_HASH:
            if(_depth == 5) {
                _file.hashes[_type] = _content;
                _state = STATE_VERIFICATION;
            }
        break;
        case STATE_VERIFICATION_PIECES:
            if(_depth == 5) {
                // Add pieces to _file, in the right order.
                int num = static_cast<int>(_pieces.size());
                for(int i = 0; i < num; i++) {
                    if(_pieces.count(i) == 1) {
                        _file.piece_hashes.push_back(_pieces[i]);
                    }
                    else {
                        // This piece is missing - skip all the pieces.
                        _file.piece_hashes.clear();
                        _file.piece_length = 0;
                        _file.piece_type = MetalinkStr();
                        break;
                    }
                }
                _state = STATE_VERIFICATION;
            }
        break;
        case STATE_VERIFICATION_PIECE:
            if(_depth == 6) {
                _pieces[_piece_id] = _content;
                _state = STATE_VERIFICATION_PIECES;
            }
        break;
    }
    _depth--;
}

void MetalinkParser::character_data(MetalinkStr data)
{
    _content += data;
}

bool MetalinkParser::parse(string data)
{
    enum XML_Status result = XML_Parse(_parser, data.c_str(), data.length(), 0);
    if(result != XML_STATUS_OK) return false;
    return true;
}

void MetalinkParser::_failed()
{
    _state = STATE_ERROR;
    XML_StopParser(_parser, false);
}

// PUBLIC FUNCTIONS

Metalink load_file(std::string filename)
{
    MetalinkParser parser;
    ifstream file(filename.c_str(), ios_base::in | ios_base::binary);
    if(file.fail()) THROW_EXCEPTION("Failed to open file.");
    char buf[1024];
    while(file.good())
    {
        file.read(buf, sizeof(buf));
        string data(buf, file.gcount());
        if(!parser.parse(data)) break;
    }
    if(file.fail() && !file.eof()) THROW_EXCEPTION("Read error!");
    if(!parser.finished()) THROW_EXCEPTION("Parse error!");
    return parser.get_metalink();
}

}
