from xml.dom.minidom import parseString
from datetime import datetime, date
import time
import gtk
import hildon

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
    # TODO: Add code to retrieve location and data from lastfm
    return open('response.xml', 'r').read()

def create_table(events):
    table = gtk.Table(columns=1)
    table.set_row_spacings(10)
    table.set_col_spacings(10)

    table.show()
    pos = 0
    for event in events:
        button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, 
                               hildon.BUTTON_ARRANGEMENT_VERTICAL)
        button.set_text(event['title'], "")
        button.connect("clicked", show_details, event)
        table.attach(button, 0, 1, pos, pos+1)
        pos += 1
    return table

def show_details(widget, data):
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
    buffer.insert(end, 'When: %s\n' % data['date'].strftime('%H:%M'))
    buffer.insert(end, '\n')
    scroll.add_with_viewport(view)

    win.show_all()

def main():
    program = hildon.Program.get_instance()
    win = hildon.StackableWindow()
    win.set_title('Gig Finder')
    win.connect("destroy", gtk.main_quit, None)

    pannable_area = hildon.PannableArea()
   
    xml = get_xml()
    events = parse_xml(xml)

    table = create_table(events)
    pannable_area.add_with_viewport(table)

    win.add(pannable_area)
    win.show_all()
    gtk.main()

if __name__ == "__main__":
    main()
