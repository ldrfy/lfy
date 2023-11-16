project('lfy',
          version: '0.1.0',
    meson_version: '>= 0.62.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
gnome = import('gnome')
python = import('python')

APP_ID = 'cool.ldr.' + meson.project_name()
PKGDATA_DIR = get_option('prefix') / get_option('datadir') / meson.project_name()
PACKAGE_URL = 'https://github.com/yuhldr/lfy'
PACKAGE_URL_BUG = 'https://github.com/yuhldr/lfy/issues'

py_installation = python.find_installation('python3')
PYTHON_DIR = py_installation.get_path('purelib')
PYTHON_LOCAL_DIR = py_installation.get_install_dir()


conf = configuration_data()
conf.set('APP_ID', APP_ID)
conf.set('APP_NAME', meson.project_name())
conf.set('VERSION', meson.project_version())
conf.set('LOCALE_DIR', get_option('prefix') / get_option('localedir'))
conf.set('PKGDATA_DIR', PKGDATA_DIR)
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('PYTHON_DIR', PYTHON_DIR)
conf.set('PYTHON_LOCAL_DIR', PYTHON_LOCAL_DIR)
conf.set('PACKAGE_URL', PACKAGE_URL)
conf.set('PACKAGE_URL_BUG', PACKAGE_URL_BUG)


configure_file(
  input: 'define.in',
  output: '__init__.py',
  configuration: conf,
  install: true,
  install_dir: join_paths(PYTHON_LOCAL_DIR, meson.project_name())
)


configure_file(
  input: meson.project_name() + '.in',
  output: meson.project_name(),
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)


# Dependencies
dependency('glib-2.0', version: '>= 2.67.1')
dependency('goa-1.0', version: '>= 3.35.90')
dependency('gobject-introspection-1.0', version: '>= 1.35.0')
dependency('gtk4', version: '>= 4.5.0')
dependency('libadwaita-1', version: '>= 1.2.alpha')
dependency('pygobject-3.0', version: '>= 3.36.1')

subdir('data')
subdir('po')
subdir('pkg')


install_subdir(
    meson.project_name(),
    install_dir: PYTHON_LOCAL_DIR
)

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)
