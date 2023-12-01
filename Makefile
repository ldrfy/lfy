TO_LANG = zh_CN
VERSION = 0.0.3
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
	meson build --prefix=${PREFIX}
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


test-whl:
	make PREFIX="/usr" DESTDIR="${PWD}/${BUILD_PKG}/pip" test

	cd ${BUILD_PKG}/pip && \
	cp ${DISK}/../README.md ./usr/ && \
	mv setup.py ./usr/ && \
	cd ./usr/ && \
	mv lib/lfy ./ && \
	python setup.py sdist bdist_wheel && \
	cd ../ && \
	cp ./usr/dist/*.whl ${DISK}

test-flatpak:clear
	meson build
	cd ${BUILD_PKG}/flatpak && \
	flatpak-builder --install build cool.ldr.lfy.json --user


test-aur: clear
	meson build

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


uninstall:
	cd build && ninja uninstall

