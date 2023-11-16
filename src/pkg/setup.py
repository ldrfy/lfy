'''pip打包，需要meson编译以后才能使用'''
import os

import setuptools

BASE_DIR = "./"


def get_all_files(directory):
    data_files = []

    # 遍历目录及其子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith(".cache"):
                file_path = os.path.join(root, file)
                data_files.append((root, [file_path]),)

    return data_files


with open("../README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

scripts = [
    f"{BASE_DIR}/bin/@APP_NAME@",
]
data_files = get_all_files("./share")
print(data_files)

setuptools.setup(name='@APP_NAME@',
                 version='@VERSION@',
                 author="yuhldr",
                 author_email="yuhldr@qq.com",
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 py_modules=["@APP_NAME@"],
                 scripts=scripts,
                 data_files=data_files,
                 install_requires=["PyGObject", "requests", "cryptography"],
                 include_package_data=True,
                 packages=setuptools.find_packages(),
                 description="翻译")
