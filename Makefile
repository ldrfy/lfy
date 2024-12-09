TO_LANG=zh_CN
VERSION=0.0.7
BUILD_TYPE=gtk
DISK = ../../../dist/
BUILD_PKG=build/pkg
DESTDIR = "/"
# PREFIX = "${HOME}/.local/"
PREFIX = "${PWD}/test/"
BASE_URL = https://github.com/ldrfy/lfy/releases/download/auto


clear:
	rm -rf build test
	mkdir -p dist
	rm -rf {HOME}/.local/share/glib-2.0/schemas/gschemas.compiled
	rm -rf {HOME}/.local/lib/lfy
	rm -rf /tmp/v${VERSION}.zip
	rm -rf /tmp/lfy-${VERSION}


test:clear
	meson setup build --prefix=${PREFIX} -Dbuild_type=${BUILD_TYPE}
	meson compile -C build
	meson test -C build
	# meson dist -C build --allow-dirty
	DESTDIR=${DESTDIR} meson install -C build


# Generate .pot file
update-pot:
	xgettext -d "lfy" \
			--output=./po/lfy.pot \
			--copyright-holder="yuhldr" \
			--package-name="cool.ldr.lfy" \
			--msgid-bugs-address="yuhldr@gmail.com" \
			--add-comments=TRANSLATORS \
			--files-from=./po/POTFILES


po-init:
	msginit -i ./po/lfy.pot -o ./po/${TO_LANG}.po


update-po:
	msgmerge -U ./po/${TO_LANG}.po ./po/lfy.pot


.PHONY: build other update-pot update-po po-init test whl rename


test-zip:
	mkdir /tmp/lfy-${VERSION} && \
	cp -r lfy /tmp/lfy-${VERSION}/ && \
	cp -r data /tmp/lfy-${VERSION}/ && \
	cp -r po /tmp/lfy-${VERSION}/ && \
	cp -r pkg /tmp/lfy-${VERSION}/ && \
	cp -r meson.build /tmp/lfy-${VERSION}/ && \
	cp -r meson_options.txt /tmp/lfy-${VERSION}/ && \
	cd /tmp/ && \
	zip -r v${VERSION}.zip lfy-${VERSION} && \
	rm -r lfy-${VERSION}


test-deb: clear
	make PREFIX="/usr" DESTDIR="${PWD}/${BUILD_PKG}/deb" test

	cd "${PWD}/${BUILD_PKG}/" && \
	mv deb/DEBIAN/control ./ && \
	sed 's/any/amd64/g' ./control > ./deb/DEBIAN/control && \
	dpkg -b deb ./deb/lfy-${VERSION}-x86_64.deb && \
	cd deb && \
	mv lfy-${VERSION}-x86_64.deb ${DISK}/lfy-${VERSION}-x86_64-${BUILD_TYPE}.deb


# python-build
test-pip: clear
	make PREFIX="/usr" DESTDIR="${PWD}/${BUILD_PKG}/pip" test
	cp README.md ${BUILD_PKG}/pip/
	cp LICENSE ${BUILD_PKG}/pip/

	cd ${BUILD_PKG}/pip && \
	mv usr/lib/lfy ./ && \
	mv usr/share/icons/hicolor/scalable/apps ./lfy/resources/ && \
	mv usr/share/locale ./lfy/resources/ && \
	python -m build && \
	cp dist/lfy-${VERSION}-py3-none-any.whl ${DISK}/



test-flatpak:clear
	meson setup build -Dbuild_type=${BUILD_TYPE}
	cd ${BUILD_PKG}/flatpak && \
	flatpak-builder --repo=repo build-dir cool.ldr.lfy.yaml && \
	flatpak build-bundle repo cool.ldr.lfy-${VERSION}.flatpak cool.ldr.lfy && \
	flatpak install -y --user cool.ldr.lfy-${VERSION}.flatpak && \
	mv cool.ldr.lfy-${VERSION}.flatpak ${DISK}/cool.ldr.lfy-${VERSION}-${BUILD_TYPE}.flatpak


test-aur: clear test-zip
	meson setup build -Dbuild_type=${BUILD_TYPE}

	cd ${BUILD_PKG}/aur && \
	cp /tmp/v${VERSION}.zip ./ && \
	makepkg -sf && \
	mv lfy-${VERSION}-1-any.pkg.tar.zst ${DISK}/lfy-${VERSION}-1-any-${BUILD_TYPE}.pkg.tar.zst


test-rpm: clear test-zip
	meson setup build -Dbuild_type=${BUILD_TYPE}

	mkdir -p ${PWD}/${BUILD_PKG}/rpm/SOURCES/lfy-${VERSION} && \
	cd ${PWD}/${BUILD_PKG}/rpm/SOURCES/ && \
	cp /tmp/v${VERSION}.zip ./

	rpmbuild -bb ${PWD}/${BUILD_PKG}/rpm/SPECS/lfy.spec \
		--define "_topdir ${PWD}/${BUILD_PKG}/rpm/"
	cd ${BUILD_PKG}/rpm/ && \
	mv RPMS/x86_64/lfy-${VERSION}-1.x86_64.rpm \
		${DISK}/lfy-${VERSION}-1.x86_64-${BUILD_TYPE}.rpm

	rpmbuild -bb ${PWD}/${BUILD_PKG}/rpm/SPECS/lfy-suse.spec \
		--define "_topdir ${PWD}/${BUILD_PKG}/rpm/"
	cd ${BUILD_PKG}/rpm/ && \
	mv RPMS/x86_64/lfy-${VERSION}-1.x86_64.rpm \
		${DISK}/lfy-${VERSION}-1.x86_64-${BUILD_TYPE}-suse.rpm


release:
	make BUILD_TYPE=qt test-aur
	make BUILD_TYPE=qt test-deb
	make BUILD_TYPE=qt test-rpm
	make BUILD_TYPE=qt test-pip
	make BUILD_TYPE=gtk test-aur
	make BUILD_TYPE=gtk test-deb
	make BUILD_TYPE=gtk test-rpm
	make BUILD_TYPE=gtk test-flatpak

uninstall:
	cd build && ninja uninstall


GTK_FILES = \
    lfy-$(VERSION)-1-any-gtk.pkg.tar.zst \
    lfy-$(VERSION)-x86_64-gtk.deb \
    lfy-$(VERSION)-1.x86_64-gtk.rpm \
    lfy-$(VERSION)-1.x86_64-gtk-suse.rpm \
    cool.ldr.lfy-$(VERSION)-gtk.flatpak

QT_FILES = \
    lfy-$(VERSION)-1-any-qt.pkg.tar.zst \
    lfy-$(VERSION)-x86_64-qt.deb \
    lfy-$(VERSION)-1.x86_64-qt.rpm \
    lfy-$(VERSION)-1.x86_64-qt-suse.rpm \
    x \
	lfy-$(VERSION)-py3-none-any.whl

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
