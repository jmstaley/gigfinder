import gobject
import location

class LocationUpdater:

    def __init__(self):
        self.lat = None
        self.long = None
        self.loop = gobject.MainLoop()
        self.fix_count = 0

        self.control = location.GPSDControl.get_default()
        self.control.set_properties(preferred_method=location.METHOD_USER_SELECTED,
                               preferred_interval=location.INTERVAL_DEFAULT)
        self.control.connect("error-verbose", self.on_error, self.loop)
        self.control.connect("gpsd-stopped", self.on_stop, self.loop)

        self.device = location.GPSDevice()
        self.device.connect("changed", self.on_changed, self.control)

    def update_location(self):
        """ Run the loop and update lat and long """
        self.reset()
        gobject.idle_add(self.start_location, self.control)
        self.loop.run()

    def on_error(self, control, error, data):
        """ Handle errors """
        print "location error: %d... quitting" % error
        data.quit()

    def on_changed(self, device, data):
        """ Set long and lat """
        if not device:
            return
        if device.fix:
            # once fix is found and long, lat available set long lat
            if device.fix[1] & location.GPS_DEVICE_LATLONG_SET:
                self.fix_count += 1
                if self.fix_count > 1:
                    self.lat, self.long = device.fix[4:6]
                    data.stop()

    def on_stop(self, control, data):
        """ Stop the location service """
        print "quitting"
        data.quit()

    def start_location(self, data):
        """ Start the location service """
        self.fix_count = 0
        data.start()
        return False

    def reset(self):
        """ Reset coordinates """
        self.lat = None
        self.long = None
        self.device.reset_last_known()

