from window_tiler import * 
import threading
from gi.repository import GLib, Gtk, GObject, GdkPixbuf

import os

class TrayIcon:
    def __init__(self):
        basedir = os.path.dirname(os.path.realpath(__file__))
        icon_file = os.path.join(basedir, "icon.png")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon_file)
        icon_buf = pixbuf.scale_simple(16, 16, GdkPixbuf.InterpType.BILINEAR)
        self.icon = Gtk.StatusIcon()
        self.icon.set_from_pixbuf(icon_buf)
        self.icon.connect('popup-menu', self.on_right_click)
        self.icon.connect('activate', self.on_left_click)


    def message(self, data=None):
        msg = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL,
                              Gtk.MessageType.INFO, Gtk.ButtonsType.OK, data)
        msg.run()
        msg.destroy()
     
    def open_app(self, data=None):
        print("Should open!")
     
    def close_app(self, data=None):
        Gtk.main_quit()
     
    def on_right_click(self, icon, button, time):
        self.menu = Gtk.Menu()

        open_item = Gtk.MenuItem("Open App")
        open_item.connect_object("activate", self.open_app, "Open App")

        close_item = Gtk.MenuItem("Close App")
        close_item.connect_object("activate", self.close_app, "Close App")
    
        #Append the menu items  
        self.menu.append(open_item)
        self.menu.append(close_item)

        self.menu.show_all()

        def pos(menu, icon):
            return (Gtk.StatusIcon.position_menu(menu, icon))

        self.menu.popup(None, None, None, self.icon,
                             button, time)
          
             
    def on_left_click(self, event):
        self.message("Status Icon Left Clicked")
 


def do_work():
  e = Environment()
  e.listen_for_events()


if __name__ == '__main__':
  GObject.threads_init()
  thread = threading.Thread(target=do_work)
  thread.daemon = True
  thread.start()
  icon = TrayIcon()
  Gtk.main()

