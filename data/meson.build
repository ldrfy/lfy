
if bt == 'gtk'
    subdir('gtk')
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
    args: join_paths(meson.current_build_dir(), APP_ID + '.desktop')
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
