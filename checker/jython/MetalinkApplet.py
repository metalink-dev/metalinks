import metalink

from java.applet import Applet

class MetalinkApplet(Applet):
    def paint(self, g):
        g.drawString("Hello from Jython!", 20, 30)
