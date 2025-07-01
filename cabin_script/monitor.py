# 用于监测计算进度
import os
import time
import re
from watchdog.events import FileSystemEventHandler

class JobFileHandler(FileSystemEventHandler):
    EXPECTED_CSV_NAMES = [
        "CABIN_PLATES_nodes.csv",
        "CABIN_FRAME_nodes.csv",
        "U_CABIN_FRAME.csv",
        "U_CABIN_PLATES.csv",
        "S_CABIN_FRAME.csv",
        "S_CABIN_PLATES.csv",
    ]

    def __init__(self, file_path, callback, iter_num=None,
                 progress_threshold=0.5, csv_finalize_wait=1.0,
                 start_percent=0.0, percent_span=50.0,
                 finish_on_progress100=False):
        """
        file_path: 要监控的 .sta 文件全路径
        callback: signature callback(scaled_progress: float, is_completed: bool)
        progress_threshold: 原逻辑中的百分比变化阈值
        csv_finalize_wait: 当检测到 CSV 文件存在后，额外等待时间以确保写入完成
        start_percent: 本阶段进度起始百分比（如第一阶段 0，第二阶段 50）
        percent_span: 本阶段跨越的百分比区间长度（如分别取 50）
        finish_on_progress100: 如果 True，则当 .sta 中 progress>=100 时，立即认为本阶段完成（不再检测 CSV）。一般用于阶段1；阶段2可留 False，以等 CSV 生成后再判完成。
        """
        self.file_path = file_path
        self.callback = callback
        self.iter_num = iter_num
        self.last_position = 0
        self.completed = False
        self.last_reported_progress = 0.0
        self.progress_threshold = progress_threshold
        self.csv_finalize_wait = csv_finalize_wait
        # 阶段相关
        self.start_percent = start_percent
        self.percent_span = percent_span
        self.finish_on_progress100 = finish_on_progress100
        # 只有当需要通过 CSV 判断真正结束时，才用下面两个标志；若 finish_on_progress100=True，可忽略 CSV 检测
        self.csv_completion_reported = False

    def on_created(self, event):
        # 当指定的 .sta 文件创建时触发
        if event.src_path == self.file_path:
            self.last_position = 0
            # 直接启动 blocking 监控
            self.monitor_file()

    def monitor_file(self):
        """
        Blocking 直到本阶段 completed=True 或者文件消失。内部会不断调用 callback(scaled_progress, is_completed)。
        """
        folder = os.path.dirname(self.file_path)
        # 如果文件不存在，则先返回；外层调用者可循环等待文件生成再调用 monitor_file
        if not os.path.exists(self.file_path):
            return

        # 初始化 last_position，如果文件已存在且希望从末尾开始监控，则在外部设置 last_position = os.path.getsize(file_path)
        while not self.completed:
            time.sleep(0.5)
            if not os.path.exists(self.file_path):
                break
            # 1) 读取 .sta 新增内容，解析进度
            try:
                with open(self.file_path, 'r') as f:
                    f.seek(self.last_position)
                    new_lines = f.readlines()
                    self.last_position = f.tell()
                    progress_to_report = None
                    for line in new_lines:
                        line = line.strip()
                        # 匹配类似：数字 ... 数字 ... [progress] 形式
                        if re.match(r'^\s*\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+[\d.]+', line):
                            parts = re.split(r'\s+', line)
                            if len(parts) >= 8:
                                try:
                                    progress_value = float(parts[-2])
                                    progress_percent = min(100.0, progress_value * 100)
                                    if progress_percent - self.last_reported_progress >= self.progress_threshold:
                                        progress_to_report = progress_percent
                                        self.last_reported_progress = progress_percent
                                except (ValueError, IndexError):
                                    continue

                    if progress_to_report is not None:
                        # 缩放到本阶段区间
                        scaled = self.start_percent + (progress_to_report / 100.0) * self.percent_span
                        # 判断本阶段是否认为“阶段完成”
                        if progress_to_report >= 100.0 and self.finish_on_progress100:
                            # 直接阶段结束
                            self.callback(scaled, True, self.iter_num)
                            self.completed = True
                            # 不再继续 CSV 检测
                            return
                        else:
                            # 还未到 progress100 或者不 finish_on_progress100: 常规上报
                            # is_completed_flag 只有在 CSV 完成（第二阶段）或者 finish_on_progress100=True 且 progress100 时才为 True
                            self.callback(scaled, False, self.iter_num)
            except (FileNotFoundError, PermissionError):
                break

            # 2) 如果本阶段不 finish_on_progress100，则尝试检测 CSV 完成情况
            if not self.finish_on_progress100 and not self.csv_completion_reported:
                all_exist = True
                for name in self.EXPECTED_CSV_NAMES:
                    if not os.path.exists(os.path.join(folder, name)):
                        all_exist = False
                        break
                if all_exist:
                    # 等待 finalize
                    time.sleep(self.csv_finalize_wait)
                    still_all_exist = all(os.path.exists(os.path.join(folder, name)) for name in self.EXPECTED_CSV_NAMES)
                    if still_all_exist:
                        # 阶段真正完成
                        self.csv_completion_reported = True
                        self.completed = True
                        # 缩放到本阶段末尾：start+span
                        scaled = self.start_percent + self.percent_span
                        self.callback(scaled, True, self.iter_num)
        # 循环结束
        return

