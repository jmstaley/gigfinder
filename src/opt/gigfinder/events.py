import urllib
import urllib2
from datetime import date
from xml.dom.minidom import parse

import location

from resultsparser import  parse_json

class Event:
    """ Represents events """
    def __init__(self, 
                 title, 
                 venue_name, 
                 address, 
                 lng,
                 lat,
                 artists, 
                 start_date):
        self.title = title
        self.venue_name = venue_name
        self.address = address
        self.lng = lng
        self.lat = lat
        self.artists = artists
        self.start_date = start_date

    def get_distance_from(self, lng, lat):
        """ return distance in km from points passed """
        return location.distance_between(float(lat), 
                                         float(lng), 
                                         float(self.lat), 
                                         float(self.lng))

class Events:
    """ Main accessible class for all events """
    def __init__(self):
        self.api_key = '1928a14bdf51369505530949d8b7e1ee'
        self.url_base = 'http://ws.audioscrobbler.com/2.0/'
        self.format = 'json'
        self.method = 'geo.getevents'
        self.metros_file = '/usr/share/gigfinder/metros.xml'

        self.lat = None
        self.long = None
        self.distance = '10'
        self.gps_search = False
        self.selected_location = ''
        self.search_date = date.today()

    def set_lat_long(self, lat, lng):
        """ set latitude and longitude """
        self.lat = lat
        self.long = lng

    def set_distance(self, distance):
        """ set distance for radius """
        self.distance = distance

    def set_gps_search(self, gps_search):
        """ is it a gps search """
        self.gps_search = gps_search

    def set_location(self, metro):
        """ set location chosen by the user """
        self.selected_location = metro

    def set_date(self, search_date):
        """ set the date of the search """
        self.search_date = search_date

    def get_events(self):
        """ Retrieve json and parse into events list """
        events = []
        result = self._get_json()
        for event in parse_json(result):
            if self.search_date == event[6].date():
                events.append(Event(event[0],
                                    event[1],
                                    event[2],
                                    event[3],
                                    event[4],
                                    event[5],
                                    event[6]))
        if self.gps_search:
            return self._sort_events(events)
        else:
            return events

    def get_metros(self):
        """ Parse metros out of file and return sorted list """
        metros = []
        dom = parse(self.metros_file)
        for element in dom.getElementsByTagName('name'):
            metros.append(element.childNodes[0].data)
        metros.sort()
        return metros

    def _sort_events(self, events):
        """ Sort gig by distance """
        if len(events) > 1:
            events.sort(cmp=self._distance_cmp, 
			key=lambda x: x.get_distance_from(self.long, self.lat))
        return events

    def _get_json(self):
        """ get the json from the api """
        params = {'method': self.method,
                  'api_key': self.api_key,
                  'format': self.format}
        if not self.gps_search:
            params['location'] = self.selected_location
        else:
            params['distance'] = self.distance
            params['long'] = self.long
            params['lat'] = self.lat

        params = urllib.urlencode(params)
        url = '%s?%s' % (self.url_base, params)
        request = urllib2.Request(url, None)
        response = urllib2.urlopen(request)
        return response.read()
        
    def _distance_cmp(self, x, y):
        """ Compare distances for list sort """
        if x > y:
            return 1
        elif x == y:
            return 0
        else:
            return -1
