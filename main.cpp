#include <glib.h>
#include <gst/gst.h>
#include <iostream>

int main(int argc, char *argv[]) {
  // Initialize GStreamer
  gst_init(&argc, &argv);

  // Get GStreamer version information
  guint major, minor, micro, nano;
  gst_version(&major, &minor, &micro, &nano);

  // Print the version information
  std::cout << "GStreamer version:"
            << " " << major << " " << minor << micro << nano << std::endl;

  GstElement *result = gst_element_factory_make("vp8enc", nullptr);

  std::cout << result << std::endl;

  std::cout << GST_ELEMENT_NAME(result) << std::endl;

  return 0;
}
