import gi
gi.require_version('Gst', '1.0')
gi.require_version('GLib', '2.0')
from gi.repository import Gst, GLib

Gst.init(None)

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

def on_new_sample(appsink):
    sample = appsink.emit('pull-sample')
    print("Received new sample")

def main():
    # Create GStreamer pipeline
    pipe = Gst.Pipeline.new('dynamic')
    
    src = Gst.ElementFactory.make("filesrc", "file-source")
    src.set_property("location", "output.webm")  # Replace with your video file path
    if src is None:
        print("unable to get filesrc")
        exit(1)

    print(src)

    decoder = Gst.ElementFactory.make("vp8dec", "vp8-decoder")
    # if decoder is None:
    #     print("unable to get vp8dec")
    #     exit(1)

    encoder = Gst.ElementFactory.make("vp8enc", "vp8-encoder")
    # if encoder is None:
    #     print("unable to get vp8enc")
    #     exit(1)

    print(decoder)
    print(encoder)

    sink = Gst.ElementFactory.make('appsink')
    if sink is None:
        print("unable to get appsink")
        exit(1)

    def on_new_sample_inner(appsink):
        on_new_sample(appsink)
        return Gst.FlowReturn.OK

    sink.set_property("emit-signals", True)
    sink.connect('new-sample', on_new_sample_inner)

    pipe.add(src)
    pipe.add(decoder)
    pipe.add(encoder)
    pipe.add(sink)

    src.link(decoder)
    decoder.link(encoder)
    encoder.link(sink)

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

if __name__ == "__main__":
    main()

