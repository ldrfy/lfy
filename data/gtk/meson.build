
# Dependencies
dependency('glib-2.0', version: '>= 2.67.1')
dependency('gobject-introspection-1.0', version: '>= 1.35.0')
dependency('gtk4', version: '>= 4.5.0')
dependency('libadwaita-1', version: '>= 1.4')
dependency('pygobject-3.0', version: '>= 3.36.1')


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



# Merging the translations with the appdata file
appdata_conf = configuration_data()
appdata_conf.set('APP_ID', APP_ID)
appdata_conf.set('APP_NAME', meson.project_name())
appdata_conf.set('PACKAGE_URL', PACKAGE_URL)
appdata_conf.set('PACKAGE_URL_BUG', PACKAGE_URL_BUG)
appdata = i18n.merge_file(
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



# Compiling the resources
# about_dialog is defined in data/ui/meson.build to generate the output file in that directory
gnome.compile_resources(
  APP_ID,
  APP_ID + '.gresource.xml',
  gresource_bundle: true,
  source_dir: meson.current_build_dir(),
  install_dir: PKGDATA_DIR,
  dependencies: [appdata],
  install: true
)
