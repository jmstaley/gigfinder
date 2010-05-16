#!/usr/bin/env python

"""Simple program to display local gigs

Intended for use on the N900, uses the devices gps to find local gigs.
"""

__authors__ = ["Jon Staley"]
__copyright__ = "Copyright 2010 Jon Staley"
__license__ = "MIT"
__version__ = "0.0.1"

from xml.dom.minidom import parseString
from datetime import datetime, date
import urllib
import time
import gtk
import hildon
import location
import time
import gobject
from threading import Thread
import thread

from locator import LocationUpdater

gtk.gdk.threads_init()

class GigParser:

    def parse_xml(self, xml, lat, long):
        """ Parse xml into a dict """
        events_list = []
        today = date.today()
        dom = parseString(xml)

        events = dom.getElementsByTagName('event')
        for event in events:
            start_date = self.parse_date(event.getElementsByTagName('startDate')[0].childNodes[0].data)
            if start_date.date() == today:
                title = event.getElementsByTagName('title')[0].childNodes[0].data
                
                artists_element = event.getElementsByTagName('artists')[0]
                artist_list = []
                for artist in artists_element.getElementsByTagName('artist'):
                    artist_list.append(artist.childNodes[0].data)
                artists = ', '.join(artist_list)

                venue_details = event.getElementsByTagName('venue')[0]
                venue_name = venue_details.getElementsByTagName('name')[0].childNodes[0].data
                address = self.get_address(venue_details.getElementsByTagName('location')[0])
                geo_data = venue_details.getElementsByTagName('geo:point')[0]
                venue_lat = geo_data.getElementsByTagName('geo:lat')[0].childNodes[0].data
                venue_long = geo_data.getElementsByTagName('geo:long')[0].childNodes[0].data
                distance = location.distance_between(float(lat), 
                                                     float(long), 
                                                     float(venue_lat), 
                                                     float(venue_long))
                
                events_list.append({'title': title,
                                    'venue': venue_name,
                                    'address': address,
                                    'distance': distance,
                                    'artists': artists,
                                    'date': start_date})
        return events_list
    
    def get_address(self, location):
        """ Return the venues address details from the xml element """
        street = ''
        city = ''
        country = ''
        postalcode = ''
        if location.getElementsByTagName('street')[0].childNodes:
            street = location.getElementsByTagName('street')[0].childNodes[0].data
        if location.getElementsByTagName('city')[0].childNodes:
            city = location.getElementsByTagName('city')[0].childNodes[0].data
        if location.getElementsByTagName('country')[0].childNodes:
            country = location.getElementsByTagName('country')[0].childNodes[0].data
        if location.getElementsByTagName('postalcode')[0].childNodes:
            postalcode = location.getElementsByTagName('postalcode')[0].childNodes[0].data
        return '\n'.join([street, city, country, postalcode])

    def parse_date(self, date_string):
        """ Parse date string into datetime object """
        fmt =  "%a, %d %b %Y %H:%M:%S"
        result = time.strptime(date_string, fmt)
        return datetime(result.tm_year, 
                        result.tm_mon, 
                        result.tm_mday, 
                        result.tm_hour, 
                        result.tm_min, 
                        result.tm_sec)


class Events:

    def __init__(self):
        self.api_key = "1928a14bdf51369505530949d8b7e1ee"
        self.url_base = "http://ws.audioscrobbler.com/2.0/"

    def get_events(self, lat, long, distance):
        """ Retrieve xml and parse into events list """
        xml = self.get_xml(lat, long, distance)
        events = self.parser.parse_xml(xml, 
                                       lat,
                                       long)
        return self.sort_events(events)

    def sort_events(self, events):
        """ Sort gig by distance """
        events.sort(cmp=self.distance_cmp, key=lambda x: x['distance'])
        return events
        
    def get_xml(self, lat, long, distance):
        """ Return xml from lastfm """
        method = "geo.getevents"
        params = urllib.urlencode({'method': method,
                                   'api_key': self.api_key,
                                   'distance': distance,
                                   'long': long,
                                   'lat': lat})
        response = urllib.urlopen(self.url_base, params)
        return response.read()
    
    def distance_cmp(self, x, y):
        """ Compare distances for list sort """
        if x > y:
            return 1
        elif x == y:
            return 0
        else:
            return -1


class GigFinder:

    def __init__(self):
        self.lat = None
        self.long = None
        self.distance = '10'
        self.banner = None
        self.parser = GigParser()
        self.location = LocationUpdater()
        self.events = Events()
        self.win = hildon.StackableWindow()
        self.app_title = "Gig Finder"
        # TODO: 
        # Add user settings for distance, date
        # refactor gui code, 
        # maybe do km to mile conversions

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
        gobject.idle_add(self.location.update_location)

        # if no gps fix wait
        # TODO: needs a timeout
        while not self.location.lat or not self.location.long:
            time.sleep(1)

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
        """ Hide banner and sete progress indicator """
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
        buffer.insert(end, 'When: %s\n' % data['date'].strftime('%H:%M %d/%M/%Y'))
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
            self.table.attach(button, 0, 1, pos, pos+1)
            pos += 1
        self.table.show_all()
   
if __name__ == "__main__":
    finder = GigFinder()
    finder.main()
