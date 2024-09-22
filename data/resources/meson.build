
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
