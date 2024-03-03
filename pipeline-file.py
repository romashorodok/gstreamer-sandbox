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
    pipe = Gst.Pipeline.new('dynamic')
    
    src = Gst.ElementFactory.make("filesrc", "file-source")
    src.set_property("location", "output.webm")

    demux = Gst.ElementFactory.make("matroskademux")
    queue = Gst.ElementFactory.make("queue")

    vp8dec = Gst.ElementFactory.make("vp8dec")
    vp8enc = Gst.ElementFactory.make("vp8enc")
    mux = Gst.ElementFactory.make("webmmux")
    filesink = Gst.ElementFactory.make("filesink")
    filesink.set_property("location", "result.webm")

    if None in [src, demux, queue, vp8dec, vp8enc, mux, filesink]:
        print("Failed to create elements")
        exit(1)

    pipe.add(src)
    pipe.add(demux)
    pipe.add(queue)
    pipe.add(vp8dec)
    pipe.add(vp8enc)
    pipe.add(mux)
    pipe.add(filesink)

    src.link(demux)
    demux.connect("pad-added", pad_added_callback, queue)
    demux.link(queue)
    queue.link(vp8dec)
    vp8dec.link(vp8enc)
    vp8enc.link(mux)
    mux.link(filesink)

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
    if pad_caps and pad_caps.is_fixed() and "video" in pad_caps.to_string():
        linked_pad = queue.get_static_pad("sink")
        if not linked_pad.is_linked():
            pad.link(linked_pad)

if __name__ == "__main__":
    main()

