#include <gst/gst.h>
#include <glib.h>
#include <iostream>

int main(int argc, char *argv[]) {
  // Initialize GStreamer
  gst_init(&argc, &argv);

  // Get GStreamer version information
  guint major, minor, micro, nano;
  gst_version(&major, &minor, &micro, &nano);

  // Print the version information
  std::cout << "GStreamer version:" << " " <<  major << " " <<  minor << micro << nano
            << std::endl;

  GstElement *result = gst_element_factory_make("vp8enc", nullptr);

  std::cout << result << std::endl; 

  GstIterator *iter = gst_bin_iterate_elements(GST_BIN(result));
    GstElement *element;

    while (gst_iterator_next(iter, (gpointer)&element) == GST_ITERATOR_OK) {
        // Print information about each element

        printf("Element: %s, Factory: %s\n", elementName, elementFactory);

        // Additional information about the element can be printed or accessed as needed
        // e.g., gst_element_get_property, gst_element_query_caps, etc.

        g_object_unref(element);
    }

  return 0;
}
