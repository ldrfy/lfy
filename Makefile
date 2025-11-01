NAME=lfy
APP_ID=cool.ldr.${NAME}
TO_LANG=zh_CN
VERSION=0.2.0
PREFIX = "/usr/"
BASE_URL = https://github.com/ldrfy/${NAME}/releases/download/auto
BUILD_TYPE=gtk


clear:
	rm -rf build test
	mkdir -p dist
	rm -rf {HOME}/.local/share/glib-2.0/schemas/gschemas.compiled
	rm -rf {HOME}/.local/lib/lfy
	rm -rf /tmp/v${VERSION}.zip
	rm -rf /tmp/${NAME}-${VERSION}

build:
	meson setup build --prefix=${PREFIX} -Dbuild_type=${BUILD_TYPE}
	meson compile -C build
	meson test -C build
	# meson dist -C build --allow-dirty

install: build
	$(MAKE) build PREFIX=${HOME}/.local/
# 	安装位置与PREFIX不一致时使用DESTDIR
# 	DESTDIR=${HOME}/.local/ meson install -C build
	meson install -C build
	${HOME}/.local/bin/${NAME}


uninstall: install
	cd build && ninja uninstall

# Generate .pot file
update-pot:
	xgettext -d "${NAME}" \
			--output=./po/${NAME}.pot \
			--copyright-holder="yuhldr" \
			--package-name="${APP_ID}" \
			--msgid-bugs-address="yuhldr@gmail.com" \
			--add-comments=TRANSLATORS \
			--files-from=./po/POTFILES


po-init:
	msginit -i ./po/${NAME}.pot -o ./po/${TO_LANG}.po


update-po:
	msgmerge -U ./po/${TO_LANG}.po ./po/${NAME}.pot


.PHONY: build other update-pot update-po po-init test whl rename

FILE_NAME_ZIP = ${NAME}-${VERSION}
PATH_ZIP = test/zip/${FILE_NAME_ZIP}/
build_zip:
	mkdir -p ${PATH_ZIP}

	cp -r ${NAME} ${PATH_ZIP}
	cp -r data ${PATH_ZIP}
	cp -r pkg ${PATH_ZIP}
	cp -r po ${PATH_ZIP}
	cp -r meson.build ${PATH_ZIP}

	cp -r meson_options.txt ${PATH_ZIP}

	cd ${PATH_ZIP}/../ && \
	zip -r ${FILE_NAME_ZIP}.zip ${FILE_NAME_ZIP}


PATH_AUR = build/pkg/aur/
pkg_aur_:
	cp ${PATH_ZIP}/../${FILE_NAME_ZIP}.zip ${PATH_AUR}

	cd build/pkg/aur/ && \
	makepkg -sf

	cp ${PATH_AUR}/${NAME}-${VERSION}-1-any.pkg.tar.zst dist/


pkg_aur: clear build build_zip pkg_aur_
# sudo pacman -U dist/${NAME}-${VERSION}-1-any.pkg.tar.zst


PATH_FLATPAK = build/pkg/flatpak/
pkg_flatpak_:
	mkdir -p ${PATH_FLATPAK}
	cp ${PATH_ZIP}/../${FILE_NAME_ZIP}.zip ${PATH_FLATPAK}

	cd ${PATH_FLATPAK} && \
	unzip ${FILE_NAME_ZIP}.zip && \
	mv ${FILE_NAME_ZIP} ${NAME} && \
	flatpak-builder --repo=repo build-dir ${APP_ID}.yaml && \
	flatpak build-bundle repo ${APP_ID}.flatpak ${APP_ID}

	cp ${PATH_FLATPAK}/${APP_ID}.flatpak dist/${APP_ID}-${VERSION}.flatpak


pkg_flatpak: clear build build_zip pkg_flatpak_
# flatpak install --user dist/${APP_ID}-${VERSION}.flatpak


PATH_DEB = build/pkg/deb/

