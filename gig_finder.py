from xml.dom.minidom import parseString
from datetime import datetime, date
import time

def parse_xml(xml):
    """ Parse xml into a dict """
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

        venue = event.getElementsByTagName('venue')[0].getElementsByTagName('name')[0].childNodes[0].data
        start_date = parse_date(event.getElementsByTagName('startDate')[0].childNodes[0].data)
        events_list.append({'title': title,
                            'venue': venue,
                            'artists': artists,
                            'date': start_date})
    return events_list

def parse_date(date_string):
    fmt =  "%a, %d %b %Y %H:%M:%S"
    result = time.strptime(date_string, fmt)
    return datetime(result.tm_year, 
                    result.tm_mon, 
                    result.tm_mday, 
                    result.tm_hour, 
                    result.tm_min, 
                    result.tm_sec)

def get_xml():
    return open('response.xml', 'r').read()

def main():
    xml = get_xml()
    events = parse_xml(xml)
    print events

if __name__ == "__main__":
    main()
