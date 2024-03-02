# import gi
# gi.require_version('Gst', '1.0')
# gi.require_version('GLib', '2.0')
# from gi.repository import Gst, GLib
#
# Gst.init(None)
#
# def on_bus_message(bus, message, loop):
#     t = message.type
#     if t == Gst.MessageType.EOS:
#         print("End of stream")
#         loop.quit()
#     elif t == Gst.MessageType.ERROR:
#         err, debug = message.parse_error()
#         print(f"Error: {err}, Debug: {debug}")
#         loop.quit()
#
# def main():
#     # Create GStreamer pipeline
#     # pipeline_str = "videotestsrc"
#     # pipeline = Gst.parse_launch(pipeline_str)
#     # print(pipeline)
#
#     pipe = Gst.Pipeline.new('dynamic')
#     
#     src = Gst.ElementFactory.make("videotestsrc")
#     if src is None:
#         print("unable get videotestsrc")
#         exit(1)
#
#     sink = Gst.ElementFactory.make('autovideosink')
#     if sink is None:
#         print("uanble get autovideosink")
#         exit(1)
#
#     pipe.add(src)
#     pipe.add(sink)
#
#     src.link(sink)
#
#
#
#     # Set up bus to handle messages
#     bus = pipe.get_bus()
#     print(bus)
#     loop = GLib.MainLoop()
#
#     if bus is None:
#         print("unable get bus")
#         exit(1)
#
#     bus.add_signal_watch() 
#     bus.connect("message", on_bus_message, loop)
#     print(bus)
#
#     # Start the pipeline
#     pipeline.set_state(Gst.State.PLAYING)
#
#     try:
#         loop.run()
#     except KeyboardInterrupt:
#         pass
#     finally:
#         # Stop the pipeline and cleanup
#         pipeline.set_state(Gst.State.NULL)
#
# if __name__ == "__main__":
#     main()
#

#!/usr/bin/env python3
# Demonstration of using compositor and the samples-selected
# signal to do frame-by-frame updates and animation by
# udpating compositor pad properties and the GstVideoConverter
# config.
#
# Supply a URI argument to use a video file in the example,
# or omit it to just animate a videotestsrc.
import gi
import math
import sys

gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
from gi.repository import GLib, GObject, Gst, GstVideo


def bus_call(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        sys.stdout.write("End-of-stream\n")
        loop.quit()
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write("Error: %s: %s\n" % (err, debug))
        loop.quit()
    return True

if __name__ == "__main__":
    Gst.init(sys.argv)

    # pipeline = Gst.ElementFactory.make('pipeline', None)
    pipe = Gst.Pipeline.new('dynamic')
    if pipe is None:
        print("pipeline not found")
        exit(1)

    conv = Gst.ElementFactory.make("videoconvert", None)
    if conv is None:
        print("videoconverter not found")
        exit(1)
    sink = Gst.ElementFactory.make("autovideosink", None)
    if sink is None:
        print("autovideosink not found")
        exit(1)

    pipe.add(conv)
    pipe.add(sink)

    succes_link = Gst.Element.link(conv, sink)
    if not succes_link:
        print("unable link")
        exit(1)

    # bgsource = Gst.parse_bin_from_description("videotestsrc pattern=circular ! capsfilter name=cf", False)

    # cfsrc = bgsource.get_by_name("cf")
    # caps = Gst.Caps.from_string("video/x-raw,width=320,height=180,framerate=1/1,format=RGB")
    # cfsrc.set_property("caps", caps)
    # src = cfsrc.get_static_pad("src")
    # bgsource.add_pad(Gst.GhostPad.new("src", src))

    # pipeline.add(bgsource)
    # bgsource.link(compositor)

    # pad = compositor.get_static_pad("sink_0")
    # pad.set_property("width", 1920)
    # pad.set_property("height", 1080)

    source = Gst.parse_bin_from_description("videotestsrc", False)
    # cfsrc = source.get_by_name("cf")
    # caps = Gst.Caps.from_string("video/x-raw,width=320,height=240,framerate=30/1,format=I420")
    # cfsrc.set_property("caps", caps)

    # src = cfsrc.get_static_pad("src")
    # source.add_pad(Gst.GhostPad.new("src", src))

    pipe.add(source)

    pipe.set_state(Gst.State.PLAYING)

    bus = pipe.get_bus()
    bus.add_signal_watch()

    loop = GLib.MainLoop()
    bus.connect("message", bus_call, loop)
    loop.run()

    pipe.set_state(Gst.State.NULL)
    pipe.get_state(Gst.CLOCK_TIME_NONE)

