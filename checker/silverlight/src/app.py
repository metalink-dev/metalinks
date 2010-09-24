from System.Windows import Application
from System.Windows.Controls import Canvas, TextBlock

import sys  

import metalinkc

print sys.version

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

print 'testing debug'

canvas = Canvas()
textblock = TextBlock()
textblock.FontSize = 24
textblock.Text = 'Hello World from IronPython'
canvas.Children.Add(textblock)

Application.Current.RootVisual = canvas

