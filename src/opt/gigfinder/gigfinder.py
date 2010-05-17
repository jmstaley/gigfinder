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
        self.banner = None
        self.location = LocationUpdater()
        self.events = Events()
        self.win = hildon.StackableWindow()
        self.app_title = "Gig Finder"

    def main(self):
        """ Build the gui and start the update thread """
        program = hildon.Program.get_instance()
        menu = self.create_menu()

        self.win.set_title(self.app_title)
        self.win.connect("destroy", gtk.main_quit, None)
        self.win.set_app_menu(menu)

        Thread(target=self.update_gigs).start()

        self.win.show_all()
        gtk.main()

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

    def update(self, widget, data):
        """ Start update process """
        self.win.set_title(self.app_title)
        self.location.reset()
        self.win.remove(self.pannable_area)
        Thread(target=self.update_gigs).start()

    def update_gigs(self):
        """ Get gig info """
        gobject.idle_add(self.show_message, "Getting events")
        
        if not 'applications' in os.path.abspath(__file__):
            gobject.idle_add(self.location.update_location)

            # if no gps fix wait
            # TODO: needs a timeout
            while not self.location.lat or not self.location.long:
                time.sleep(1)
        else:
            self.location.lat = float(51.517369)
            self.location.long = float(-0.082998)

        events = self.events.get_events(self.location.lat, 
                                        self.location.long, 
                                        self.distance)
        gobject.idle_add(self.hide_message)
        gobject.idle_add(self.show_events, events)
        thread.exit()

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
        if events:
            self.win.set_title('%s (%s)' % (self.app_title, len(events)))
            self.add_events(events)
        else:
            label = gtk.Label('No events available')
            vbox = gtk.VBox(False, 0)
            vbox.pack_start(label, True, True, 0)
            vbox.show_all()
            self.win.add(vbox)

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

        menu = hildon.AppMenu()
        menu.append(update_button)
        menu.append(about_button)
        menu.show_all()
        return menu

    def show_details(self, widget, data):
        """ Open new window showing gig details """
        win = hildon.StackableWindow()
        win.set_title(data['title'])

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
        buffer.insert(end, '%s\n' % data['title'])
        buffer.insert(end, 'Artists: %s\n' % data['artists'])
        buffer.insert(end, 'Venue: %s\n' % data['venue'])
        buffer.insert(end, '%s\n' % data['address'])
        buffer.insert(end, 'When: %s\n' % data['date'].strftime('%H:%M %d/%m/%Y'))
        buffer.insert(end, '\n')
        scroll.add_with_viewport(view)

        win.show_all()

    def add_table(self):
        """ Add table for events """
        self.table = gtk.Table(columns=1)
        self.table.set_row_spacings(10)
        self.table.set_col_spacings(10)

        self.pannable_area = hildon.PannableArea()
        self.pannable_area.add_with_viewport(self.table)
        self.pannable_area.show_all()
        self.win.add(self.pannable_area)
        
    def add_events(self, events):
        """ Add a table of buttons """
        self.add_table()
        pos = 0
        
        for event in events:
            button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, 
                                   hildon.BUTTON_ARRANGEMENT_VERTICAL)
            button.set_text(event['title'], "distance: %0.02f km" % event['distance'])
            button.connect("clicked", self.show_details, event)
            self.table.attach(button, 0, 1, pos, pos+1, yoptions=gtk.FILL)
            pos += 1
        self.table.show_all()
            
if __name__ == "__main__":
    finder = GigFinder()
    finder.main()
