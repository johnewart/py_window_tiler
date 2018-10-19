from Xlib.display import Display
from Xlib import X, Xatom
from Xlib.ext import randr
import Xlib

import pprint
pp = pprint.PrettyPrinter(indent=4)

class Region():
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height 

    def __str__(self):
        return "<Region @ %d, %d is %d x %d>" % (self.x, self.y, self.width,
                self.height)


class Column(): 
    def __init__(self):
        self.windows = []

class RowLayout():
    def __init__(self, region = None, parent_layout = None):
        self.parent_layout = parent_layout
        if region is None:
            region = Region(x = 0, y = 0, width = 0, height = 0)
        self.region = region
        self.windows = []

    def window_count(self):
        return len(self.windows)

    def add_window(self, window):
        if window not in self.windows:
            self.windows.append(window)

    def remove_window(self, window):
        try:
            self.windows.remove(window)
        except ValueError:
            pass

    def get_vertical_gap(self):
        try:
            return self.vertical_gap
        except AttributeError:
            return 0


    def window_top_padding(self):
        try:
            return self.wnd_top_padding
        except AttributeError:
            return self.parent_layout.window_top_padding()


    def redraw(self):
        if len(self.windows) > 0:
            cell_height = (self.region.height / len(self.windows)) - self.window_top_padding()
            cell_width = self.region.width 
            vertical_gap = self.get_vertical_gap()
            
            x = self.region.x
            y = self.region.y 

            for window in self.windows:
                print("Resizing window %s to %d x %d @ %d, %d" % (window, cell_width,
                    cell_height, x, y))
                window.configure(width = cell_width, 
                                 height = cell_height,
                                 x = x, y = y)
                y = y + cell_height + self.window_top_padding()

# Three column layout,66/33 
class TwoColumnLayout():

    LEFT = 0
    RIGHT = 1 

    def __init__(self, region, parent_layout):
        self.columns = [
                RowLayout(parent_layout = self),
                RowLayout(parent_layout = self)
            ]
        self.region = region
        self.parent_layout = parent_layout
        self.top_padding = 32
        self.wnd_top_padding = 24 

    def get_wm_title_size(self):
        if self.wm_title_size is not None:
            return self.wm_title_size 
    
    def window_top_padding(self):
        if self.window_top_padding is not None:
            return self.wnd_top_padding
        else:
            return parent_layout.window_top_padding()


    def window_count(self):
        count = 0
        for col in columns:
            count = count + col.window_count()
        return count 

    # Add to middle column, only one, then add to sides, left then right...
    def add_window(self, window):
        left = self.columns[self.LEFT]
        right = self.columns[self.RIGHT]

        target = None

        if left.window_count() == 0:
            target = left
        else:
            target = right

        target.add_window(window)

    def remove_window(self, window):
        for col in self.columns:
            col.remove_window(window)
    
    def redraw(self):
        print("Screen width: %d" % (self.region.width))
        left_col = self.columns[self.LEFT]
        right_col = self.columns[self.RIGHT]
        column_height = self.region.height
        x = self.region.x
        y = self.region.y

        if (right_col.window_count() == 0):
            # FULL SCREEN BABY!
            left_width = self.region.width
            right_width = 0
        else:
            left_width = int((float(self.region.width) / 3.0) * 2.0)
            right_width = self.region.width - left_width

        left_col.region.width = left_width
        left_col.region.height = column_height
        left_col.region.x = x
        left_col.region.y = y

        right_col.region.width = right_width
        right_col.region.height = column_height
        right_col.region.x = x + left_width
        right_col.region.y = y

        left_col.redraw()
        right_col.redraw()

          
# Three column layout, 33/33/33
class ThreeColumnLayout():

    LEFT = 0
    MIDDLE = 1
    RIGHT = 2

    def __init__(self, region, parent_layout):
        self.columns = [
                RowLayout(parent_layout = self),
                RowLayout(parent_layout = self), 
                RowLayout(parent_layout = self)
            ]
        self.region = region
        self.parent_layout = parent_layout
        self.redraw()
      
    def window_count(self):
        count = 0
        for col in columns:
            count = count + col.window_count()
        return count 

    # Add to middle column, only one, then add to sides, left then right...
    def add_window(self, window):
        left = self.columns[self.LEFT]
        middle = self.columns[self.MIDDLE]
        right = self.columns[self.RIGHT]

        target = None

        if middle.window_count() == 0:
            target = middle
        else:
            if left.window_count() <= right.window_count(): 
                target = left
            else:
                target = right

        target.add_window(window)

    def remove_window(self, window):
        for col in self.columns:
            col.remove_window(window)
    
    def redraw(self):
        column_height = self.region.height
        column_width = self.region.width / 3
        column_count = 3

        current_x = 0
        current_y = 0

        for i in range(column_count):
            col = self.columns[i]
            col.region.width = column_width
            col.region.height = column_height
            col.region.x = current_x
            col.region.y = current_y
            current_x = current_x + column_width

        for i in range(column_count):
            col = self.columns[i]
            col.redraw()

        
        return None

