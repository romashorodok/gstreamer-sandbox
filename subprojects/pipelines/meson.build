project('pipelines-1.0', 'cpp', default_options: ['cpp_std=c++17'])

pkgconfig = import('pkgconfig')

api_version = '1.0'

gstreamer_full_dep = dependency('gstreamer-full-1.0')
gstreamer_base_dep = dependency('gstreamer-base-1.0')
gstreamer_app_dep = dependency('gstreamer-app-1.0')

pipelines_inc = include_directories('.')
proxypipe_inc = include_directories('proxy-pipe')

subdir('proxy-pipe')

pipelines_sources = [
  'pipelines.cpp',
  ]
pipelines_headers = [
  'pipelines.h',
  ]

pipelines_lib = static_library('pipelines-@0@'.format(api_version), 
  pipelines_sources + pipelines_headers,
  dependencies: [gstreamer_full_dep],
  )

pipelines_dep = declare_dependency(link_with: pipelines_lib,
  include_directories: [pipelines_inc],
  dependencies: [gstreamer_full_dep],
  )

pkgconfig.generate(pipelines_lib) 
meson.override_dependency(pipelines_lib.name(), pipelines_dep)
