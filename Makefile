TO_LANG=zh_CN
VERSION=0.0.7
BUILD_TYPE=qt
DISK = ../../../dist/
BUILD_PKG=build/pkg
DESTDIR = "/"
PREFIX = "${HOME}/.local/"


clear:
	rm -rf build test
	mkdir -p dist
	rm -rf {HOME}/.local/share/glib-2.0/schemas/gschemas.compiled
	rm -rf {HOME}/.local/lib/lfy
	rm -rf /tmp/v${VERSION}.zip


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
	cp -r define.py /tmp/lfy-${VERSION}/ && \
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
	make test-aur
	make test-deb
	make test-rpm
	make BUILD_TYPE=gtk test-aur
	make BUILD_TYPE=gtk test-deb
	make BUILD_TYPE=gtk test-rpm
	make BUILD_TYPE=gtk test-flatpak

uninstall:
	cd build && ninja uninstall
