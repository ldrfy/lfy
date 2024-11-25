#!@PYTHON@
import sys

APP_NAME = '@APP_NAME@'
PYTHON_DIR = '@PYTHON_DIR@'

print("PYTHON_DIR", PYTHON_DIR)
sys.path.append(PYTHON_DIR)

from lfy.qt.main import main  # pylint: disable=C0413

if __name__ == "__main__":

    main()
