import pytest
from pathlib import Path
from configparser import ConfigParser as CP
import sys
import os

sys.path.append(os.getcwd())

from modules.config import check_config_file

normalFile = Path("tests/settings.ini")
DOEError = Path("tests/DOE_settings.ini")
DSEError = Path("tests/DSE_settings.ini")
MSHError = Path("tests/MSH_settings.ini")
cfg = CP()


@pytest.mark.parametrize("args, expectedResult", [
    ((normalFile, cfg), True),
    ((MSHError, cfg), False),
    ((DOEError, cfg), False),
    ((DSEError, cfg), False),
])
def test_check_config(args, expectedResult):
    res = check_config_file(*args)
    assert res == expectedResult


if __name__ == '__main__':
    pytest.main()
