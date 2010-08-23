#!/usr/bin/env python

"""Simple program to display local gigs

Intended for use on the N900, uses the devices gps to find local gigs.
"""

__authors__ = ["Jon Staley"]
__copyright__ = "Copyright 2010 Jon Staley"
__license__ = "MIT"
__version__ = "0.0.1"

import gtk
import hildon
import time
import gobject
import os.path
from threading import Thread
import thread
from datetime import date

from locator import LocationUpdater
from events import Events

gtk.gdk.threads_init()

# TODO: 
# Add user settings for distance, date
# maybe switch to json
# maybe do km to mile conversions

class GigFinder:

    def __init__(self):
        self.lat = None
        self.long = None
        self.distance = '10'
        self.current_date = date.today()
        self.banner = None
        self.location = LocationUpdater()
        self.events = Events()
        self.win = hildon.StackableWindow()
        self.app_title = "Gig Finder"

    def main(self):
        """ Build the gui and start the update thread """
        gtk.gdk.threads_enter()
        program = hildon.Program.get_instance()
        menu = self.create_menu()

        self.win.set_title(self.app_title)
        self.win.connect("destroy", self.quit, None)
        self.win.set_app_menu(menu)

        button_box = gtk.VBox()
    	date_button = hildon.DateButton(gtk.HILDON_SIZE_AUTO,
	                                hildon.BUTTON_ARRANGEMENT_VERTICAL)
        date_button.set_title('Select date')
        date_button.connect('value-changed',
		            	    self.set_date,
            			    None)

        update_button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT,
                                           hildon.BUTTON_ARRANGEMENT_VERTICAL)
        update_button.set_label('Find Gigs')
        update_button.connect('clicked',
                              self.update,
                              None)
        
        button_box.pack_start(date_button, expand=False, fill=True, padding=5)
        button_box.pack_start(update_button, expand=False, fill=True, padding=5)
        
        self.win.add(button_box)
        self.win.show_all()
        gtk.main()
        k.gdk.threads_leave()

    def quit(self, widget, data):
        self.location.stop(widget, data)
        thread.exit()
        k.main_quit()
        return False

    def show_about(self, widget, data):
        """ Show about dialog """
        dialog = gtk.AboutDialog()
        dialog.set_name('Gig Finder')
        dialog.set_version(__version__)
        dialog.set_authors(__authors__)
        dialog.set_comments('Display gigs close by.\nUsing the http://www.last.fm api.')
        dialog.set_license('Distributed under the MIT license.\nhttp://www.opensource.org/licenses/mit-license.php')
        dialog.set_copyright(__copyright__)
        dialog.show_all()

    def show_message(self, message):
        """ Set window progress indicator and show message """
        hildon.hildon_gtk_window_set_progress_indicator(self.win, 1)
        self.banner = hildon.hildon_banner_show_information(self.win,
                                                            '', 
                                                            message)

    def hide_message(self):
        """ Hide banner and set progress indicator """
        self.banner.hide()
        hildon.hildon_gtk_window_set_progress_indicator(self.win, 0)

    def show_events(self, events):
        """ Sort events, set new window title and add events to table """
        win = hildon.StackableWindow()
        win.set_title(self.app_title)

        if events:
            self.add_button_area(win)
            win.set_title('%s (%s)' % (self.app_title, len(events)))
            self.add_events(events)
        else:
            label = gtk.Label('No events available')
            vbox = gtk.VBox(False, 0)
            vbox.pack_start(label, True, True, 0)
            vbox.show_all()
            win.add(vbox)
        win.show_all()

    def create_menu(self):
        """ Build application menu """
        update_button = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
        update_button.set_label('Update')
        update_button.connect('clicked',
                              self.update,
                              None)

        about_button = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
        about_button.set_label('About')
        about_button.connect('clicked',
                             self.show_about,
                             None)
	
    	date_button = hildon.DateButton(gtk.HILDON_SIZE_AUTO,
	                                hildon.BUTTON_ARRANGEMENT_VERTICAL)
        date_button.set_title('Select date')
        date_button.connect('value-changed',
		            	    self.set_date,
            			    None)

        menu = hildon.AppMenu()
        #menu.append(update_button)
        menu.append(about_button)
        menu.show_all()
        return menu

    def set_date(self, widget, data):
        year, month, day = widget.get_date()
        self.current_date = date(year, month+1, day)

    def show_details(self, widget, data):
        """ Open new window showing gig details """
        win = hildon.StackableWindow()
        win.set_title(data.title)

        win.vbox = gtk.VBox()
        win.add(win.vbox)

        scroll = hildon.PannableArea()
        win.vbox.pack_start(scroll, True, True, 0)

        view = hildon.TextView()
        view.set_editable(False)
        view.unset_flags(gtk.CAN_FOCUS)
        view.set_wrap_mode(gtk.WRAP_WORD)
        buffer = view.get_buffer()
        end = buffer.get_end_iter()
        buffer.insert(end, '%s\n' % data.title)
        buffer.insert(end, 'Artists: %s\n' % data.artists)
        buffer.insert(end, 'Venue: %s\n' % data.venue_name)
        buffer.insert(end, '%s\n' % data.address)
        buffer.insert(end, 'When: %s\n' % data.start_date.strftime('%H:%M %d/%m/%Y'))
        buffer.insert(end, '\n')
        scroll.add_with_viewport(view)

        win.show_all()

    def add_button_area(self, win):
        self.box = gtk.VBox(True,0)
        self.pannable_area = hildon.PannableArea()
        self.pannable_area.add_with_viewport(self.box)
        self.pannable_area.show_all()
        win.add(self.pannable_area)
        
    def add_events(self, events):
        """ Add a table of buttons """
        for event in events:
            button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, 
                                   hildon.BUTTON_ARRANGEMENT_VERTICAL)
            button.set_text(event.title, "distance: %0.02f km" % event.get_distance_from(self.location.long, self.location.lat))
            button.connect("clicked", self.show_details, event)
            self.box.pack_start(button)
        self.box.show_all()
            
    def update(self, widget, data):
        """ Start update process """
        self.location.reset()
        self.location.update_location()
        Thread(target=self.update_gigs).start()

    def update_gigs(self):
        """ Get gig info """
        gobject.idle_add(self.show_message, "Getting events")
        
        if not 'applications' in os.path.abspath(__file__):
            # if no gps fix wait
            while not self.location.lat or not self.location.long:
                time.sleep(1)
        else:
            self.location.lat = float(51.517369)
            self.location.long = float(-0.082998)
         
        events = self.events.get_events(self.location.lat, 
                                        self.location.long, 
                                        self.distance,
                                        self.current_date)
        gobject.idle_add(self.show_events, events)
        gobject.idle_add(self.hide_message)
        return True

if __name__ == "__main__":
    finder = GigFinder()
    finder.main()
