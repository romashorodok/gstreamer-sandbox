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
    sample: Gst.Sample = appsink.emit('pull-sample')
    print("Received new sample", sample)

def main():
    pipe = Gst.Pipeline.new('dynamic')

    # file = Gst.ElementFactory.make("filesrc", "file-source")
    # print(file)
    
    src = Gst.ElementFactory.make("videotestsrc")
    if src is None:
        print("unable to get videotestsrc")
        exit(1)

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

