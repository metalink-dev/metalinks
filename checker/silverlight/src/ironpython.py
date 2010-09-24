import imp
import sys
import os

from System.Windows.Browser import HtmlPage  
class Writer(object):  
    def __init__(self):  
        self.stdout = '' 

    def write(self, text):  
        self.stdout += text
        element = HtmlPage.Document.debugging                              
        element.value = self.stdout

output_writer = Writer()  
sys.stdout = output_writer

def override_builtin(name):
    sys.modules[name] = module = imp.new_module(name)
    for path in sys.path:
        filename = os.path.join(path, name + '.py')
        try:
            execfile(file, module.__dict__)
        except: pass

override_builtin('socket')
