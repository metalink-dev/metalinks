import urlparse

def make_uri_from_shell_arg(uri):
    return uri
    
def get_uri_scheme(uri):
    return urlparse.urlparse(uri).scheme
    
def get_file_mime_type(filename):
    return "/"