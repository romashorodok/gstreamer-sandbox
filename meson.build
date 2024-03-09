project('gst-demo', 'c', 'cpp',
  default_options : [ 'buildtype=debug', 'cpp_std=c++17' ],
  version: '1.21.0'
)

cc = meson.get_compiler('c')
stdcpp = cc.find_library('stdc++', required: true)

gstreamer_full_dep = dependency('gstreamer-full-1.0', fallback: 'gstreamer-1.0', required: true)

pipelines_proj = subproject('pipelines')
pipelines_lib = pipelines_proj.get_variable('pipelines_lib')

go = find_program('go')

server_cmd_path = join_paths(meson.current_source_dir(), 'cmd/server')

pkg_config_path = join_paths(meson.current_build_dir(), 'meson-uninstalled')

# // also may be used cgo LDFLAGS: -v -lstdc++
# ldflags = '-ldflags= @0@'.format('-lstdc++')

goenv = environment()
goenv.set('PKG_CONFIG_PATH', pkg_config_path)

go_mod = custom_target('golang',
  output: 'server',
  env: goenv,
  depends: [pipelines_lib],
  command: [go, 'build', '-a', '-o', '@OUTPUT@', server_cmd_path],
  install: true,
  install_dir: '',
  build_always_stale: true,
  )

# pipelines = dependency('pipelines-1.0', fallback: ['pipelines-1.0'], required: true)
# executable('demo', 'main.cpp', dependencies: [gstreamer_full_dep])
