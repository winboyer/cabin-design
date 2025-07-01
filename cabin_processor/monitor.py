import os
import time
import threading
from tqdm import tqdm


def parse_progress_from_line(line: str):
    """
    尝试从一行文本中提取倒数第二列的浮点数进度值。
    返回 float（0~1）或 None（无法解析）。
    """
    # 去掉行首尾空白后按空白分割
    parts = line.strip().split()
    if len(parts) < 2:
        return None
    token = parts[-2]
    try:
        # 这里视情况 . 替换逗号？通常是小数点表示法，直接 float 即可
        prog = float(token)
    except ValueError:
        return None
    return prog


def monitor_sta_progress(dir_path: str, sta_filename: str,
                         poll_interval: float = 1.0):
    """
    生成器：实时监控 dir_path/sta_filename 文件，一旦文件创建，
    便尾随读取新增行，提取倒数第二列数值并 yield。
    当进度达到或超过 1.0 时，yield 后退出。

    参数：
      - dir_path: 目录路径，比如 r"F:\CAE\cube"
      - sta_filename: 文件名，比如 "Job-Mises.sta"
      - poll_interval: 轮询间隔（秒），检查文件是否存在或等待新行时的 sleep 时间
    用法示例：
        for prog in monitor_sta_progress(dir, fname):
            # prog 是浮点型，0~1 之间
            ...
    """
    file_path = os.path.join(dir_path, sta_filename)
    # 1. 等待文件创建
    while not os.path.exists(file_path):
        # 文件尚未出现，休眠后重试
        time.sleep(poll_interval)
    # 2. 文件已存在，开始尾随读取
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # 先读取已有内容（可选），以便拿到最近的进度
            last_progress = 0.0
            # 读取已有所有行，尝试获取最后一行的进度
            # （如果已有内容里最后一行包含进度信息）
            for line in f:
                prog = parse_progress_from_line(line)
                if prog is not None and prog > last_progress:
                    last_progress = prog
            # 到这里，文件指针在末尾
            # 如果已有进度 >=1.0，可以直接 yield 然后结束；否则继续 tail
            if last_progress >= 1.0:
                yield last_progress
                return
            # 3. 持续 tail
            while True:
                line = f.readline()
                if not line:
                    # 无新行，待定后重试
                    time.sleep(poll_interval)
                    continue
                prog = parse_progress_from_line(line)
                if prog is None:
                    continue
                # 仅在进度增大时才 yield
                if prog > last_progress:
                    last_progress = prog
                    yield last_progress
                    # 如果达到或超过 1.0，则视作完成并退出
                    if last_progress >= 1.0:
                        return
    except Exception as e:
        # 根据需要，这里可以记录异常或重试；此处简化为抛出
        raise


# 可选：若希望在后台线程里监控并通过回调通知，则可以这样包装：
def start_sta_monitor_thread(dir_path: str, sta_filename: str, callback,
                             poll_interval: float = 1.0):
    """
    在后台线程启动 monitor_sta_progress，并在每次拿到新进度时执行 callback(prog)。
    callback 接收一个浮点数进度值。
    返回 threading.Thread 对象；线程结束时自然退出。
    """

    def _target():
        try:
            for prog in monitor_sta_progress(dir_path, sta_filename, poll_interval=poll_interval):
                callback(prog)
        except Exception as e:
            # 若需要，将异常回调或打印
            print(f"[监控线程] 遇到异常: {e}")

    t = threading.Thread(target=_target, daemon=True)
    t.start()
    return t


def tqdm_monitor(dir_path: str, sta_filename: str, iter_cnt: int,
                 poll_interval: float = 1.0):
    """
    通过 monitor_sta_progress 获取浮点进度（0~1），
    将其转换为百分比（0~100）整数后，用 tqdm 显示进度条。
    """
    total_percent = 100  # 以百分比为单位
    # 初始化 tqdm，total=100
    if sta_filename.startswith("Job-Mises"):
        name = f"[第 {iter_cnt} 轮迭代] 应力分析进度"
    else:
        name = f"[第 {iter_cnt} 轮迭代] 挠度分析进度"
    pbar = tqdm(total=total_percent, desc=name, unit="%")
    last_percent = 0
    try:
        for prog in monitor_sta_progress(dir_path, sta_filename, poll_interval=poll_interval):
            # prog 是 0~1 之间浮点
            percent = int(prog * 100)
            # 避免重复更新或回退：只在 percent > last_percent 时更新
            if percent > last_percent:
                delta = percent - last_percent
                pbar.update(delta)
                last_percent = percent
            # 当达到 100% 时跳出
            if last_percent >= total_percent:
                break
        # 最后确保条满
        if last_percent < total_percent:
            pbar.update(total_percent - last_percent)
    finally:
        pbar.close()

# 脚本入口示例
if __name__ == "__main__":
    # 示例路径，请根据实际改为原始字符串或正斜杠，以避免转义问题
    dir_path = r"F:\CAE\cube_test\iter_0_20250625_100749"
    sta_filename = "Job-Mises.sta"
    # 启动进度显示
    tqdm_monitor(dir_path, sta_filename, poll_interval=0.5)
