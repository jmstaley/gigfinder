from datetime import datetime
import time
import simplejson

def parse_json(json):
    """ Parse json into usable format """
    json = simplejson.loads(json)

    events = json['events']['event']
    for event in events:
        venue_location = event['venue']['location']
        address = '\n'.join([venue_location['street'],
                             venue_location['city'],
                             venue_location['country'],
                             venue_location['postalcode']])
        venue_geo = venue_location['geo:point']
        if type(event['artists']['artist']) == list:
            artist = '\n'.join(event['artists']['artist'])
        else:
            artist = event['artists']['artist']
                
        yield (event['title'], 
               event['venue']['name'], 
               address, 
               venue_geo['geo:long'],
               venue_geo['geo:lat'],
               artist, 
               parse_date(event['startDate']))
        

def parse_date(date_string):
    """ Parse date string into datetime object """
    fmt =  "%a, %d %b %Y %H:%M:%S"
    result = time.strptime(date_string, fmt)
    return datetime(result.tm_year, 
                    result.tm_mon, 
                    result.tm_mday, 
                    result.tm_hour, 
                    result.tm_min, 
                    result.tm_sec)
