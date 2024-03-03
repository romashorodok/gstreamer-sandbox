from typing import override
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
from gi.repository import Gst, GstBase, GObject, GLib
from gstreamer.utils import gst_buffer_with_caps_to_ndarray 

import numpy as np
import logging
import logging
from typing import Tuple
import cv2

Gst.init(None)

DEFAULT_KERNEL_SIZE = 3
DEFAULT_SIGMA_X = 1000
DEFAULT_SIGMA_Y = 1000

def gaussian_blur(img: np.ndarray, kernel_size: int = 3, sigma: Tuple[int, int] = (1, 1)) -> np.ndarray:
    """ Blurs image
    :param img: [height, width, channels >= 3]
    :param kernel_size:
    :param sigma: (int, int)
    """
    sigmaX, sigmaY = sigma
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), sigmaX=sigmaX, sigmaY=sigmaY)



class CustomProcessor(GstBase.BaseTransform):
    GST_PLUGIN_NAME = 'customprocessor'

    __gstmetadata__ = ("customprocessor",
                       "Transform",
                       "Custom Sample Processor",
                       "Author Name")

    __gsttemplates__ = (Gst.PadTemplate.new("src",
                                            Gst.PadDirection.SRC,
                                            Gst.PadPresence.ALWAYS,
                                            # Set to RGB format
                                            Gst.Caps.from_string(f"video/x-raw")),
                        Gst.PadTemplate.new("sink",
                                            Gst.PadDirection.SINK,
                                            Gst.PadPresence.ALWAYS,
                                            # Set to RGB format
                                            Gst.Caps.from_string(f"video/x-raw")))

    def __init__(self):
        super(CustomProcessor, self).__init__()

    @override
    def do_transform_ip(self, buf: Gst.Buffer) -> Gst.FlowReturn:
    # def (self, inbuf: Gst.Buffer, outbuf: Gst.Buffer) -> Gst.FlowReturn:
        try:
            frame = gst_buffer_with_caps_to_ndarray(buf, self.sinkpad.get_current_caps())

            frame[:] = gaussian_blur(frame, DEFAULT_KERNEL_SIZE, sigma=(
                DEFAULT_SIGMA_X,
                DEFAULT_SIGMA_Y,
            )).squeeze()

            # out = np.random.random((460800))

            # pass
            # outbuf =  Gst.Buffer.new_wrapped(out.tobytes())
            
        except Exception as e:
            logging.error(e)

        return Gst.FlowReturn.OK


    # def do_transform_ip(self, buf: Gst.Buffer) -> Gst.FlowReturn:
    #     try:
            # data = np.frombuffer(buf.extract_dup(0, buf.get_size()), dtype=np.uint8)

            # Invert colors (simple example)
            # inverted_data = 255 - data

            # Create a new buffer from the modified data
            # modified_buffer = Gst.Buffer.new_wrapped(inverted_data.tobytes())

        # except Exception as e:
        #     logging.error(e)
        #
        # return Gst.FlowReturn.OK

GObject.type_register(CustomProcessor)
__gstelementfactory__ = (CustomProcessor.GST_PLUGIN_NAME, Gst.Rank.NONE, CustomProcessor)

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
    src.set_property("location", "output.mkv")

    demux = Gst.ElementFactory.make("matroskademux")
    queue = Gst.ElementFactory.make("queue")
    queueAfter = Gst.ElementFactory.make("queue")

    vp8dec = Gst.ElementFactory.make("vp8dec")

    
    # src = Gst.ElementFactory.make("videotestsrc")

    custom_processor = CustomProcessor()

    # videosink = Gst.ElementFactory.make('appsink')
    vp8enc = Gst.ElementFactory.make("vp8enc")
    # vp8enc.set_property("profile", "1")

    # if None in [src, demux, queue, vp8dec, custom_processor, videosink]:
    #     print("Failed to create elements")
    #     exit(1)

    videosink = Gst.ElementFactory.make('appsink')
    videosink.set_property("emit-signals", True)
    videosink.connect('new-sample', on_new_sample_inner)

    mux = Gst.ElementFactory.make("webmmux")
    mux.set_property("streamable", True)  # Set to True for live streaming
    filesink = Gst.ElementFactory.make("filesink")
    filesink.set_property("location", "result.webm")

    pipe.add(src) 
    pipe.add(queue)
    pipe.add(demux)
    pipe.add(queueAfter)
    pipe.add(vp8dec)
    pipe.add(custom_processor)
    pipe.add(vp8enc)
    pipe.add(mux)
    pipe.add(filesink)
    # pipe.add(videosink)

    # src.link(videosink)
    src.link(queue)
    queue.link(demux)
    demux.link(queueAfter)
    demux.connect("pad-added", pad_added_callback, queueAfter)
    queueAfter.link(vp8dec)
    vp8dec.link(custom_processor)
    custom_processor.link(vp8enc)
    vp8enc.link(mux)
    mux.link(filesink)
    # vp8enc.link(videosink)



    # src.link(demux)
    # demux.link(videosink)
    # demux.link(queue)
    # queue.link(videosink)
    # vp8dec.link(videosink)
    # vp8dec.link(custom_processor)
    # custom_processor.link(videosink)
    # custom_processor.link(videosink)
    # custom_processor.link(vp8enc)
    # vp8enc.link(videosink)

    # pipe.add(src)
    # pipe.add(demux)
    # pipe.add(queue)
    # pipe.add(vp8dec)
    # pipe.add(src)
    # pipe.add(custom_processor)
    # pipe.add(vp8enc)
    # pipe.add(videosink)

    # src.link(custom_processor)
    
    # demux.connect("pad-added", pad_added_callback, queue)
    # demux.link(queue)
    # queue.link(vp8dec)

    # Link your custom processor
    # vp8dec.link(custom_processor)

    # Link your custom processor's output to videosink
    # custom_processor.link(videosink)
    # custom_processor.link(vp8enc)

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

