project('gst-demo', 'c', 'cpp',
  default_options : [ 'buildtype=debug', 'cpp_std=c++17' ],
  version: '1.21.0'
)

gstreamer_full_dep = dependency('gstreamer-full-1.0', fallback: ['gstreamer-1.0'], required :true)

executable('demo', 'main.cpp', dependencies: [gstreamer_full_dep])