pkg_deb_:
	DESTDIR=../${PATH_DEB} meson install -C build

	cd "${PWD}/${PATH_DEB}/../" && \
	dpkg -b deb ./deb/${NAME}-${VERSION}-x86_64.deb

	cp ${PATH_DEB}/${NAME}-${VERSION}-x86_64.deb dist/

pkg_deb: clear build pkg_deb_


PATH_RPM = build/pkg/rpm/
pkg_rpm_:

	mkdir -p ${PWD}/${PATH_RPM}/SOURCES/${NAME}-${VERSION} && \
	cp ${PATH_ZIP}/../${FILE_NAME_ZIP}.zip ${PATH_RPM}/SOURCES/

	cd ${PATH_RPM} && \
	rpmbuild -bb ${PWD}/${PATH_RPM}/SPECS/${NAME}.spec \
		--define "_topdir ${PWD}/${PATH_RPM}/" \
		  --define "_enable_debug_packages 0" \
		  --define "debug_package %{nil}" \
		  --define "_debugsource_packages 0"

	cp ${PATH_RPM}/RPMS/x86_64/${NAME}-${VERSION}-1.x86_64.rpm dist/${NAME}-${VERSION}-1.x86_64.rpm

	rpmbuild -bb ${PWD}/${PATH_RPM}/SPECS/${NAME}-suse.spec \
		--define "_topdir ${PWD}/${PATH_RPM}/"\
		  --define "_enable_debug_packages 0" \
		  --define "debug_package %{nil}" \
		  --define "_debugsource_packages 0"

	cp ${PATH_RPM}/RPMS/x86_64/${NAME}-${VERSION}-1.x86_64.rpm dist/${NAME}-${VERSION}-1.x86_64-suse.rpm

pkg_rpm: clear build build_zip pkg_rpm_


pkg_all: clear build build_zip pkg_aur_ pkg_deb_ pkg_rpm_ pkg_flatpak_
	#cp dist/* ${HOME}/data/my/vmware/files



PATH_PIP = build/pkg/pip/
pkg_pip_:
	DESTDIR=../${PATH_PIP} meson install -C build

	cp README.md ${PATH_PIP}
	cp LICENSE ${PATH_PIP}

	cd ${PATH_PIP} && \
	mv usr/lib/${NAME} ./ && \
	mv usr/share/icons/hicolor/scalable/apps ./${NAME}/resources/ && \
	mv usr/share/locale ./${NAME}/resources/ && \
	python -m build

	cp ${PATH_PIP}/dist/${NAME}-${VERSION}-py3-none-any.whl dist/

pkg_pip: clear build pkg_pip_


release:
	make BUILD_TYPE=qt pkg_all
	make BUILD_TYPE=gtk pkg_all

	make BUILD_TYPE=qt pkg_pip

GTK_FILES = \
    ${NAME}-$(VERSION)-1-any-gtk.pkg.tar.zst \
    ${NAME}-$(VERSION)-x86_64-gtk.deb \
    ${NAME}-$(VERSION)-1.x86_64-gtk.rpm \
    ${NAME}-$(VERSION)-1.x86_64-gtk-suse.rpm \
    ${APP_ID}-$(VERSION)-gtk.flatpak

QT_FILES = \
    ${NAME}-$(VERSION)-1-any-qt.pkg.tar.zst \
    ${NAME}-$(VERSION)-x86_64-qt.deb \
    ${NAME}-$(VERSION)-1.x86_64-qt.rpm \
    ${NAME}-$(VERSION)-1.x86_64-qt-suse.rpm \
    x \
	${NAME}-$(VERSION)-py3-none-any.whl

generate:
	@echo -n "gtk|"
	@for f in $(GTK_FILES); do \
		echo -n "[$$f]($(BASE_URL)/$$f)|"; \
	done
	@echo
	@echo -n "qt|"
	@for f in $(QT_FILES); do \
		if [ "$$f" = "x" ]; then \
			echo -n "|"; \
		else \
			echo -n "[$$f]($(BASE_URL)/$$f)|"; \
		fi \
	done
	@echo
