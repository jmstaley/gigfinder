#!/usr/bin/env python

"""Simple program to display local gigs

Intended for use on the N900, uses the devices gps to find local gigs.
"""

import gtk
import hildon
import time
import gobject
import os.path
from threading import Thread
import thread
from datetime import date
from xml.dom.minidom import parse

import gigfinder_ui
from locator import LocationUpdater
from events import Events

gtk.gdk.threads_init()

__authors__ = ["Jon Staley"]
__copyright__ = "Copyright 2010 Jon Staley"
__license__ = "MIT"
__version__ = "0.0.1"

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
        self.gps_search = False
        self.selected_location = ''
        self.accuracy = '1000'
        self.metros_file = '/usr/share/gigfinder/metros.xml'
        self.version = __version__
        self.authors = __authors__
        self.copyright = __copyright__
        self.license = __license__
        
        self.ui = gigfinder_ui.GigfinderUI(self)
        self.events = Events()

    def main(self):
        """ Build the gui and start the update thread """
        gtk.gdk.threads_enter()
        program = hildon.Program.get_instance()
        gtk.main()
        gkt.gdk.threads_leave()
        
    def get_metros(self):
        metros = []
        dom = parse(self.metros_file)
        for element in dom.getElementsByTagName('name'):
            metros.append(element.childNodes[0].data)
        metros.sort()
        return metros

    def set_location(self, selector, data):
        self.selected_location = selector.get_current_text()

    def set_accuracy(self, selector, data):
        self.accuracy = selector.get_current_text()
        self.location.set_accuracy(self.accuracy)

    def quit(self, widget, data):
        self.location.stop(widget, data)
        thread.exit()
        k.main_quit()
        return False

    def toggle_gps(self):
        if self.gps_search:
            self.gps_search = False
	else:
            self.gps_search = True

    def set_date(self, widget, data):
        year, month, day = widget.get_date()
        self.current_date = date(year, month+1, day)

    def update(self, widget, data):
        """ Start update process """
        self.location.reset()
        self.location.update_location()
        Thread(target=self.update_gigs).start()

    def update_gigs(self):
        """ Get gig info """
        gobject.idle_add(self.ui.show_message, "Getting events")
        
	if self.gps_search:
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
					gps_search=self.gps_search,
                                        date=self.current_date,
					metro=self.selected_location)
        gobject.idle_add(self.ui.show_events, events, self.location)
        gobject.idle_add(self.ui.hide_message)
        return True

if __name__ == "__main__":
    finder = GigFinder()
    finder.main()
