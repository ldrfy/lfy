deps0 = 'python3 python3-requests'
if bt == 'qt'
    # opensuse
    # deps += ' python3-PyQt6'
    deps = deps0 + ' python3-pillow python3-pyqt6'
else
    deps = deps0 + ' python3-pillow python3-gobject libadwaita'
endif

conf_pkg_rpm = configuration_data()
foreach key : conf_pkg.keys()
    conf_pkg_rpm.set(key, conf_pkg.get(key))
endforeach
if bt == 'qt'
    deps = deps0 + ' python3-Pillow python3-PyQt6'
else
    deps = deps0 + ' python3-Pillow python3-gobject libadwaita typelib-1_0-Gtk-4_0'
endif
conf_pkg_rpm.set('DEPS', deps)
conf_pkg_rpm.set('BUILD_TYPE', bt)

configure_file(
    input: 'lfy.spec',
    output: 'lfy.spec',
    configuration: conf_pkg_rpm,
    install: false,
)


conf_pkg_rpm_suse = configuration_data()
foreach key : conf_pkg_rpm.keys()
    conf_pkg_rpm_suse.set(key, conf_pkg_rpm.get(key))
endforeach
conf_pkg_rpm_suse.set('DEPS', deps)
conf_pkg_rpm_suse.set('BUILD_TYPE', bt)

configure_file(
    input: 'lfy.spec',
    output: 'lfy-suse.spec',
    configuration: conf_pkg_rpm_suse,
    install: false,
)
