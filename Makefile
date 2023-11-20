TO_LANG = zh_CN
INSTALL_DIR=${HOME}/.local
PKG_DIR="${PWD}/_build/pkg"

install:
	rm -rf _build
	meson src _build
	meson test -C _build
	meson install -C _build

test:
	rm -rf _build
	meson src _build --prefix=${INSTALL_DIR}
	meson install -C _build


rm:
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


whl:
	mkdir -p disk
	rm -rf _build

	meson src _build --prefix=${INSTALL_DIR}
	DESTDIR=${PKG_DIR} meson install -C _build

	cp README.md ${PKG_DIR}

	cd ${PKG_DIR} && \
	cp -r ./${INSTALL_DIR}/lib/*/site-packages/lfy ./ && \
	cp -r ./${INSTALL_DIR}/bin ./ && \
	cp -r ./${INSTALL_DIR}/share ./ && \
	rm -rf ./home && \
	python setup.py sdist bdist_wheel && \
	cp ./dist/*.whl ../../disk/

	rm -rf _build
	pip uninstall lfy --break-system-packages

	pip install ./disk/*.whl --break-system-packages



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


