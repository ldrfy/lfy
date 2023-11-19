subdir('resources')

# Install gsettings schema
gschema_conf = configuration_data()
gschema_conf.set('APP_ID', APP_ID)
configure_file(
  input: APP_ID + '.in.gschema.xml',
  output: APP_ID + '.gschema.xml',
  configuration: gschema_conf,
  install: true,
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif


# Merging the translations with the desktop file
desktop_conf = configuration_data()
desktop_conf.set('APP_ID', APP_ID)
desktop_conf.set('APP_NAME', meson.project_name())
desktop_conf.set('BIN_DIR', join_paths(get_option('prefix'), get_option('bindir')))

i18n.merge_file(
  type: 'desktop',
  input: configure_file(
    input: APP_ID + '.in.in.desktop',
    output: APP_ID + '.in.desktop',
    configuration: desktop_conf),
  output: APP_ID + '.desktop',
  po_dir: join_paths(meson.project_source_root(), 'po'),
  install: true,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'applications')
)

# Validating the desktop file
desktop_file_validate = find_program('desktop-file-validate', required:false)
if desktop_file_validate.found()
  test (
    'Validate desktop file',
    desktop_file_validate,
    args: join_paths(meson.current_build_dir (), APP_ID + '.desktop')
  )
endif

# Merging the translations with the appdata file
appdata_conf = configuration_data()
appdata_conf.set('appid', APP_ID)
appdata_conf.set('package_url', PACKAGE_URL)
appdata_conf.set('package_url_bug', PACKAGE_URL_BUG)
i18n.merge_file(
  input: configure_file(
    output: APP_ID + '.in.appdata.xml',
    input: APP_ID + '.in.appdata.xml',
    configuration: appdata_conf
  ),
  output: APP_ID + '.appdata.xml',
  po_dir: join_paths(meson.project_source_root(), 'po'),
  install: true,
  install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'metainfo')
)

# Validating the appdata file
appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test (
    'Validate appdata file',
    appstream_util,
    args: ['validate-relax', '--nonet', join_paths(meson.current_build_dir (), APP_ID + '.appdata.xml')]
  )
endif

# Installing the default icon
install_data(
    join_paths('resources/icons/hicolor/scalable/apps', APP_ID + '.svg'),
    install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'icons/hicolor/scalable/apps')
)

# Installing the symbolic icon
install_data(
    join_paths('resources/icons/hicolor/symbolic/apps', APP_ID + '-symbolic.svg'),
    install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'icons/hicolor/symbolic/apps'),
    rename: '@0@-symbolic.svg'.format(APP_ID)
)
