blueprints = custom_target('blueprints',
  input: files(
    'provider-preferences.blp',
    'theme-switcher.blp',
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)


# Compiling the resources
# about_dialog is defined in data/ui/meson.build to generate the output file in that directory
gnome.compile_resources(
  APP_ID,
  APP_ID + '.gresource.xml',
  dependencies: blueprints,
  gresource_bundle: true,
  source_dir: meson.current_build_dir(),
  install_dir: PKGDATA_DIR,
  install: true
)
