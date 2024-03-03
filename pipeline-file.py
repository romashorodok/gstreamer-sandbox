import gi
gi.require_version('Gst', '1.0')
gi.require_version('GLib', '2.0')
gi.require_version('GstBase', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GLib, GObject, GstBase, GstVideo
import numpy as np

Gst.init(None)

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
    # Set specific caps on the sink pad
        # sinkpad.set_caps(Gst.Caps.from_string("video/x-raw, format=(string)I420"))
        return super().link(sinkpad)


    def chainfunc(self, pad, parent, buffer):
        try:
            print("Input caps:", pad.query_caps(None).to_string())
            return self.srcpad.push(buffer)

            # Extract buffer data as a numpy array
            # data = np.frombuffer(buffer.extract_dup(0, buffer.get_size()), dtype=np.uint8)
            #
            # # Invert colors (simple example)
            # inverted_data = 255 - data
            #
            # # Create a new buffer from the modified data
            # modified_buffer = Gst.Buffer.new_wrapped(inverted_data.tobytes())
            #
            # # Forward the modified buffer to the source pad
            # return self.srcpad.push(modified_buffer)
        finally:
            pass

        # except Exception as e:
        #     print(f"Error in chainfunc: {e}")
        #     return Gst.FlowReturn.ERROR

GObject.type_register(CustomProcessor)
__gstelementfactory__ = ("gaussianblur", Gst.Rank.NONE, CustomProcessor)

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

def on_new_sample(appsink, filesink):
    sample: Gst.Sample = appsink.emit('pull-sample')
    if sample is not None:
        buffer = sample.get_buffer()
        if buffer is not None:
            data = buffer.extract_dup(0, buffer.get_size())
            print(data)
            filesink.emit('write', data)
            print("Received and wrote a sample with size:", buffer.get_size())
            # Unreference the buffer explicitly to release its resources
            Gst.Buffer.unmap(data)
            Gst.Buffer.unref(data)
        else:
            print("Failed to get buffer from sample")
    else:
        print("Failed to get sample")

def on_new_sample_inner(appsink, filesink):
    on_new_sample(appsink, filesink)
    return Gst.FlowReturn.OK

def main():
    # Create GStreamer pipeline
    pipe = Gst.Pipeline.new('pipeline')
    # pipe = Gst.Pipeline.new('dynamic')
    
    src = Gst.ElementFactory.make("filesrc", "file-source")
    src.set_property("location", "output.webm")

    demux = Gst.ElementFactory.make("matroskademux")
    queue = Gst.ElementFactory.make("queue")

    vp8dec = Gst.ElementFactory.make("vp8dec")
    vp8enc = Gst.ElementFactory.make("vp8enc")
    mux = Gst.ElementFactory.make("webmmux")
    mux.set_property("streamable", True)  # Set to True for live streaming
    filesink = Gst.ElementFactory.make("filesink")
    filesink.set_property("location", "result.webm")

    custom_processor = Gst.ElementFactory.make("gaussianblur")  # Instantiate the GstPycustom element

    # custom_processor = CustomProcessor()  # Instantiate the GstPycustom element
    # custom_processor_sink_pad = custom_processor.get_static_pad("sink")
    # custom_processor_sink_pad.set_caps(Gst.Caps.from_string("video/x-raw, format=(string)I420"))

    # custom_processor_sink_pad = custom_processor.get_static_pad("sink")
    # custom_processor_sink_pad.set_caps(Gst.Caps.from_string("video/x-raw, format=(string)I420"))


    if None in [src, demux, queue, vp8dec, custom_processor,  vp8enc, mux, filesink]:
        print("Failed to create elements")
        exit(1)

    pipe.add(src)
    pipe.add(demux)
    pipe.add(queue)
    pipe.add(vp8dec)
    # pipe.add(custom_processor)  # Add your custom element here
    pipe.add(vp8enc)
    pipe.add(mux)
    pipe.add(filesink)

    src.link(demux)
    demux.connect("pad-added", pad_added_callback, queue)
    demux.link(queue)
    queue.link(vp8dec)

    vp8dec.link(vp8enc)

    # for temp in vp8dec.get_pad_template_list():
    #     print(temp.name)
    #     print(temp.caps)

    # vp8dec.link(custom_processor)
    # custom_processor.link(vp8enc)  # Link the source pad of custom_processor to vp8enc

    vp8enc.link(mux)
    mux.link(filesink)

    # vp8dec.link(custom_processor)

    # custom_processor.link(vp8enc)  # Link the source pad of custom_processor to vp8enc

    # vp8dec.link(vp8enc)  # Link to videoconvert
    # vp8enc.link(mux)
    # mux.link(filesink)
    #

    # src.link(demux)
    # demux.connect("pad-added", pad_added_callback, queue)
    # demux.link(queue)
    # queue.link(vp8dec)
    #
    # # Get the sink pad from the custom processor after adding it to the pipeline
    # custom_processor_sink_pad = custom_processor.get_static_pad("sink")
    #
    # # Link the vp8dec's source pad to the custom_processor's sink pad
    # vp8dec_src_pad = vp8dec.get_static_pad("src")
    # vp8dec_src_pad.link(custom_processor_sink_pad)
    #
    # custom_processor.link(vp8enc)  # Link the source pad of custom_processor to vp8enc
    #
    # vp8enc.link(mux)
    # mux.link(filesink)

    # Set up bus to handle messages
    bus = pipe.get_bus()
    loop = GLib.MainLoop()

    if bus is None:
        print("unable to get bus")
        exit(1)

    bus.add_signal_watch() 
    bus.connect("message", on_bus_message, loop)

    # Start the pipeline
    pipe.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    finally:
        # Stop the pipeline and cleanup
        pipe.set_state(Gst.State.NULL)

def pad_added_callback(demux, pad, queue):
    pad_caps = pad.query_caps(None)
    print("Caps:", pad_caps.to_string())
    if pad_caps and pad_caps.is_fixed() and "video" in pad_caps.to_string():
        linked_pad = queue.get_static_pad("sink")
        if not linked_pad.is_linked():
            pad.link(linked_pad)

if __name__ == "__main__":
    main()

