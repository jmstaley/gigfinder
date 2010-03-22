#!/usr/bin/env python2.5

"""Simple program to display local gigs

Intended for use on the N900, uses the devices gps to find local gigs.
"""

__author__ = "Jon Staley"
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

class GigParser:

    def parse_xml(self, xml, lat, long):
        """ Parse xml into a dict """
        # TODO: filter to todays events only
        events_list = []
        today = date.today()
        dom = parseString(xml)

        events = dom.getElementsByTagName('event')
        for event in events:
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
            
            start_date = self.parse_date(event.getElementsByTagName('startDate')[0].childNodes[0].data)
            
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


class GigFinder:

    def __init__(self):
        self.lat = None
        self.long = None
        self.url_base = "http://ws.audioscrobbler.com/2.0/"
        self.api_key = "1928a14bdf51369505530949d8b7e1ee"
        self.distance = '10'

        program = hildon.Program.get_instance()
        self.win = hildon.StackableWindow()
        self.win.set_title('Gig Finder')
        self.win.connect("destroy", gtk.main_quit, None)

        pannable_area = hildon.PannableArea()

        self.table = gtk.Table(columns=1)
        self.table.set_row_spacings(10)
        self.table.set_col_spacings(10)

        pannable_area.add_with_viewport(self.table)

        self.win.add(pannable_area)

        self.update_gigs()

    def main(self):
        self.win.show_all()
        gtk.main()

    def update_gigs(self):
        """ Get gig info """
        parser = GigParser()
        self.get_lat_long()
        xml = self.get_xml()
        events = parser.parse_xml(xml, self.lat, self.long)
        self.add_events(events)
        
    def get_xml(self):
        """ Return xml from lastfm """
        method = "geo.getevents"
        params = urllib.urlencode({'method': method,
                                   'api_key': self.api_key,
                                   'distance': self.distance,
                                   'long': self.long,
                                   'lat': self.lat})
        response = urllib.urlopen(self.url_base, params)
        return response.read()

    def get_lat_long(self):
        """ Access gps and return current long lats """
        # TODO: Improve geolocation code, very crude atm
        control = location.GPSDControl.get_default()
        device = location.GPSDevice()
        control.start()
        fix = device.fix
        control.stop()
        self.lat, self.long = fix[4:6]
        #self.lat, self.long = ('51.546228', '-0.075016')

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
        buffer.insert(end, data['address'])
        buffer.insert(end, 'When: %s\n' % data['date'].strftime('%H:%M'))
        buffer.insert(end, '\n')
        scroll.add_with_viewport(view)

        win.show_all()
        
    def add_events(self, events):
        """ Return table of buttons """
        pos = 0
        for event in events:
            button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, 
                                   hildon.BUTTON_ARRANGEMENT_VERTICAL)
            button.set_text(event['title'], "distance: %0.02f km" % event['distance'])
            button.connect("clicked", self.show_details, event)
            self.table.attach(button, 0, 1, pos, pos+1)
            pos += 1



    #hildon.hildon_gtk_window_set_progress_indicator(win, 1)
    #banner = hildon.hildon_banner_show_information(win,
    #                                               "Updating", 
    #                                               "Retrieving gig info")
    #banner.hide()
    #hildon.hildon_gtk_window_set_progress_indicator(win, 0)

   
if __name__ == "__main__":
    finder = GigFinder()
    finder.main()
