import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
from gi.repository import Gst, GLib, GObject, GstBase

Gst.init(None)

FORMATS = "{RGBx,BGRx,xRGB,xBGR,RGBA,BGRA,ARGB,ABGR,RGB,BGR}"

# class GstGaussianBlur(Gst.Element):
#     GST_PLUGIN_NAME = 'gaussianblur'
#
#     __gstmetadata__ = ("gaussianblur",
#                        "Filter",
#                        "Apply Gaussian Blur to Buffer",
#                        "Taras Lishchenko <taras at lifestyletransfer dot com>")
#
#     __gsttemplates__ = (Gst.PadTemplate.new("src",
#                                             Gst.PadDirection.SRC,
#                                             Gst.PadPresence.ALWAYS,
#                                             Gst.Caps.from_string(f"video/x-raw,format={FORMATS}")),
#                         Gst.PadTemplate.new("sink",
#                                             Gst.PadDirection.SINK,
#                                             Gst.PadPresence.ALWAYS,
#                                             Gst.Caps.from_string(f"video/x-raw,format={FORMATS}")))
#
#     __gproperties__ = {
#         "kernel": (GObject.TYPE_INT64, "Kernel Size", "Gaussian Kernel Size", 1, GLib.MAXINT, 3, GObject.ParamFlags.READWRITE),
#         "sigmaX": (GObject.TYPE_FLOAT, "Standard deviation in X", "Gaussian kernel standard deviation in X direction", 1.0, GLib.MAXFLOAT, 1.0, GObject.ParamFlags.READWRITE),
#         "sigmaY": (GObject.TYPE_FLOAT, "Standard deviation in Y", "Gaussian kernel standard deviation in Y direction", 1.0, GLib.MAXFLOAT, 1.0, GObject.ParamFlags.READWRITE),
#     }
#
#     def __init__(self):
#         super(GstGaussianBlur, self).__init__()
#
#         self.kernel_size = 3
#         self.sigma_x = 1.0
#         self.sigma_y = 1.0
#
#     def do_get_property(self, prop):
#         return getattr(self, prop.name)
#
#     def do_set_property(self, prop, value):
#         setattr(self, prop.name, value)
#
#     def do_transform_ip(self, buffer):
#         try:
#             image = gst_buffer_with_caps_to_ndarray(buffer, self.get_static_pad("sink").get_current_caps())
#             image[:] = gaussian_blur(image, self.kernel_size, sigma=(self.sigma_x, self.sigma_y))
#         except Exception as e:
#             print(f"Error in do_transform_ip: {e}")


class CustomProcessor(GstBase.BaseTransform):
    GST_PLUGIN_NAME = 'gaussianblur'

    __gstmetadata__ = ("gaussianblur",  # Name
                       "Filter",   # Transform
                       "Apply Gaussian Blur to Buffer",  # Description
                       "Taras Lishchenko <taras at lifestyletransfer dot com>")  # Author

    # __gsttemplates__ = (
    #     Gst.PadTemplate.new("sink", Gst.PadDirection.SINK, Gst.PadPresence.ALWAYS, Gst.Caps.new_any()),
    #     Gst.PadTemplate.new("src", Gst.PadDirection.SRC, Gst.PadPresence.ALWAYS, Gst.Caps.new_any())
    # )

    __gsttemplates__ = (Gst.PadTemplate.new("src",
                                            Gst.PadDirection.SRC,
                                            Gst.PadPresence.ALWAYS,
                                            # Set to RGB format
                                            Gst.Caps.from_string(f"video/x-raw")
                                            ),
                        Gst.PadTemplate.new("sink",
                                            Gst.PadDirection.SINK,
                                            Gst.PadPresence.ALWAYS,
                                            Gst.Caps.from_string(f"video/x-vp8")
                                            ))

    def __init__(self):
        super(CustomProcessor, self).__init__()
        self.sinkpad = Gst.Pad.new_from_template(self.__gsttemplates__[0], "sink")
        self.sinkpad.set_chain_function(self.chainfunc)

    # Set specific caps on the sink pad
        self.sinkpad.set_caps(Gst.Caps.from_string("video/x-raw, format=(string)I420"))

        self.add_pad(self.sinkpad)
        self.srcpad = Gst.Pad.new_from_template(self.__gsttemplates__[1], "src")
        self.add_pad(self.srcpad)

    def link(self, sinkpad):
        print("sink pad", sinkpad)

        return super().link(sinkpad)


    def chainfunc(self, pad, parent, buffer):
        try:
            print("Input caps:", pad.query_caps(None).to_string())
        finally:
            pass

GObject.type_register(CustomProcessor)
__gstelementfactory__ = (CustomProcessor.GST_PLUGIN_NAME, Gst.Rank.NONE, CustomProcessor)

def on_bus_message(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        print("End of stream")
        loop.quit()
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"Error: {err}, Debug: {debug}")
        loop.quit()

def main():
    pipe = Gst.Pipeline.new('dynamic')
    
    src = Gst.ElementFactory.make("videotestsrc")
    if src is None:
        print("unable to get videotestsrc")
        exit(1)

    sink = Gst.ElementFactory.make("gaussianblur")
    if sink is None:
        print("unable to get appsink")
        exit(1)

    pipe.add(src)
    pipe.add(sink)

    src.link(sink)

    bus = pipe.get_bus()
    loop = GLib.MainLoop()

    if bus is None:
        print("unable to get bus")
        exit(1)

    bus.add_signal_watch() 
    bus.connect("message", on_bus_message, loop)

    pipe.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    finally:
        pipe.set_state(Gst.State.NULL)

if __name__ == "__main__":
    main()

