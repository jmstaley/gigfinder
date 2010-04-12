from xml.dom.minidom import parseString
from datetime import datetime, date
import time

import location

def parse_json(json, lat, long):
    """ Parse json into usable format """
    pass

def parse_xml(xml, lat, long):
    """ Parse xml into a dict """
    events_list = []
    today = date.today()
    dom = parseString(xml)

    events = dom.getElementsByTagName('event')
    for event in events:
        start_date = parse_date(event.getElementsByTagName('startDate')[0].childNodes[0].data)
        if start_date.date() == today:
            title = event.getElementsByTagName('title')[0].childNodes[0].data
            
            artists_element = event.getElementsByTagName('artists')[0]
            artist_list = []
            for artist in artists_element.getElementsByTagName('artist'):
                artist_list.append(artist.childNodes[0].data)
            artists = ', '.join(artist_list)

            venue_details = event.getElementsByTagName('venue')[0]
            venue_name = venue_details.getElementsByTagName('name')[0].childNodes[0].data
            address = get_address(venue_details.getElementsByTagName('location')[0])
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

def get_address(location):
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
