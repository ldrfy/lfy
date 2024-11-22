deps = 'python3 python3-requests'
if bt == 'qt'
    # opensuse
    # deps += ' python3-PyQt6'
    deps += ' python3-pyqt6'
else
    deps += ' python3-gobject libadwaita'
endif

conf_pkg_rpm = configuration_data()
foreach key : conf_pkg.keys()
    conf_pkg_rpm.set(key, conf_pkg.get(key))
endforeach
conf_pkg_rpm.set('DEPS', deps)
conf_pkg_rpm.set('BUILD_TYPE', bt)

configure_file(
    input: 'lfy.spec',
    output: 'lfy.spec',
    configuration: conf_pkg_rpm,
    install: false,
)