def monitor(params, iter_cnt=None):
    """
    串联监控 Job-Mises 和 Job-Deflection:
    - 先等待并监控 Job-Mises.sta，当其进度到 100% 时即视为阶段1完成（占总进度的 0-50%）。
    - 再等待并监控 Job-Deflection.sta，当其 CSV 全部生成后视为阶段2完成（占总进度的 50-100%）。
    - iter_cnt为当前迭代次数
    """
    folder_to_watch = params["output"]["dir"]
    # 第一阶段文件名
    mises_file = os.path.join(folder_to_watch, "Job-Mises.sta")
    # 第二阶段文件名
    deflection_file = os.path.join(folder_to_watch, "Job-Deflection.sta")

    # 第一阶段 callback：把 progress 缩放到 [0,50]
    def callback_mises(progress, is_completed, iter_num):
        if iter_num is None:
            # progress 已是缩放后百分比
            if not is_completed:
                if progress <= 50.0:
                    print(f"进度: {progress:.2f}%")
            else:
                # 阶段1完成的提示
                print("应力分析已完成，即将开始挠度分析...")
        else:
            if not is_completed:
                if progress <= 50.0:
                    print(f"[第 {iter_num} 轮迭代] 进度: {progress:.2f}%")
            else:
                # 阶段1完成的提示
                print(f"[第 {iter_num} 轮迭代] 应力分析已完成，即将开始挠度分析...")

    # 第二阶段 callback：把 progress 缩放到 [50,100]
    def callback_deflection(progress, is_completed, iter_num):
        if iter_num is None:
            # progress 已是缩放后百分比
            if not is_completed:
                print(f"进度: {progress:.2f}%")
            else:
                print("挠度分析已完成，正在处理结算结果...")
        else:
            if not is_completed:
                print(f"[第 {iter_num} 轮迭代] 进度: {progress:.2f}%")
            else:
                print(f"[第 {iter_num} 轮迭代] 挠度分析已完成，正在处理结算结果...")

    if iter_cnt is None:
        print("等待计算开始...")
    else:
        print(f"[第 {iter_cnt} 轮迭代] 等待计算开始...")

    while not os.path.exists(mises_file):
        time.sleep(0.5)

    if iter_cnt is None:
        print("开始应力分析")
    else:
        print(f"[第 {iter_cnt} 轮迭代] 开始应力分析")

    handler1 = JobFileHandler(
        mises_file, callback_mises, iter_num=iter_cnt,
        progress_threshold=0.5, csv_finalize_wait=1.0,
        start_percent=0.0, percent_span=50.0,
        finish_on_progress100=True  # 见说明：当 progress>=100% 时直接结束阶段1
    )
    # 直接 blocking 监控；如果希望借助 Observer，也可类似原逻辑，但此处直接调用 monitor_file()
    handler1.last_position = os.path.getsize(mises_file)
    handler1.monitor_file()

    # 进入第二阶段
    # 等待稍许时间或直接开始等待第二文件
    if iter_cnt is None:
        print("等待挠度分析开始...")
    else:
        print(f"[第 {iter_cnt} 轮迭代] 等待挠度分析开始...")

    while not os.path.exists(deflection_file):
        time.sleep(0.5)

    if iter_cnt is None:
        print("开始挠度分析")
    else:
        print(f"[第 {iter_cnt} 轮迭代] 开始挠度分析")

    handler2 = JobFileHandler(
        deflection_file, callback_deflection, iter_num=iter_cnt,
        progress_threshold=0.5, csv_finalize_wait=1.0,
        start_percent=50.0, percent_span=50.0,
        finish_on_progress100=False  # 阶段2需要等 CSV 完成才算真正结束
    )
    handler2.last_position = os.path.getsize(deflection_file)
    handler2.monitor_file()