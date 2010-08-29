import gobject
import location
import thread

ACCURACY = {'500': 50000,
            '1000': 100000,
            '1500': 150000,
            '2000': 200000}

class LocationUpdater:

    def __init__(self):
        self.lat = None
        self.long = None
        self.accuracy = ACCURACY['1000']

        self.control = location.GPSDControl.get_default()
        self.control.set_properties(preferred_method=location\
                                            .METHOD_USER_SELECTED,
                                    preferred_interval=location\
                                            .INTERVAL_DEFAULT)
        self.control.connect("error-verbose", self.on_error, self.control)
        self.control.connect("gpsd-stopped", self.stop, None)

        self.device = location.GPSDevice()
        self.device.connect("changed", self.on_changed, self.control)

    def set_accuracy(self, accuracy):
        self.accuracy = ACCURACY[accuracy]

    def update_location(self):
        """ Run the loop and update lat and long """
        self.reset()
        gobject.idle_add(self.start_location, self.control)

    def on_error(self, control, error, data):
        """ Handle errors """
        print "location error: %d... quitting" % error
        data.quit()

    def on_changed(self, device, data):
        """ Set long and lat """
        if not device:
            return
        if device.fix:
            # once fix is found and horizontal accuracy is 1km
            if location.GPS_DEVICE_LATLONG_SET:
                if device.fix[6] <= self.accuracy:
                    self.lat, self.long = device.fix[4:6]
                    data.stop()

    def stop(self, widget, data):
        """ Stop the location service """
        self.control.stop()

    def start_location(self, data):
        """ Start the location service """
        data.start()
        return False

    def reset(self):
        """ Reset coordinates """
        self.lat = None
        self.long = None
        self.device.reset_last_known()

