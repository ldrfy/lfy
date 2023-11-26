TO_LANG = zh_CN
VERSION = 0.0.2
DISK = ../../../../disk/

clear:
	rm -rf _build test
	mkdir -p disk


flatpak:clear
	meson _build
	cd _build/src/pkg/flatpak && \
	flatpak-builder --repo=repo-dir _build cool.ldr.lfy.json --user &&\
	flatpak build-bundle repo-dir lfy-${VERSION}.flatpak cool.ldr.lfy && \
	mv *.flatpak ${DISK}
	# flatpak-builder --install _build cool.ldr.lfy.json --user



aur: clear
	meson _build

	cd _build/src/pkg/aur && \
	makepkg -sf && \
	mv *.pkg.tar.zst ${DISK}


deb: clear
	meson _build --prefix="/usr"
	meson compile -C _build
	meson test -C _build
	DESTDIR="${PWD}/_build/src/pkg/deb" meson install -C _build

	cd "${PWD}/_build/src/pkg/" \
	&& dpkg -b deb ./deb/lfy-${VERSION}.deb && \
	cd deb && \
	mv *.deb ${DISK}


# Generate .pot file
update-pot:
	xgettext -d "lfy" \
			--output=./src/po/lfy.pot \
			--copyright-holder="yuhldr" \
			--package-name="cool.ldr.lfy" \
			--msgid-bugs-address="yuhldr@gmail.com" \
			--add-comments=TRANSLATORS \
			--files-from=./src/po/POTFILES


po-init:
	msginit -i ./src/po/lfy.pot -o ./src/po/${TO_LANG}.po


update-po:
	msgmerge -U ./src/po/${TO_LANG}.po ./src/po/lfy.pot


.PHONY: build other update-pot update-po po-init test whl



test-flatpak:clear
	meson _build
	cd _build/src/pkg/flatpak && \
	flatpak-builder --install _build cool.ldr.lfy.json --user


test-aur: clear
	meson _build
	cd _build/src/pkg/aur && \
	mkdir lfy-${VERSION} && \
	cp -r ../../../../src lfy-${VERSION}/ && \
	cp -r ../../../../meson.build lfy-${VERSION}/ && \
	zip -r v${VERSION}.zip lfy-${VERSION} && \
	rm -r lfy-${VERSION} && \
	makepkg -sf && \
	mv *.pkg.tar.zst ${DISK}

test:clear
	meson _build --prefix="${HOME}/.local"
	meson compile -C _build
	meson test -C _build
	meson install -C _build
	# DESTDIR="${PWD}/test" meson install -C _build

uninstall:
	cd _build && ninja uninstall

