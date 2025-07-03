import logging
import builtins

# 1. 初始化 logger（同上）
logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)
# ... add handler, formatter, etc.

# 2. 把 print 绑到 logger.info
def print_to_log(*args, **kwargs):
    # 把 sep、end 之类的参数也考虑进去
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    message = sep.join(str(a) for a in args) + ("" if end=="\n" else end)
    logger.info(message)

builtins.print = print_to_log

# —— 之后不需要改 print，所有 print() 都走 logger.info ——
print("这条本来要打印到控制台，现在同时写到日志了")
