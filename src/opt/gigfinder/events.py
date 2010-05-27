import urllib
import urllib2

import location

from resultsparser import  parse_json

class Event:
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
        return location.distance_between(float(lat), 
                                         float(lng), 
                                         float(self.lat), 
                                         float(self.lng))

class Events:
    def __init__(self):
        self.api_key = '1928a14bdf51369505530949d8b7e1ee'
        self.url_base = 'http://ws.audioscrobbler.com/2.0/'
        self.format = 'json'
        self.method = 'geo.getevents'

    def get_events(self, lat, lng, distance):
        """ Retrieve json and parse into events list """
        events = []
        result = self.get_json(lat, lng, distance)
        for event  in parse_json(result):
            events.append(Event(event[0],
                                event[1],
                                event[2],
                                event[3],
                                event[4],
                                event[5],
                                event[6]))
        return self.sort_events(events, lat, lng)

    def sort_events(self, events, lat, lng):
        """ Sort gig by distance """
        if len(events) > 1:
            events.sort(cmp=self.distance_cmp, key=lambda x: x.get_distance_from(lng, lat))
        return events

    def get_json(self, lat='', lng='', distance=''):
        params = urllib.urlencode({'method': self.method,
                                   'api_key': self.api_key,
                                   'distance': distance,
                                   'long': lng,
                                   'lat': lat,
                                   'format': self.format})
        url = '%s?%s' % (self.url_base, params)
        request = urllib2.Request(url, None)
        response = urllib2.urlopen(request)
        return response.read()
        
    def distance_cmp(self, x, y):
        """ Compare distances for list sort """
        if x > y:
            return 1
        elif x == y:
            return 0
        else:
            return -1
