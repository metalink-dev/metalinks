import gtk
import gtk.gdk

class TrayIcon(gtk.StatusIcon):
    def __init__(self, name):
        gtk.StatusIcon.__init__(self)
    
    def add(self, eventbox):
        self.eb = eventbox
        image = eventbox.get_children()[0]
        icon_name = image.get_icon_name()[0] 
        self.set_from_icon_name(icon_name)
        self.connect("activate", self.activate)
        self.connect("popup_menu", self.popup)

    def activate(self, widget):
        window = self.eb.get_root_window()
        # this doesn't seem to work for some reason
        if window.is_visible():
            #print "hiding"
            window.hide()
        else:
            #print "showing"
            window.show()
        #print self.eb.translate_coordinates(self.eb.get_toplevel(), 0, 0)
        #event = gtk.gdk.Event(gtk.gdk.BUTTON_PRESS)
        #event.button = 1
        #event.x = 0
        #event.y = 0
        #gtk.main_do_event(event)
        #print self.eb.get_size_request()
        #self.eb.event(event)
        

    def popup(self, widget, two, three):
        #print widget,two, three
        pass
        
    def show_all(self):
        return
