deps0 = '"requests"'
if bt == 'qt'
    # opensuse
    # deps += ' python3-PyQt6'
    deps = deps0 + ' ,"pillow", "PyQt6"'
else
    deps = deps0 + ' ,"pillow", "PyGObject"'
endif

conf_pkg_pip = configuration_data()
foreach key : conf_pkg.keys()
    conf_pkg_pip.set(key, conf_pkg.get(key))
endforeach
conf_pkg_pip.set('DEPS', deps)
conf_pkg_pip.set('BUILD_TYPE', bt)

configure_file(
    input: 'pyproject.toml',
    output: 'pyproject.toml',
    configuration: conf_pkg_pip,
    install: false,
)
