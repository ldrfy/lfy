'''pip打包，需要meson编译以后才能使用'''
import setuptools

BASE_DIR = "./"


with open("../README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

scripts = [
    f"{BASE_DIR}/bin/@APP_NAME@",
]
data_files = [
    ('./',
     [
         f"{BASE_DIR}/share/applications/@APP_ID@.desktop",
         f"{BASE_DIR}/share/glib-2.0/schemas/@APP_ID@.gschema.xml",
         f"{BASE_DIR}/share/icons/hicolor/scalable/apps/@APP_ID@.svg",
         f"{BASE_DIR}/share/icons/hicolor/symbolic/apps/@APP_ID@-symbolic.svg",
         f"{BASE_DIR}/share/locale/zh_CN/LC_MESSAGES/@APP_ID@.mo",
         f"{BASE_DIR}/share/metainfo/@APP_ID@.appdata.xml",
     ])
]

setuptools.setup(name='@APP_NAME@',
                 version='@VERSION@',
                 author="yuhldr",
                 author_email="yuhldr@qq.com",
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 py_modules=["@APP_NAME@"],
                 scripts=scripts,
                 data_files=data_files,
                 install_requires=["requests"],
                 include_package_data=True,
                 packages=setuptools.find_packages(),
                 description="翻译")
