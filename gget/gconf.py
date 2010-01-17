CLIENT_PRELOAD_RECURSIVE = 1
VALUE_STRING = 2

import xml.parsers.expat

class Client:
    def __init__(self):
        xml = ReadDefaults()
        xml.parsefile()
        self.opts = xml.get_dict()
        
    def dir_exists(self, dir):
        return True
        
    def add_dir(self, dir, opt):
        return

    def get_list(self, opt, type):
        return self.opts[opt]
        
    def get_string(self, opt):
        return str(self.opts[opt])
        
    def get_int(self, opt):
        return int(self.opts[opt])
        
    def get_bool(self, opt):
        return bool(self.opts[opt])
        
    def set_string(self, opt, value):
        return
        
    def set_int(self, opt, value):
        return
        
    def set_bool(self, opt, value):
        return
                
    def notify_add(self, opt, callback):
        return

        
class DefaultObj:
    def __init__(self, applyto=None, default=None):
        self.applyto = applyto
        self.default = default
        self.type = None
        
    def get_value(self):
        if self.type == 'list':
            return []
        else:
            return self.default
    
class ReadDefaults:
    def __init__(self):

        self.p = xml.parsers.expat.ParserCreate()

        self.p.StartElementHandler = self.start_element
        self.p.EndElementHandler = self.end_element
        self.p.CharacterDataHandler = self.char_data
        
        self.values = [
            DefaultObj("/apps/gget/system/http_proxy/use_http_proxy", "False"),
            DefaultObj("/apps/gget/system/http_proxy/use_authentication", "False"),
            DefaultObj("/apps/gget/system/http_proxy/authentication_user", ""),
            DefaultObj("/apps/gget/system/http_proxy/authentication_password", ""),
            DefaultObj("/apps/gget/system/http_proxy/host", ""),
            DefaultObj("/apps/gget/system/http_proxy/port", "0"),
            DefaultObj("/apps/gget/system/http_proxy/use_same_proxy", "False"),
            DefaultObj("/apps/gget/system/proxy/secure_host", ""),
            DefaultObj("/apps/gget/system/proxy/secure_port", "0"),
            DefaultObj("/apps/gget/system/proxy/ftp_host", ""),
            DefaultObj("/apps/gget/system/proxy/ftp_port", "0"),
            DefaultObj("/apps/gget/interface/toolbar_style", ""),
        ]
        
    def get_dict(self):
        mydict = {}
        for item in self.values:
            mydict[item.applyto] = item.get_value()
        return mydict

    # 3 handler functions
    def start_element(self, name, attrs):
        self.data = ""
        if name == "schema":
            self.values.append(DefaultObj())

    def end_element(self, name):
        if name == "applyto":
            self.values[-1].applyto = self.data
        if name == "default":
            self.values[-1].default = self.data
        if name == "type":
            self.values[-1].type = self.data
            
    def char_data(self, data):
        self.data += data #.strip()

    def parsefile(self, filename="data/gget.schemas.in"):
        handle = open(filename, "rb")
        try:
            self.parsehandle(handle)
        except:
            print filename
            raise
        handle.close()

    def parsehandle(self, handle):
        return self.p.ParseFile(handle)

    def parse(self, text):
        self.p.Parse(text)

        
def client_get_default():
    return Client()