class Environment():

    
    def __init__(self):
        self.display = Display()
        self.screen = self.display.screen()
        self.root = self.screen.root
        self.region = Region(x = 0, y = 0, width = self.screen.width_in_pixels,
                height = self.screen.height_in_pixels)
        self.desktops = []
        self.windows = self.get_window_set()
        self.window_desktop_map = {}

     
        for i in range(self.number_of_desktops()):
            print("\n\n\nCreating Desktop %d" % (i))
            d = Desktop(i, self)
            self.desktops.append(d)
            #d.print_windows()
            d.arrange()

        self.update_desktop_map()
        self.setup_listeners()

        #self.print_hierarchy(self.root, " - ")
   
    def setup_listeners(self):
        self.root.change_attributes(event_mask =
                X.SubstructureNotifyMask|X.PropertyChangeMask)
      
        anchor = self.root.create_window(0, 0, 1, 1, 1, self.screen.root_depth)

        anchor.xrandr_select_input(
                          randr.RRScreenChangeNotifyMask
                          | randr.RRCrtcChangeNotifyMask
                          | randr.RROutputChangeNotifyMask
                          | randr.RROutputPropertyNotifyMask
                   )



    def update_all_the_things(self):
        self.display = Display()
        self.screen = self.display.screen()
        self.root = self.screen.root
        self.region = Region(x = 0, y = 0, width = self.screen.width_in_pixels,
                height = self.screen.height_in_pixels - 32)

        print("NEW REGION: %s" % (self.region))
        
        for d in self.desktops:
            d.resize()

        self.setup_listeners()
        
    def print_hierarchy(self, window, indent):
        children = window.query_tree().children
        for w in children:
            print(indent, window.get_wm_class())
            self.print_hierarchy(w, indent+'-')


    def interesting_properties(self):
        #_NET_WM_DESKTOP
        # root: _NET_CURRENT_DESKTOP
        print("Current desktop")
        print(self.root.get_full_property(self.display.intern_atom('_NET_CURRENT_DESKTOP'),
            Xatom.CARDINAL).value[0])

    def current_desktop(self):
        return self.root.get_full_property(self.display.intern_atom('_NET_CURRENT_DESKTOP'), Xatom.CARDINAL).value[0]

    def number_of_desktops(self):
        return self.root.get_full_property(self.display.intern_atom('_NET_NUMBER_OF_DESKTOPS'), Xatom.CARDINAL).value[0]

    def update_desktop_map(self):
        self.window_desktop_map = {}
        for d in self.desktops:
            for window_id in d.get_window_set():
                self.window_desktop_map[window_id] = d

    def get_window_desktop(self, window):
        if type(window) is long:
            w = self.display.create_resource_object('window', window)
        else:
            w = window

        try:
            value = w.get_full_property(self.display.intern_atom('_NET_WM_DESKTOP'), Xatom.CARDINAL).value[0]
            if value > self.number_of_desktops():
                return None
            else:
                return value

        except AttributeError:
            return None
        except Xlib.error.BadWindow:
            return None

    def get_window_states(self, window):
        w = self.display.create_resource_object('window', window)
        #return w.get_full_property(self.display.intern_atom('_NET_WM_STATE'), Xatom.ATOM).value
        try:
	    states = w.get_full_property(self.display.get_atom('_NET_WM_STATE'), Xatom.WINDOW)
        except Xlib.error.BadWindow:
            states = None

	if states == None:
            return []
        else:
            return w.get_full_property(self.display.get_atom('_NET_WM_STATE'), 0).value.tolist()

    def is_window_hidden(self, window):
        states = self.get_window_states(window)
        hidden = self.display.get_atom("_NET_WM_STATE_HIDDEN") in states
        #print("Window %d is hidden: %s" % (window, hidden))
        return hidden

    def is_window_visible(self, window):
        return not self.is_window_hidden(window)


    def listen_for_events(self):
        print("Listening for change events!")
        while True:
            ev = self.display.next_event()
            self.handle_event(ev)

    def handle_event(self, event):
        needs_update = False

	wm_active_window = self.display.get_atom('_NET_ACTIVE_WINDOW')

        if event.type == X.PropertyNotify:
            print("Property changed...")
            if event.atom == wm_active_window:
                print("Property changed on an active window....")
                data = event.window.get_full_property(event.atom, 0)
                window_id = int(data.value.tolist()[0])
                desktop = self.window_desktop_map.get(window_id, None)
                print("Window changed: %s on desktop: %s" % (window_id, desktop))
                if desktop is not None: 
                    desktop.arrange()
                    needs_update = True         
               
        elif event.type == X.CreateNotify or event.type == X.DestroyNotify:
            needs_update = True
            window_set = self.get_window_set()

            if event.type == X.CreateNotify:
                print("Handling creation!")
                new_windows = window_set.difference(self.windows)
                for window in new_windows:
                    window_resource = self.display.create_resource_object('window', window)
                    window_desktop = self.get_window_desktop(window_resource)
                    if window_desktop is not None:
                        self.desktops[window_desktop].layout.add_window(window_resource)

            if event.type == X.DestroyNotify:
                print("Handling destruction!")
                missing_windows = self.windows.difference(window_set)
                for window in missing_windows:
                    window_resource = self.display.create_resource_object('window', window)
                    # TODO: optimize lookup by keeping old map?
                    for desktop in self.desktops:
                        desktop.layout.remove_window(window_resource)

            self.windows = window_set

            for desktop in self.desktops:
                desktop.layout.redraw()
       
        elif event.__class__.__name__ == randr.ScreenChangeNotify.__name__:
            print('Screen change')
            print(pp.pprint(event._data))
            self.update_all_the_things()

        else:
            #print("Unhandled event: %d" % (event.type))
            pass

        if needs_update:
            self.update_desktop_map()


    def get_window_set(self, include_hidden = False, desktop_number = None):
        windows = set([x for x in self.root.get_full_property(self.display.intern_atom('_NET_CLIENT_LIST'), Xatom.WINDOW).value])

        if desktop_number is not None:
            #print("Filtering windows not on: %d" % (desktop_number))
            windows = filter(lambda w: self.get_window_desktop(w) == desktop_number, windows)
   
        if include_hidden is False:
            #print("Filtering hidden windows...")
            windows = filter(lambda w: self.is_window_visible(w) == True, windows)

        return set(windows)

