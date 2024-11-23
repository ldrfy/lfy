#!@PYTHON@
import os
import sys

APP_NAME = '@APP_NAME@'
PYTHON_DIR = '@PYTHON_DIR@'

print("PYTHON_DIR", PYTHON_DIR)
if not os.path.exists(f"{PYTHON_DIR}/{APP_NAME}"):
    print("修正")
    THIS_DIR, THIS_FILENAME = os.path.split(__file__)
    PYTHON_DIR = os.path.abspath(f"{THIS_DIR}/../lib/")
    print(PYTHON_DIR)
sys.path.append(PYTHON_DIR)

from lfy.gtk.main import main  # pylint: disable=C0413

if __name__ == '__main__':

    main()
