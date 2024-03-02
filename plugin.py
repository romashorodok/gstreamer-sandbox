import gi
import os
import platform
import sys

gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('GLib', '2.0')

from gi.repository import Gst, GObject, GLib, GstBase, GstVideo

def is_aarch64():
    return platform.uname()[4] == 'aarch64'


sys.path.append('/opt/nvidia/deepstream/deepstream-5.0/sources/python/bindings/' +
                ('jetson' if is_aarch64() else 'x86_64'))

Gst.init(None)

# resample_element = Gst.ElementFactory.make("audioresample", "audio-resample")
# src_element = Gst.ElementFactory.make("audiotestsrc", "audio-source")
# print(src_element)
# print(resample_element)

FIXED_CAPS: Gst.Caps = Gst.Caps.new_empty()

caps = Gst.Caps.from_string(
'video/x-raw,format={ (string)RGBA, (string)I420 },width=[1,2147483647],height=[1,2147483647],framerate=[ 0/1, 2147483647/1 ]'
)
if caps is not None:
    FIXED_CAPS.append(caps)

caps = Gst.Caps.from_string(
    'video/x-raw(memory:NVMM),format={ (string)RGBA, (string)NV12 },width=[1,2147483647],height=[1,2147483647],framerate=[ 0/1, 2147483647/1 ]'
)

if caps is not None:
    FIXED_CAPS.append(caps)

# FIXED_CAPS = Gst.Caps.from_string(
#     'video/x-raw,format={ (string)RGBA, (string)I420 },width=[1,2147483647],height=[1,2147483647],framerate=[ 0/1, 2147483647/1 ]')

# FIXED_CAPS.append(Gst.Caps.from_string(
#     'video/x-raw(memory:NVMM),format={ (string)RGBA, (string)NV12 },width=[1,2147483647],height=[1,2147483647],framerate=[ 0/1, 2147483647/1 ]'))

class GstPycustom(GstBase.BaseTransform):
    __gstmetadata__ = (
        'PyCustom',
        'Generic',
        'Custom python element',
        'Miguel Taylor <miguel.taylor@ridgerun.com>')

    __gsttemplates__ = (
        Gst.PadTemplate.new(
            "src",
            Gst.PadDirection.SRC,
            Gst.PadPresence.ALWAYS,
            FIXED_CAPS),
        Gst.PadTemplate.new(
            "sink",
            Gst.PadDirection.SINK,
            Gst.PadPresence.ALWAYS,
            FIXED_CAPS))

    __gproperties__ = {}

    def __init__(self):
        GstBase.BaseTransform.__init__(self)
        GstBase.BaseTransform.set_in_place(self, True)

    def do_transform_ip(self, buf):
        print("transform_ip")
        print(buf)
        # Gst.debug("transform_ip")
        # custom operation
        return Gst.FlowReturn.OK

GObject.type_register(GstPycustom)
__gstelementfactory__ = ("pycustom", Gst.Rank.NONE, GstPycustom)
