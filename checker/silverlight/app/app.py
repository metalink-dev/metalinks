from System.Windows import Application
from System.Windows.Controls import Canvas, TextBlock

#import download
#import sys

class TextOut:
    def __init__(self, string):
        self.string = string

    def write(self, text):
        self.string = text


canvas = Canvas()
textblock = TextBlock()
textblock.FontSize = 20
textblock.Text = 'Text'
canvas.Children.Add(textblock)

Application.Current.RootVisual = canvas

#sys.stdout = TextOut(textblock.Text)


#print "more stuff"


#import System.Net
#import System.Net.Sockets
#from System.Net import *
#from System.Net.Sockets import *


#listener = TcpListener(IPAddress.Any, 4530)
#print dir(listener)
#textblock.Text = dir(listener)
