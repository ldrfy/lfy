project('lt',
          version: '0.1.0',
    meson_version: '>= 0.62.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
gnome = import('gnome')
python = import('python')

APPLICATION_ID = 'lt.ldr.cool'
PKGDATA_DIR = get_option('prefix') / get_option('datadir') / meson.project_name()
PROJECT_RDNN_NAME = 'lt.ldr.cool'
PACKAGE_URL = 'https://github.com/yuhldr/lt'
PACKAGE_URL_BUG = 'https://github.com/yuhldr/lt/issues'


moduledir = PKGDATA_DIR / 'lt'


py_installation = python.find_installation('python3')

PYTHON_DIR = py_installation.get_path('purelib')

conf = configuration_data()
conf.set('application_id', APPLICATION_ID)
conf.set('rdnn_name', PROJECT_RDNN_NAME)

conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', PKGDATA_DIR)
conf.set('pythondir', PYTHON_DIR)
conf.set('schemasdir', PKGDATA_DIR)


configure_file(
  input: 'lt.in',
  output: 'lt',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr--r--'
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


install_subdir(
    'lt_gtk',
    install_dir: py_installation.get_install_dir()
)

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)
