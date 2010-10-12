import gtk
import hildon

class GigfinderUI:
    def __init__(self, controller):
        self.controller = controller
        self.win = hildon.StackableWindow()
        self.app_title = "Gig Finder"

        menu = self.create_menu()

        self.win.set_title(self.app_title)
        self.win.connect("destroy", self.controller.quit, None)
        self.win.set_app_menu(menu)

        button_box = gtk.VBox()
    	date_button = hildon.DateButton(gtk.HILDON_SIZE_AUTO,
	                                hildon.BUTTON_ARRANGEMENT_VERTICAL)
        date_button.set_title('Select date')
        date_button.connect('value-changed',
		            	    self.controller.set_date,
            			    None)

        gps_toggle = hildon.CheckButton(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT)
        gps_toggle.set_label('Use GPS')
        gps_toggle.connect('toggled', self.toggle_gps)

        gps_accuracy = hildon.TouchSelector(text=True)
        for accuracy in ['500', '1000', '1500', '2000']:
            gps_accuracy.append_text(accuracy)
        gps_accuracy.set_column_selection_mode(hildon.TOUCH_SELECTOR_SELECTION_MODE_SINGLE)
        gps_accuracy.connect('changed', controller.set_accuracy)
        self.accuracy_picker = hildon.PickerButton(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT,
                                            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        self.accuracy_picker.set_title('Select GPS accuracy (meters)')
        self.accuracy_picker.set_selector(gps_accuracy)
        self.accuracy_picker.set_active(1)
        self.accuracy_picker.set_sensitive(False)

        location_selector = hildon.TouchSelector(text=True)
        for metro in controller.get_metros():
            location_selector.append_text(metro)
        location_selector.set_column_selection_mode(hildon.TOUCH_SELECTOR_SELECTION_MODE_SINGLE)
        location_selector.connect('changed', controller.set_location)
        self.picker_button = hildon.PickerButton(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT,
                                            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        self.picker_button.set_title('Select location')
        self.picker_button.set_selector(location_selector)

        update_button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT,
                                           hildon.BUTTON_ARRANGEMENT_VERTICAL)
        update_button.set_label('Find Gigs')
        update_button.connect('clicked',
                              self.controller.update,
                              None)
        
        button_box.pack_start(date_button, expand=False, fill=True, padding=5)
        button_box.pack_start(gps_toggle, expand=False, fill=True, padding=5)
        button_box.pack_start(self.accuracy_picker, expand=False, fill=True, padding=5)
        button_box.pack_start(self.picker_button, expand=False, fill=True, padding=5)
        button_box.pack_start(update_button, expand=False, fill=True, padding=5)
        
        self.win.add(button_box)
        self.win.show_all()

    def about(self, widget, data):
        """ Show about dialog """
        dialog = gtk.AboutDialog()
        dialog.set_name('Gig Finder')
        dialog.set_version(self.controller.version)
        dialog.set_authors(self.controller.authors)
        dialog.set_comments('Display gigs close by.\nUsing the http://www.last.fm api.')
        dialog.set_license('Distributed under the MIT license.\nhttp://www.opensource.org/licenses/mit-license.php')
        dialog.set_copyright(self.controller.copyright)
        dialog.show_all()

    def show_message(self, message):
        """ Set window progress indicator and show message """
        hildon.hildon_gtk_window_set_progress_indicator(self.win, 1)
        self.banner = hildon.hildon_banner_show_information(self.win,
                                                            '', 
                                                            message)

    def hide_message(self):
        """ Hide banner and set progress indicator """
        self.banner.hide()
        hildon.hildon_gtk_window_set_progress_indicator(self.win, 0)

    def show_events(self, events, location):
        """ Sort events, set new window title and add events to table """
        win = hildon.StackableWindow()
        win.set_title(self.app_title)

        if events:
            self.add_button_area(win)
            win.set_title('%s (%s)' % (self.app_title, len(events)))
            self.add_events(events, location)
        else:
            label = gtk.Label('No events available')
            vbox = gtk.VBox(False, 0)
            vbox.pack_start(label, True, True, 0)
            vbox.show_all()
            win.add(vbox)
        win.show_all()

    def create_menu(self):
        """ Build application menu """
        update_button = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
        update_button.set_label('Update')
        update_button.connect('clicked',
                              self.controller.update,
                              None)

        about_button = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
        about_button.set_label('About')
        about_button.connect('clicked',
                             self.about,
                             None)
	
    	date_button = hildon.DateButton(gtk.HILDON_SIZE_AUTO,
	                                hildon.BUTTON_ARRANGEMENT_VERTICAL)
        date_button.set_title('Select date')
        date_button.connect('value-changed',
		            	    self.controller.set_date,
            			    None)

        menu = hildon.AppMenu()
        menu.append(about_button)
        menu.show_all()
        return menu

    def show_details(self, widget, data):
        """ Open new window showing gig details """
        win = hildon.StackableWindow()
        win.set_title(data.title)

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
        buffer.insert(end, '%s\n' % data.title)
        buffer.insert(end, 'Artists: %s\n' % data.artists)
        buffer.insert(end, 'Venue: %s\n' % data.venue_name)
        buffer.insert(end, '%s\n' % data.address)
        buffer.insert(end, 'When: %s\n' % data.start_date.strftime('%H:%M %d/%m/%Y'))
        buffer.insert(end, '\n')
        scroll.add_with_viewport(view)

        win.show_all()

    def add_button_area(self, win):
        self.box = gtk.VBox(True,0)
        self.pannable_area = hildon.PannableArea()
        self.pannable_area.add_with_viewport(self.box)
        self.pannable_area.show_all()
        win.add(self.pannable_area)
        
    def add_events(self, events, location):
        """ Add a table of buttons """
        for event in events:
            button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_THUMB_HEIGHT, 
                                   hildon.BUTTON_ARRANGEMENT_VERTICAL)
	    button_text = event.title
	    if self.controller.gps_search:
                button_text += 'distance: %0.02f km' % event.get_distance_from(location.long, location.lat)
            button.set_text(button_text, '')
            button.connect("clicked", self.show_details, event)
            self.box.pack_start(button, fill=False)
        self.box.show_all()
	
    def toggle_gps(self, gps_toggle):
        if gps_toggle.get_active():
            self.picker_button.set_sensitive(False)
            self.accuracy_picker.set_sensitive(True)
        else:
            self.picker_button.set_sensitive(True)
            self.accuracy_picker.set_sensitive(False)
	self.controller.toggle_gps()
