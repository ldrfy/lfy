deps = '"python-requests" "python-pillow"'
build_deps = '"meson"'
if bt == 'gtk'
    deps += ' "libadwaita" "gobject-introspection"'
else
    deps += ' "python-pyqt6" "qt6-svg"'
endif

conf_pkg_aur = configuration_data()
foreach key : conf_pkg.keys()
    conf_pkg_aur.set(key, conf_pkg.get(key))
endforeach
conf_pkg_aur.set('DEPS', deps)
conf_pkg_aur.set('BUILD_DEPS', build_deps)
conf_pkg_aur.set('BUILD_TYPE', bt)

configure_file(
    input: 'PKGBUILD',
    output: 'PKGBUILD',
    configuration: conf_pkg_aur,
    install: false,
)