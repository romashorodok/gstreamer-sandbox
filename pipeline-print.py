import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GLib

Gst.init(None)

class CustomProcessor(Gst.Element):
    __gstmetadata__ = ("CustomProcessor",
                       "Generic",
                       "Custom Sample Processor",
                       "Author Name")

    __gsttemplates__ = (Gst.PadTemplate.new("sink",
                                            Gst.PadDirection.SINK,
                                            Gst.PadPresence.ALWAYS,
                                            Gst.Caps.new_any()),
                        Gst.PadTemplate.new("src",
                                            Gst.PadDirection.SRC,
                                            Gst.PadPresence.ALWAYS,
                                            Gst.Caps.new_any()))

    def __init__(self):
        super(CustomProcessor, self).__init__()

        # Use Gst.PadTemplate.new instead of get_static_pad_template
        self.sinkpad = Gst.Pad.new_from_template(self.__gsttemplates__[0], "sink")
        self.sinkpad.set_chain_function(self.chainfunc)
        self.add_pad(self.sinkpad)

        self.srcpad = Gst.Pad.new_from_template(self.__gsttemplates__[1], "src")
        self.add_pad(self.srcpad)

    def chainfunc(self, pad, parent, buffer):
        # Your custom processing logic goes here
        # Modify the buffer as needed

        # Example: Printing buffer size
        print("Processing buffer with size:", buffer.get_size())

        # Forward the modified buffer to the source pad
        return self.srcpad.push(buffer)

GObject.type_register(CustomProcessor)

def on_new_sample(appsink):
    sample: Gst.Sample = appsink.emit('pull-sample')
    if sample is not None:
        buffer = sample.get_buffer()
        if buffer is not None:
            print("Received new sample with size:", buffer.get_size())
        else:
            print("Failed to get buffer from sample")
    else:
        print("Failed to get sample")

def on_new_sample_inner(appsink):
    on_new_sample(appsink)
    return Gst.FlowReturn.OK

def pad_added_callback(demux, pad, queue):
    pad_caps = pad.query_caps(None)
    if pad_caps and pad_caps.is_fixed() and "video" in pad_caps.to_string():
        linked_pad = queue.get_static_pad("sink")
        if not linked_pad.is_linked():
            pad.link(linked_pad)

def on_bus_message(bus, message, loop):
    print(message.type)
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

    src = Gst.ElementFactory.make("filesrc", "file-source")
    src.set_property("location", "output.webm")

    demux = Gst.ElementFactory.make("matroskademux")
    queue = Gst.ElementFactory.make("queue")
    vp8dec = Gst.ElementFactory.make("vp8dec")

    custom_processor = CustomProcessor()

    videosink = Gst.ElementFactory.make('appsink')

    if None in [src, demux, queue, vp8dec, custom_processor, videosink]:
        print("Failed to create elements")
        exit(1)

    videosink.set_property("emit-signals", True)
    videosink.connect('new-sample', on_new_sample_inner)

    pipe.add(src)
    pipe.add(demux)
    pipe.add(queue)
    pipe.add(vp8dec)
    pipe.add(custom_processor)
    pipe.add(videosink)

    src.link(demux)
    
    demux.connect("pad-added", pad_added_callback, queue)
    demux.link(queue)
    queue.link(vp8dec)

    # Link your custom processor
    vp8dec.link(custom_processor)

    # Link your custom processor's output to videosink
    custom_processor.link(videosink)

    bus = pipe.get_bus()
    loop = GLib.MainLoop()

    if bus is None:
        print("Unable to get the bus")
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

