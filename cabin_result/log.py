import logging
import sys


logger = logging.getLogger("cabin")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

file_handler = logging.FileHandler("cabin.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# ———————————————————————— #

def print_to_log(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    # 拼接位置参数
    message = sep.join(str(a) for a in args)
    if end != "\n":
        message += end
    logger.info(message)
