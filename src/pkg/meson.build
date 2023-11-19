conf_pip = configuration_data()
conf_pip.set('APP_ID', APP_ID)
conf_pip.set('APP_NAME', meson.project_name())
conf_pip.set('PACKAGE_URL', PACKAGE_URL)
conf_pip.set('VERSION', meson.project_version())

configure_file(
  input: 'setup.py',
  output: 'setup.py',
  configuration: conf_pip,
  install: false,
)

configure_file(
  input: 'PKGBUILD',
  output: 'PKGBUILD',
  configuration: conf_pip,
  install: false,
)
