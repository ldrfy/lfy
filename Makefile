TO_LANG = zh_CN
VERSION = 0.0.1
INSTALL_DIR=${HOME}/.local


install:
	rm -rf _build
	rm -rf test
	meson src _build --prefix=${INSTALL_DIR}
	meson compile -C _build
	meson install -C _build

# DESTDIR="../test" meson install -C build

rm:
	cd _build && ninja uninstall

other:
	python -m compileall -d ${HOME}/.local/lib "test/.local/lib"
	python -O -m compileall -d ${HOME}/.local/lib "test/.local/lib"


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


.PHONY: build other update-pot update-po po-init


