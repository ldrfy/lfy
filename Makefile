TO_LANG = zh_CN
VERSION = 0.0.7
DISK = ../../../dist/
BUILD_PKG=build/pkg
DESTDIR = "/"
PREFIX = "${HOME}/.local/"


clear:
	rm -rf build test
	mkdir -p dist
	rm -rf {HOME}/.local/share/glib-2.0/schemas/gschemas.compiled
	rm -rf {HOME}/.local/lib/lfy

test:clear
	meson setup build --prefix=${PREFIX}
	meson compile -C build
	meson test -C build
	meson dist -C build --allow-dirty
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


.PHONY: build other update-pot update-po po-init test whl



test-deb: clear
	make PREFIX="/usr" DESTDIR="${PWD}/${BUILD_PKG}/deb" test

	cd "${PWD}/${BUILD_PKG}/" && \
	mv deb/DEBIAN/control ./ && \
	sed 's/any/arm64/g' ./control > ./deb/DEBIAN/control && \
	dpkg -b deb ./deb/lfy-${VERSION}-aarch64.deb && \
	cd deb && mv ./lfy-${VERSION}-aarch64.deb ${DISK} && cd - && \
	sed 's/any/amd64/g' ./control > ./deb/DEBIAN/control && \
	dpkg -b deb ./deb/lfy-${VERSION}-x86_64.deb && \
	cd deb && mv ./lfy-${VERSION}-x86_64.deb ${DISK}


test-flatpak:clear
	meson setup build
	cd ${BUILD_PKG}/flatpak && \
	flatpak-builder --repo=repo build-dir cool.ldr.lfy.yaml && \
	flatpak build-bundle repo cool.ldr.lfy-${VERSION}.flatpak cool.ldr.lfy && \
	flatpak install -y --user cool.ldr.lfy-${VERSION}.flatpak && \
	mv cool.ldr.lfy-${VERSION}.flatpak ${DISK}


test-aur: clear
	meson setup build

	cd ${BUILD_PKG}/aur && \
	mkdir lfy-${VERSION} && \
	cp -r ../../../lfy lfy-${VERSION}/ && \
	cp -r ../../../data lfy-${VERSION}/ && \
	cp -r ../../../po lfy-${VERSION}/ && \
	cp -r ../../../pkg lfy-${VERSION}/ && \
	cp -r ../../../lfy.in lfy-${VERSION}/ && \
	cp -r ../../../define.in lfy-${VERSION}/ && \
	cp -r ../../../meson.build lfy-${VERSION}/ && \
	zip -r v${VERSION}.zip lfy-${VERSION} && \
	rm -r lfy-${VERSION} && \
	makepkg -sf && \
	mv *.pkg.tar.zst ${DISK}


test-rpm: clear
	make PREFIX="/usr" DESTDIR="${PWD}/${BUILD_PKG}/rpm/" test

	cd "${PWD}/${BUILD_PKG}/rpm/SPECS/" &&\
	rpmbuild -bb lfy.spec && \
	cd ../ && \
	mv ./RPMS/x86_64/*.rpm ${DISK}


release: test-deb test-rpm test-flatpak
	cd ${BUILD_PKG}/aur && \
	makepkg -sf && \
	mv *.pkg.tar.zst ${DISK}

uninstall:
	cd build && ninja uninstall

