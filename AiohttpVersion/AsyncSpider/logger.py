"""
@File    : logger.py
@Author  : CXJ
@Contact : github.com/WSWSCSJ
"""
import sys
import time
import os

#TODO: add log level
def log(information):
    f = sys._getframe(1)
    sys.stdout.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [ {f.f_code.co_filename.split(os.sep)[-1]} | {f.f_code.co_name} | {f.f_lineno} ] {information}\n")