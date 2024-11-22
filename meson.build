project(
    'lfy',
    version: '0.0.7',
    meson_version: '>= 0.62.0',
    default_options: [
        'warning_level=2',
        'werror=false',
    ],
)

bt = get_option('build_type')

if bt == 'gtk'

    gnome = import('gnome')

    gnome.post_install(
        glib_compile_schemas: true,
        gtk_update_icon_cache: true,
        update_desktop_database: true,
    )
endif

i18n = import('i18n')
python = import('python')

APP_ID = 'cool.ldr.' + meson.project_name()
# PKGLIB_DIR = join_paths(get_option('prefix'), get_option('libdir'), APPLICATION_ID)
SCHEMAS_DIR = join_paths(get_option('prefix'), get_option('datadir'))
PKGDATA_DIR = join_paths(SCHEMAS_DIR, APP_ID)
LOCALE_DIR = join_paths(SCHEMAS_DIR, 'locale')

PACKAGE_URL = 'https://github.com/ldrfy/lfy'
PACKAGE_URL_BUG = 'https://github.com/ldrfy/lfy/issues'

py_installation = python.find_installation('python3')
# /usr/lib/python3.11/site-packages
PYTHON_DIR = join_paths(get_option('prefix'), 'lib')

conf = configuration_data()
conf.set('LOCAL_BUILD', 'False')

conf.set('APP_ID', APP_ID)
conf.set('APP_NAME', meson.project_name())
conf.set('VERSION', meson.project_version())
conf.set('PYTHON', py_installation.full_path())

conf.set('SCHEMAS_DIR', SCHEMAS_DIR)
conf.set('LOCALE_DIR', LOCALE_DIR)
conf.set('PKGDATA_DIR', PKGDATA_DIR)
conf.set('PYTHON_DIR', PYTHON_DIR)

conf.set('PACKAGE_URL', PACKAGE_URL)
conf.set('PACKAGE_URL_BUG', PACKAGE_URL_BUG)

configure_file(
    input: 'define.py',
    output: '__init__.py',
    configuration: conf,
    install: true,
    install_dir: join_paths(PYTHON_DIR, meson.project_name()),
)

configure_file(
    input: meson.project_name() + '/' + bt + '/' + meson.project_name() + '.py',
    output: meson.project_name(),
    configuration: conf,
    install: true,
    install_dir: get_option('bindir'),
    install_mode: 'r-xr-xr-x',
)

subdir('data')
subdir('po')
subdir('pkg')

install_subdir(
    meson.project_name() + '/api',
    install_dir: join_paths(PYTHON_DIR, meson.project_name()),
)

install_subdir(
    meson.project_name() + '/utils',
    install_dir: join_paths(PYTHON_DIR, meson.project_name()),
)

install_subdir(
    meson.project_name() + '/' + bt,
    install_dir: join_paths(PYTHON_DIR, meson.project_name()),
)