#include <gst/app/gstappsink.h>
#include <gst/app/gstappsrc.h>
#include <gst/gst.h>
#include <iostream>

#include "proxy_pipe.h"

BasePipeline::BasePipeline(const char *name) {
  this->pipeline = gst_pipeline_new(name);
  this->appsrc = gst_element_factory_make("appsrc", nullptr);
}

BasePipeline::~BasePipeline() {
  std::cout << "destroy from base pipe" << std::endl;
  gst_element_deinit(this->pipeline);
  gst_element_deinit(this->appsrc);
}

static GstFlowReturn on_sample_vp8_pipeline(GstAppSink *sink, gpointer data) {
  GstSample *sample = gst_app_sink_pull_sample(GST_APP_SINK(sink));
  if (sample) {
    // Get sample details
    GstCaps *caps = gst_sample_get_caps(sample);
    GstBuffer *buffer = gst_sample_get_buffer(sample);

    // Print sample details
    if (caps) {
      gchar *caps_str = gst_caps_to_string(caps);
      g_print("Received sample with caps: %s\n", caps_str);
      g_free(caps_str);
    }

    if (buffer) {
      g_print("Received sample with size: %lu\n", gst_buffer_get_size(buffer));
    }

    gst_sample_unref(sample);
  }

  return GST_FLOW_OK;
}

ProxyPipeRtpVP8::ProxyPipeRtpVP8(const char *name) : BasePipeline(name) {
  auto appsrc = this->getAppsrc();
  g_object_set(appsrc, "format", GST_FORMAT_TIME, "is-live", TRUE, nullptr);

  GstCaps *caps = gst_caps_new_simple(
      "application/x-rtp", "media", G_TYPE_STRING, "video", "payload",
      G_TYPE_INT, 96, "clock-rate", G_TYPE_INT, 90000, "encoding-name",
      G_TYPE_STRING, "VP8-DRAFT-IETF-01", nullptr);
  g_object_set(appsrc, "caps", caps, nullptr);
  gst_caps_unref(caps);

  this->rtpsession = gst_element_factory_make("rtpjitterbuffer", nullptr);
  this->queueRtpvp8depay = gst_element_factory_make("queue", nullptr);
  this->rtpvp8depay = gst_element_factory_make("rtpvp8depay", nullptr);
  this->queueVp8dec = gst_element_factory_make("queue", nullptr);
  this->vp8dec = gst_element_factory_make("vp8dec", nullptr);
  this->vp8enc = gst_element_factory_make("vp8enc", nullptr);
  this->webmmux = gst_element_factory_make("webmmux", nullptr);
  g_object_set(this->webmmux, "streamable", TRUE, nullptr);

  this->filesink = gst_element_factory_make("filesink", nullptr);
  g_object_set(this->filesink, "location", "proxy.webm", nullptr);

  // this->printsink = gst_element_factory_make("appsink", nullptr);

  if (!this->rtpsession || !this->queueRtpvp8depay || !this->rtpvp8depay ||
      !this->queueVp8dec || !this->vp8dec || !this->vp8enc ||
      !this->webmmux || !this->filesink) {
    g_printerr("Unable create the pipeline.\n");
    exit(1);
  }

  gst_bin_add_many(GST_BIN(this->getPipeline()), this->getAppsrc(),
                   this->rtpsession, this->queueRtpvp8depay, this->rtpvp8depay,
                   this->queueVp8dec, this->vp8dec, this->vp8enc, this->webmmux,
                   this->filesink,

                   // this->printsink,
                   nullptr);

  gst_element_link_many(this->getAppsrc(), this->rtpsession,
                        this->queueRtpvp8depay, this->rtpvp8depay,
                        this->queueVp8dec, this->vp8dec,

                        this->vp8enc, this->webmmux, this->filesink,

                        // this->printsink,
                        nullptr);

  // GstAppSinkCallbacks callbacks = {NULL, NULL, on_sample_vp8_pipeline, NULL};
  // gst_app_sink_set_callbacks(GST_APP_SINK(printsink), &callbacks, NULL,
  // NULL);
}

ProxyPipeRtpVP8::~ProxyPipeRtpVP8() {
  std::cout << "destory from rtp VP8 pipe" << std::endl;
  // gst_element_deinit(this->rtpsession);
  gst_element_deinit(this->queueRtpvp8depay);
  gst_element_deinit(this->rtpvp8depay);
  gst_element_deinit(this->queueVp8dec);
  gst_element_deinit(this->vp8dec);
  // gst_element_deinit(this->printsink);
}

extern "C" void start_proxy_pipe(void *pipe) {
  auto _pipe = dynamic_cast<BasePipeline *>(static_cast<BasePipeline *>(pipe));
  if (_pipe == nullptr)
    return;

  auto pipeline = _pipe->getPipeline();

  gst_element_set_state(pipeline, GST_STATE_PLAYING);
}

extern "C" void write_proxy_pipe(void *pipe, void *buffer, int len) {
  auto _pipe = dynamic_cast<BasePipeline *>(static_cast<BasePipeline *>(pipe));
  if (_pipe == nullptr)
    return;

  auto *src = _pipe->getAppsrc();

  // std::cout << "write_proxy_pipe" << std::endl;

  if (src != nullptr) {
    // Assuming buffer is the data you want to push

    // // std::cout << "gst_app_src_push_buffer" << std::endl;
    gpointer p = g_memdup2(buffer, len);
    GstBuffer *buffer = gst_buffer_new_wrapped(p, len);
    gst_app_src_push_buffer(GST_APP_SRC(src), buffer);
  }
}

extern "C" void delete_proxy_pipe(void *pipe) {
  auto _pipe = dynamic_cast<BasePipeline *>(static_cast<BasePipeline *>(pipe));
  if (_pipe == nullptr)
    return;
  delete _pipe;
}

extern "C" void *new_proxy_pipe_rtp_vp8(const char *name) {
  return new ProxyPipeRtpVP8(name);
}
