"""
@File    : util.py
@Author  : CXJ
@Contact : github.com/WSWSCSJ
"""
import time
import asyncio
from sys import stdout as out
import threading
import re
from .logger import INFO


def time_counter(function):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = function(*args, **kwargs)
        end = time.time()
        INFO(f"{function.__name__} cost {end - start} second")
        return result

    return wrapper


def between_filter(first_str, last_str, text):
    """
    Find string between first_str and last_str in text, don't contain first_str and last_str
    :return: String
    """
    pattern = re.compile(r'(?<={}).+?(?={})'.format(first_str, last_str))
    filter_text = ''.join(pattern.findall(text))
    return filter_text


def retry(limit=1, duration=0, debug=False):
    """
    case:
        @retry(5, 0.1, True)
        def task(**kwargs):
            pass
    :param limit: max retry times
    :param duration: thread level time duration
    :param debug: log out function arguments
    :return: wrapper
    """
    assert isinstance(limit, int) and limit > 0

    def wrapper(function):
        _limit, _debug = limit + 1, debug

        def inner(*args, **kwargs):
            __limit, __debug = _limit, _debug
            while __limit:
                try:
                    function(*args, **kwargs)
                except Exception as e:
                    information = "{method} retry cause by {error}\n".format(
                        method=function.__name__, error=e
                    )
                    if __debug:
                        if args:
                            information += "{}\n".format(args)
                        if kwargs:
                            information += "{}\n".format(kwargs)
                    print(information)
                    __limit -= 1
                    time.sleep(duration)
                    continue
                break

        return inner

    return wrapper


def async_runtime_inspect(function):
    async def wrapper(*args, **kwargs):
        out.write(
            "[{datetime}] {thread}.{function} start\n".format(
                datetime=time.strftime("%Y-%m-%d %H:%M:%S"), thread=threading.current_thread(),
                function=function.__name__)
        )
        if args:
            out.write(f"\targs:{args}")
        if kwargs:
            out.write(f"\tkwargs:{kwargs}")
        out.write("\n")
        result = await function(*args, **kwargs)
        out.write(
            "[{datetime}] {thread}.{function} finish\n".format(
                datetime=time.strftime("%Y-%m-%d %H:%M:%S"), thread=threading.current_thread(),
                function=function.__name__)
        )
        return result

    return wrapper


def async_retry(limit=1, duration=0):
    """
        case:
            @retry(5, 0.1)
            def task(**kwargs):
                pass
        :param limit: max retry times
        :param duration: thread level time duration
        :return: wrapper
        """
    assert isinstance(limit, int) and limit > 0

    def wrapper(function):
        _limit = limit + 1

        async def inner(*args, **kwargs):
            total = _limit - 1
            __limit = _limit
            while __limit:
                try:
                    result = await function(*args, **kwargs)
                except Exception as e:
                    __limit -= 1
                    out.write(
                        "[{datetime}] {thread}.{function} retry {has}/{have} cause by {error}\n"
                        "args: {args}, kwargs: {kwargs}\n".format(
                            datetime=time.strftime("%Y-%m-%d %H:%M:%S"), thread=threading.current_thread(),
                            function=function.__name__, error=e, args=args, kwargs=kwargs, has=total - __limit,
                            have=total)
                    )
                    await asyncio.sleep(duration)
                    continue
                else:
                    return result
            return None

        return inner

    return wrapper
