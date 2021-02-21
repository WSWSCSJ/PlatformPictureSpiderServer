"""
@File    : configure.py
@Author  : CXJ
@Contact : github.com/WSWSCSJ
"""
from configparser import ConfigParser


class Configure(ConfigParser):
    """
    convert configure parser sections to python.dictionary
    """

    def to_dict(self):
        _dict = dict(self._sections)
        for key in _dict:
            _dict[key] = dict(_dict[key])
        return _dict