class Desktop():
    def __init__(self, desktop_number, environment):
        self.environment = environment
        self.display = environment.display
        self.screen = self.display.screen()
        self.root = self.screen.root
        self.desktop_number = desktop_number
        self.region = environment.region
        self.update_layout()

    def update_layout(self):
        if self.region.width <= 1920:
            self.layout = TwoColumnLayout(region = self.region, parent_layout = None)
        else: 
            self.layout = ThreeColumnLayout(region = self.region, parent_layout = None)



    def print_windows(self):
        print("Windows on desktop %d" % (self.desktop_number))
        for window in self.get_window_set():
            w = self.display.create_resource_object('window', window)
            try:
                print("Window: %s (%s)" % (w.get_wm_name(), w.get_wm_class()))
            except UnicodeDecodeError:
                print("Failed on %s" % (window))
   
    def resize(self):
        self.display = self.environment.display
        self.screen = self.display.screen()
        self.root = self.screen.root
        self.region = self.environment.region
        self.arrange()
        
    def arrange(self):
        print("Rearranging with region: %s" % (self.region))
        self.update_layout()
        window_areas = []

        print("Arranging windows on desktop: %d" % (self.desktop_number))

        for window in self.get_window_set():
            w = self.display.create_resource_object('window', window)
            geom = w.get_geometry()
            window_areas.append({'window': w, 'area': (geom.height *
                geom.width)})
            #print("Geometry: %s" % geom)

        window_areas.sort(key=lambda x: x['area'], reverse=True)

        for element in window_areas:
            window = element['window']
            area = element['area']
            self.layout.add_window(window)

        self.layout.redraw()

    def get_window_set(self):
        return self.environment.get_window_set(desktop_number=self.desktop_number)

e = Environment()
e.listen_for_events()

