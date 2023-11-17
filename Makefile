TO_LANG = zh_CN
INSTALL_DIR=${HOME}/.local


install:
	rm -rf _build
	meson src _build --prefix=${INSTALL_DIR}
	meson test -C _build
	meson install -C _build

test:
	rm -rf test
	rm -rf _build
	meson src _build --prefix=${INSTALL_DIR}
	DESTDIR="${PWD}/test" meson install -C _build

rm:
	cd _build && ninja uninstall

whl:
	make test

	cp README.md ./test/${INSTALL_DIR} && \
	cp _build/pkg/setup.py ./test/${INSTALL_DIR} && \
	cd ./test/${INSTALL_DIR} && \
	cp -r ./lib/*/site-packages/lfy ./ && \
	python setup.py sdist bdist_wheel

	pip uninstall lfy --break-system-packages
	pip install ./test/${INSTALL_DIR}/dist/*.whl --break-system-packages

	rm -rf _build
	rm -rf test


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


