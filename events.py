import urllib
import urllib2

from resultsparser import EventParser

class Events:
    def __init__(self):
        self.api_key = '1928a14bdf51369505530949d8b7e1ee'
        self.url_base = 'http://ws.audioscrobbler.com/2.0/'
        self.format = 'json'
        self.method = 'geo.getevents'
        self.parser = EventParser()

    def get_events(self, lat, long, distance):
        """ Retrieve xml and parse into events list """
        xml = self.get_xml(lat, long, distance)
        events = self.parser.parse_xml(xml, 
                                       lat,
                                       long)
        return self.sort_events(events)

    def sort_events(self, events):
        """ Sort gig by distance """
        if len(events) > 1:
            events.sort(cmp=self.distance_cmp, key=lambda x: x['distance'])
        return events

    def get_json(self, lat='', long='', distance=''):
        # testing json results
        lat = '51.5174'
        long = '-0.0829'
        distance = '10'
        params = urllib.urlencode({'method': self.method,
                                   'api_key': self.api_key,
                                   'distance': distance,
                                   'long': long,
                                   'lat': lat,
                                   'format': self.format})
        url = '%s?%s' % (self.url_base, params)
        request = urllib2.Request(url, None)
        response = urllib2.urlopen(request)
        return response
        
    def get_xml(self, lat, long, distance):
        """ Return xml from lastfm """
        params = urllib.urlencode({'method': self.method,
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
