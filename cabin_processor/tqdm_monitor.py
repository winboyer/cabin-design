import os
import time
from tqdm import tqdm
import builtins
from cabin_result.log import print_to_log
builtins.print = print_to_log

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
    except Exception :
        # 根据需要，这里可以记录异常或重试；此处简化为抛出
        raise


# 只能监控一个作业
def tqdm_monitor(dir_path: str, sta_filename: str, iter_cnt: int,
                 win_width, poll_interval: float = 0.5):
    """
    通过 monitor_sta_progress 获取浮点进度（0~1），
    将其转换为百分比（0~100）整数后，用 tqdm 显示进度条。
    """
    total_percent = 100  # 以百分比为单位
    # 初始化 tqdm，total=100
    if iter_cnt is not None:
        if sta_filename.startswith("Job-Mises"):
            name = f"[窗宽 {win_width} 第 {iter_cnt} 轮迭代] 舱体应力分析"
        else:
            name = f"[窗宽 {win_width} 第 {iter_cnt} 轮迭代] 舱体挠度分析"
    else:
        if sta_filename.startswith("Job-Mises"):
            name = f"舱体应力分析"
        else:
            name = f"舱体挠度分析"
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

def wait_for_all_csv(dir_path: str, expected_names, win_width, poll_interval: float = 0.5, iter_cnt: int = None):
    """
    等待直到 expected_names 列表中的所有文件都出现在 dir_path 下。
    可以用 tqdm 显示“CSV 生成进度”。
    """
    # 初始化一个 set 用于记录已经检测到的文件
    found = set()
    total = len(expected_names)
    # 构建进度条名称
    if iter_cnt is not None:
        desc = f"[窗宽 {win_width} 第 {iter_cnt} 轮迭代] 计算结果处理"
    else:
        desc = "计算结果处理"
    # 用 total 作为进度条总量
    pbar = tqdm(total=total, desc=desc, unit="file")
    try:
        while True:
            for name in expected_names:
                if name not in found:
                    fullp = os.path.join(dir_path, name)
                    if os.path.exists(fullp):
                        found.add(name)
                        pbar.update(1)
            if len(found) >= total:
                break
            time.sleep(poll_interval)
    finally:
        pbar.close()

def monitor(dir_path: str, iter_cnt: int, win_width ,poll_interval: float = 0.5):

    expected_csv_names = [
        "CABIN_PLATES_nodes.csv",
        "CABIN_FRAME_nodes.csv",
        "U_CABIN_FRAME.csv",
        "U_CABIN_PLATES.csv",
        "S_CABIN_FRAME.csv",
        "S_CABIN_PLATES.csv",
    ]

    if iter_cnt is not None:
        print(f"[窗宽 {win_width} 第 {iter_cnt} 轮迭代] 等待模型创建...")
    else:
        print(f"等待模型创建...")

    file_path = os.path.join(dir_path, "Job-Mises.sta")
    while not os.path.exists(file_path):
        time.sleep(poll_interval)

    tqdm_monitor(dir_path, "Job-Mises.sta", iter_cnt, win_width, poll_interval)

    file_path = os.path.join(dir_path, "Job-Deflection.sta")
    while not os.path.exists(file_path):
        time.sleep(poll_interval)

    tqdm_monitor(dir_path, "Job-Deflection.sta", iter_cnt, win_width, poll_interval)

    wait_for_all_csv(dir_path, expected_csv_names, win_width, poll_interval, iter_cnt)



