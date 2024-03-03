"""
    Plugin blurs incoming buffer

    export GST_PLUGIN_PATH=$GST_PLUGIN_PATH:$PWD

    gst-launch-1.0 videotestsrc! gaussian_blur kernel=9 sigmaX = 5.0 sigmaY=5.0 ! videoconvert ! autovideosink
"""

import logging
import timeit
import traceback
from typing import Tuple
import time
import cv2
import numpy as np
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GLib', '2.0')
from gi.repository import Gst, GLib, GstBase, GObject
from gstreamer.utils import gst_buffer_with_caps_to_ndarray

