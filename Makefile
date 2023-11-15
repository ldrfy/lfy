TO_LANG = zh_CN
VERSION = 0.0.1


install:
	rm -rf _build
	rm -rf test
	meson lt _build --prefix=${HOME}/.local
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
	xgettext -d "lt" \
			--output=./lt/po/lt.pot \
			--no-wrap \
			--copyright-holder="yuhldr" \
			--package-name="cool.ldr.lt" \
			--msgid-bugs-address="yuhldr@gmail.com" \
			--add-comments=TRANSLATORS \
			--files-from=./lt/po/POTFILES


po-init:
	msginit -i ./lt/po/lt.pot -o ./lt/po/${TO_LANG}.po


update-po:
	msgmerge -U ./lt/po/${TO_LANG}.po ./lt/po/lt.pot


.PHONY: build other update-pot update-po po-init


