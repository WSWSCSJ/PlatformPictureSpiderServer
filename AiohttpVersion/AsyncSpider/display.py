"""
@File    : display.py
@Author  : CXJ
@Contact : github.com/WSWSCSJ
@Description:
    进度条测试
    case:
        _counter = {
            "done": 0, "total": 0
        }

        @async_task_progress(counter=_counter)
        async def process():
            await asyncio.sleep(random.randint(3, 15))

        async def run():
            tasks = [asyncio.create_task(process()) for _ in range(20)]
            tasks.append(asyncio.create_task(counting(_counter)))
            await asyncio.gather(*tasks)

        asyncio.run(run())
"""
import sys
import time
import asyncio
import threading

MAX_SPACE = 150
DONE_SIGN = "▋"
UNDONE_SIGN = "-"

def async_task_progress(counter):
    def wrapper(function):
        async def inner(*args, **kwargs):
            counter["total"] += 1
            if args:
                sys.stdout.write(f"args: {args}")
            if kwargs:
                sys.stdout.write(f"kwargs: {kwargs}")
            result = await function(*args, **kwargs)
            counter["done"] += 1
            return result
        return inner
    return wrapper

async def counting(counter):
    def show():
        current_information = f"[{time.strftime('%Y-%m-%d %H:%M:%S')} {threading.current_thread()}] {counter['done']}/{counter['total']} "
        progress_space = MAX_SPACE - len(current_information)
        done_space = int(progress_space * counter['done'] / counter['total'])
        undone_space = progress_space - done_space
        sys.stdout.write(
            "\b" * MAX_SPACE * 2 + current_information + DONE_SIGN * done_space + UNDONE_SIGN * undone_space
        )
    while True:
        show()
        await asyncio.sleep(0.05)
        if counter["done"] == counter["total"] and counter["total"] != 0:
            show()
            break