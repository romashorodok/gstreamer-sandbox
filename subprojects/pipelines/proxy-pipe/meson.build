proxypipe_sources = [
  'proxy_pipe.cpp'
  ]
proxypipe_headers = [
  'proxy_pipe.h'
  ]

proxypipe_lib = static_library('proxypipe-@0@'.format(api_version), 
  proxypipe_sources + proxypipe_headers,
  include_directories: [pipelines_inc, proxypipe_inc],
  dependencies: [gstreamer_full_dep, gstreamer_base_dep, gstreamer_app_dep],
  )

proxypipe_dep = declare_dependency(link_with: proxypipe_lib,
  include_directories: [pipelines_inc, proxypipe_inc],
  dependencies: [gstreamer_full_dep, gstreamer_base_dep, gstreamer_app_dep],
  )

pkgconfig.generate(proxypipe_lib)
meson.override_dependency(proxypipe_lib.name(), proxypipe_dep)
