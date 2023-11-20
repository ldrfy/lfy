TO_LANG = zh_CN

install:
	rm -rf _build
	meson src _build
	meson test -C _build
	meson install -C _build

uninstall:
	cd _build && ninja uninstall


arch:
	mkdir -p disk
	rm -rf _build
	meson src _build

	cd _build/pkg && \
	mkdir lfy-0.2.0 && \
	cp -r ../../src lfy-0.2.0 && \
	zip -r v0.2.0.zip lfy-0.2.0 && \
	makepkg -sf && \
	cp *.pkg.tar.zst ../../disk/

	rm -rf _build



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


