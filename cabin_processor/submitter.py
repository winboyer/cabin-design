from cabin_processor.param_validation import ParamValidationError
from cabin_processor.generator import Generator
import cabin_script.monitor as monitor
import cabin_script.auto as auto
import pandas as pd
import cabin_result.odb_result as odb_result
import shutil, threading, time, os, json

# 执行计算
class Submitter(Generator):
    def __init__(self, params:dict, section:list=None, iter_cnt=None, allowable_mises: float = None,
                 allowable_deflection: float=None):
        super().__init__(params, section)
        self._generate_script()

        self.beam_result = pd.DataFrame()  # 梁柱应力挠度结果，是一个DataFrame
        self.plate_result = 0.0  # 钢板最大应力
        self.iter_cnt = iter_cnt # 当前迭代次数，默认为空
        self.allowable_deflection = allowable_deflection # 允许的最大挠度
        self.allowable_mises = allowable_mises # 允许的最大应力

        # 首先检测是否有abaqus
        abaqus_error = self._check_abaqus()
        if abaqus_error:
            raise ParamValidationError(abaqus_error)
        self.is_running = 0 #计算状态

    # 用于提交作业进行计算
    def put_into_job(self) -> None:
        errors = self._check_abaqus() + self._check_running()
        if errors:
            raise ParamValidationError(errors)

        # 更改程序计算状态
        self.is_running = 1
        odb_result.delete_file(self.params)

        # 添加计算脚本语句
        end = f"""
mdb.jobs['Job-Mises'].submit(consistencyChecking=OFF)   
mdb.jobs['Job-Mises'].waitForCompletion()  #一定不要在GUI中添加这段代码，否则会导致卡死
mdb.jobs['Job-Deflection'].submit(consistencyChecking=OFF)   
mdb.jobs['Job-Deflection'].waitForCompletion()  #一定不要在GUI中添加这段代码，否则会导致卡死
mdb.saveAs(pathName="{self.params["output"]["dir"]}" + '/cabin_model')
"""
        self.script += end
        # 添加后处理语句
        process_result = odb_result.get_part_node_coord_csv(self.params) + odb_result.get_result_u(
            self.params) + odb_result.get_result_s(self.params)
        self.script += process_result

        # 写入脚本文件
        self.write_to_py()

        # 计算线程
        t_job = threading.Thread(
            target=self._run_put_job,
            args=()
        )
        t_job.daemon = True

        # 监测线程
        t_moni = threading.Thread(
            target=self._run_monitor,
            args=()
        )
        t_moni.daemon = True

        # 当计算完毕后将结果写入文件
        t_trigger = threading.Thread(
            target=self._generate_sum,
            args=(t_moni,),
        )
        t_trigger.daemon = True

        # 启动线程，同时等待线程结束
        start_time = time.perf_counter()  # 记录开始时间
        t_job.start()
        t_moni.start()
        t_trigger.start()
        t_job.join()
        t_moni.join()
        t_trigger.join()

        # 传递最大应力结果
        self._update_result()

        elapsed = time.perf_counter() - start_time
        minutes = int(elapsed // 60)
        seconds = elapsed % 60

        # 汇总本次计算结果
        self._generate_txt()

        if self.iter_cnt is None:
            print("分析已完成")
            print(f"分析总耗时: {elapsed:.2f} 秒（{minutes}分{seconds:.2f}秒）\n")
        else:
            print(f"[第 {self.iter_cnt} 轮迭代] 分析已完成")
            print(f"[第 {self.iter_cnt} 轮迭代] 分析总耗时: {elapsed:.2f} 秒（{minutes}分{seconds:.2f}秒）\n")

    # 用于检查abaqus是否存在
    @staticmethod
    def _check_abaqus() -> list:
        error = []
        if not shutil.which("abaqus"):
            error.append("未检测到abaqus安装路径，无法执行计算")
        return error

    # 用于检查计算情况
    def _check_running(self) -> list:
        error = []
        if self.is_running == 1:
            error.append( "已提交作业进行计算，请勿重复提交")
        return error

    # 用于存放最终的梁柱钢板计算结果
    def _update_result(self) -> None:
        frame_csv_path = self.params["output"]["dir"] + '\\frame_sum.csv'
        plate_csv_path = self.params["output"]["dir"] + '\\S_CABIN_PLATES.csv'

        df = pd.read_csv(frame_csv_path)
        # 按type分组，并找到每组中max_mises最大的行
        self.beam_result = df.loc[df.groupby('type')['max_mises'].idxmax()]
        # 重置索引
        self.beam_result = self.beam_result.reset_index(drop=True)

        df = pd.read_csv(plate_csv_path)
        self.plate_result = df['Mises'].max()

    # 计算线程
    def _run_put_job(self) -> None:
        try:
            auto.put_job(self.params)
        finally:
            self.is_running = 0

    # 监控线程
    def _run_monitor(self) -> None:
        try:
            monitor.monitor(self.params, self.iter_cnt)
        finally:
            self.is_running = 0

    # 汇总csv结果
    def _generate_sum(self, monitor_thread) -> None:
        # 等待监测线程结束
        monitor_thread.join()
        # 计算完成后再执行两次 merge
        odb_result.merge_nodes_displacements(self.params, 'CABIN_FRAME_nodes.csv', 'U_CABIN_FRAME.csv',
                                          'U_CABIN_FRAME_PROCESSED.csv')
        odb_result.merge_nodes_displacements(self.params, 'CABIN_PLATES_nodes.csv', 'U_CABIN_PLATES.csv',
                                          'U_CABIN_PLATES_PROCESSED.csv')
        odb_result.process_frame_parts_by_element_with_locate(self.parts_info, self.params)

    # 生成本次计算的txt文档
    def _generate_txt(self) -> None:
        """
        生成计算报告 TXT 文档，保存到 self.params["output"]["dir"]。
        """
        out_dir = self.params.get("output", {}).get("dir")
        if not out_dir:
            raise ValueError("输出目录未设置: self.params['output']['dir'] 为空")
        os.makedirs(out_dir, exist_ok=True)
        # 决定标题：本次计算结果 或 第X次迭代结果
        if getattr(self, "iter_cnt", None) is None:
            title_iter = "本次计算结果"
        else:
            title_iter = f"第{self.iter_cnt}次迭代结果"

        # 1. 读取 FRAME_SUM.csv
        frame_csv_path = os.path.join(out_dir, "FRAME_SUM.csv")
        if not os.path.isfile(frame_csv_path):
            raise FileNotFoundError(f"找不到 FRAME_SUM.csv: {frame_csv_path}")
        df_frame = pd.read_csv(frame_csv_path)

        # 要求列: 'type', 'part_id', 'max_mises', 'locate', 'max_deflection', 'direction'
        required_cols = ["type", "part_id", "max_mises", "locate", "max_deflection", "direction"]
        for c in required_cols:
            if c not in df_frame.columns:
                raise KeyError(f"FRAME_SUM.csv 缺少列: {c}")

        # 按 type 分组，找最大 max_mises 对应行
        frame_groups = df_frame.groupby("type", as_index=False)
        max_mises_rows = []
        for t, grp in frame_groups:
            # 找该组中 max_mises 最大的行
            row = grp.loc[grp["max_mises"].idxmax()]
            max_mises_rows.append({
                "type": t,
                "part_id": row["part_id"],
                "max_mises": float(row["max_mises"]),
                "locate": row["locate"]
            })
        # 同理最大挠度
        max_defl_rows = []
        for t, grp in frame_groups:
            row = grp.loc[grp["max_deflection"].idxmax()]
            max_defl_rows.append({
                "type": t,
                "part_id": row["part_id"],
                "max_deflection": float(row["max_deflection"]),
                "direction": row["direction"]
            })

        # 2. 读取 S_CABIN_PLATES.csv，找到 Mises 最大值
        plate_csv_path = os.path.join(out_dir, "S_CABIN_PLATES.csv")
        if not os.path.isfile(plate_csv_path):
            raise FileNotFoundError(f"找不到 S_CABIN_PLATES.csv: {plate_csv_path}")
        df_plate = pd.read_csv(plate_csv_path)
        if "Mises" not in df_plate.columns:
            raise KeyError("S_CABIN_PLATES.csv 缺少列: 'Mises'")
        max_mises_plate = df_plate["Mises"].max()

        # 3. 读取 steel_usage.json
        steel_json_path = os.path.join(out_dir, "steel_usage.json")
        if not os.path.isfile(steel_json_path):
            raise FileNotFoundError(f"找不到 steel_usage.json: {steel_json_path}")
        with open(steel_json_path, 'r', encoding='utf-8') as f:
            steel_usage = json.load(f)
        # steel_usage 结构示例如题中所示

        # 4. self.section
        # 预期 self.section = {
        #    "main_beam_column": "...",
        #    "cir_main_column": "...",
        #    "cir_secd_column": "...",
        #    "cir_sup_column": "..."
        # }
        section_map = getattr(self, "section", {})
        # 构件类别中文对应
        type_map_cn = {
            "main_beam_column": "框架梁",
            "cir_main_column": "环向主梁",
            "cir_secd_column": "环向次梁",
            "cir_sup_column": "环向支撑梁"
        }
        # 5. allowable
        allowable_mises = getattr(self, "allowable_mises", None)
        allowable_deflection = getattr(self, "allowable_deflection", None)

        # 准备写入文件
        report_path = os.path.join(out_dir, "REPORT.txt")
        with open(report_path, 'w', encoding='utf-8') as fw:
            # 1. 概述
            if self.iter_cnt is not None:
                fw.write(f"{title_iter}\n\n")

            # 2. 截面选型
            fw.write("--------------------------截面选型--------------------------\n")
            # 构造表格：根据 type_map_cn 顺序输出
            headers = ["构件类别", "当前截面类型"]
            # 计算列宽
            col1_width = max(len(headers[0]), max(len(type_map_cn[k]) for k in type_map_cn))
            col2_width = max(len(headers[1]), max(len(str(section_map.get(k, ""))) for k in type_map_cn))
            # 分隔线
            sep = "+" + "-" * (col1_width + 2) + "+" + "-" * (col2_width + 2) + "+\n"
            # 写表头
            fw.write(sep)
            fw.write(f"| {'构件类别'.ljust(col1_width)} | {'当前截面类型'.ljust(col2_width)} |\n")
            fw.write(sep)
            for key in ["main_beam_column", "cir_main_column", "cir_secd_column", "cir_sup_column"]:
                cn = type_map_cn.get(key, key)
                prof = section_map.get(key, "-")
                fw.write(f"| {cn.ljust(col1_width)} | {str(prof).ljust(col2_width)} |\n")
            fw.write(sep)
            fw.write("\n\n")


            # 3. 构件最大应力分析
            fw.write("--------------------------构件最大应力分析--------------------------\n")
            # 表头: 构件类别 | 构件ID | 当前截面 | 最大应力(MPa) | 超出(%)
            headers = ["构件类别", "构件ID", "当前截面", "最大应力(MPa)", "超出(%)"]
            # 先收集所有行数据到 list of dict
            rows = []
            # 使用 max_mises_rows: list of dict with keys type, part_id, max_mises, locate
            for item in max_mises_rows:
                part_id = item["part_id"]
                max_m = item["max_mises"]
                current_section = "-"
                if item["type"] in type_map_cn.values():
                    # 找到对应 key
                    for k, v in type_map_cn.items():
                        if v == item["type"]:
                            current_section = section_map.get(k, "-")
                            break
                else:
                    # 假设 type 列为与 section_map 的 key 相同
                    if item["type"] in section_map:
                        current_section = section_map[item["type"]]
                    else:
                        # 否则记录原始
                        current_section = "-"
                # 计算超出比例
                exceed_str = "-"
                if allowable_mises is not None:
                    try:
                        allowable = float(allowable_mises)
                        if max_m > allowable:
                            pct = (max_m - allowable) / allowable * 100.0
                            exceed_str = f"{pct:.2f}"
                        else:
                            exceed_str = "-"
                    except Exception:
                        exceed_str = "-"
                rows.append({
                    "构件类别": item["type"],
                    "构件ID": str(part_id),
                    "当前截面": str(current_section),
                    "最大应力(MPa)": f"{max_m:.3f}",
                    "超出(%)": exceed_str
                })
            # 计算列宽
            col_widths = {}
            for h in headers:
                col_widths[h] = len(h)
            for row in rows:
                for h in headers:
                    col_widths[h] = max(col_widths[h], len(row[h]))
            # 构造分隔线
            sep = "+" + "+".join("-" * (col_widths[h] + 2) for h in headers) + "+\n"
            # 写表头
            fw.write(sep)
            fw.write("| " + " | ".join(h.ljust(col_widths[h]) for h in headers) + " |\n")
            fw.write(sep)

            # 写行，按某种顺序：可按超出降序，也可保持原顺序；此处按超出是否为 '-' 先后，再值降序
            def sort_key(k):
                if k["超出(%)"] == "-":
                    return 1, 0
                else:
                    try:
                        return 0, -float(k["超出(%)"])
                    except:
                        return 1, 0

            rows_sorted = sorted(rows, key=sort_key)
            for r in rows_sorted:
                fw.write("| " + " | ".join(r[h].ljust(col_widths[h]) for h in headers) + " |\n")
            fw.write(sep)
            fw.write("\n\n")

            # 4.构件最大挠度分析
            fw.write("--------------------------构件最大挠度分析--------------------------\n")
            # 表头: 构件类别 | 构件ID | 当前截面 | 最大挠度 | 超出(%)
            headers = ["构件类别", "构件ID", "当前截面", "最大挠度", "超出(%)"]
            rows = []
            # 使用 max_defl_rows: list of dict with keys type, part_id, max_deflection, direction
            for item in max_defl_rows:
                part_id = item["part_id"]
                max_d = item["max_deflection"]
                # 获取当前截面，逻辑与应力部分一致
                current_section = "-"
                if item["type"] in type_map_cn.values():
                    for k, v in type_map_cn.items():
                        if v == item["type"]:
                            current_section = section_map.get(k, "-")
                            break
                else:
                    if item["type"] in section_map:
                        current_section = section_map[item["type"]]
                    else:
                        current_section = "-"
                # 计算超出比例，仅当 allowable_deflection 不为 None 且可解析时
                exceed_str = "-"
                if allowable_deflection is not None:
                    try:
                        allowable = float(allowable_deflection)
                        if max_d > allowable:
                            pct = (max_d - allowable) / allowable * 100.0
                            exceed_str = f"{pct:.2f}"
                        else:
                            exceed_str = "-"
                    except Exception:
                        exceed_str = "-"
                rows.append({
                    "构件类别": item["type"],
                    "构件ID": str(part_id),
                    "当前截面": str(current_section),
                    "最大挠度": f"{max_d:.5f}",
                    "超出(%)": exceed_str
                })

            # 计算列宽
            col_widths = {h: len(h) for h in headers}
            for row in rows:
                for h in headers:
                    col_widths[h] = max(col_widths[h], len(row[h]))
            # 构造分隔线
            sep = "+" + "+".join("-" * (col_widths[h] + 2) for h in headers) + "+\n"
            # 写表头
            fw.write(sep)
            fw.write("| " + " | ".join(h.ljust(col_widths[h]) for h in headers) + " |\n")
            fw.write(sep)

            # 排序：超出降序在前，无超出的在后
            def sort_key(j):
                if j["超出(%)"] == "-":
                    return 1, 0
                else:
                    try:
                        return 0, -float(j["超出(%)"])
                    except:
                        return 1, 0

            rows_sorted = sorted(rows, key=sort_key)
            for r in rows_sorted:
                fw.write("| " + " | ".join(r[h].ljust(col_widths[h]) for h in headers) + " |\n")
            fw.write(sep)
            fw.write("\n\n")

            # 5. 钢板最大应力
            fw.write("--------------------------钢板最大应力--------------------------\n")
            headers = ["项目", "数值"]
            # 仅一行: 最大应力值 | {value} MPa
            val_str = f"{max_mises_plate:.3f} MPa"
            col1 = len(headers[0])
            col2 = max(len(headers[1]), len(val_str))
            sep = "+" + "-" * (col1 + 2) + "+" + "-" * (col2 + 2) + "+\n"
            fw.write(sep)
            fw.write(f"| {headers[0].ljust(col1)} | {headers[1].ljust(col2)} |\n")
            fw.write(sep)
            fw.write(f"| {'最大应力值'.ljust(col1)} | {val_str.ljust(col2)} |\n")
            fw.write(sep)
            fw.write("\n\n")

            # 6. 钢材用量及焊点统计
            fw.write("--------------------------钢材用量及焊点统计--------------------------\n")
            # 6.1 型材用量
            fw.write("型材用量\n")
            headers = ["型材", "总长度(m)", "单位重量(kg/m)", "总重量(kg)"]
            # 收集所有 dict 类型的条目，忽略 'steel_plate' and fields非dict，或仅 include dict 且非 'steel_plate'
            rows = []
            for k, v in steel_usage.items():
                if isinstance(v, dict) and k != "steel_plate":
                    total_length = v.get("total_length_m", "")
                    unit_w = v.get("unit_weight_kg/m", "")
                    total_w = v.get("total_weight_kg", "")

                    # 格式化数字为保留两位小数或原样
                    def fmt(x):
                        try:
                            return f"{float(x):.2f}"
                        except:
                            return str(x)

                    rows.append({
                        "型材": k,
                        "总长度(m)": fmt(total_length),
                        "单位重量(kg/m)": fmt(unit_w),
                        "总重量(kg)": fmt(total_w)
                    })
            # 计算列宽
            col_widths = {h: len(h) for h in headers}
            for row in rows:
                for h in headers:
                    col_widths[h] = max(col_widths[h], len(row[h]))
            sep = "+" + "+".join("-" * (col_widths[h] + 2) for h in headers) + "+\n"
            fw.write(sep)
            fw.write("| " + " | ".join(h.ljust(col_widths[h]) for h in headers) + " |\n")
            fw.write(sep)
            for row in rows:
                fw.write("| " + " | ".join(row[h].ljust(col_widths[h]) for h in headers) + " |\n")
            fw.write(sep)
            fw.write("\n")

            # 6.2 钢板统计
            fw.write("钢板用量统计\n")
            headers = ["项目", "总面积(m²)", "总体积(m³)", "总重量(kg)"]
            plate_info = steel_usage.get("steel_plate", {})
            area = plate_info.get("total_area_m", "")
            vol = plate_info.get("total_volume_m^3", "")
            w_plate = plate_info.get("total_weight_kg", "")

            # 格式化
            def fmt(x):
                try:
                    return f"{float(x):.6f}" if isinstance(x, (int, float)) else str(x)
                except:
                    return str(x)

            val_area = fmt(area)
            val_vol = fmt(vol)
            val_w = fmt(w_plate)
            # 可能为负，按原样输出
            col1 = len(headers[0])
            col2 = max(len(headers[1]), len(val_area))
            col3 = max(len(headers[2]), len(val_vol))
            col4 = max(len(headers[3]), len(val_w))
            sep = "+" + "-" * (col1 + 2) + "+" + "-" * (col2 + 2) + "+" + "-" * (col3 + 2) + "+" + "-" * (
                        col4 + 2) + "+\n"
            fw.write(sep)
            fw.write(
                f"| {headers[0].ljust(col1)} | {headers[1].ljust(col2)} | {headers[2].ljust(col3)} | {headers[3].ljust(col4)} |\n")
            fw.write(sep)
            fw.write(
                f"| {'钢板'.ljust(col1)} | {val_area.ljust(col2)} | {val_vol.ljust(col3)} | {val_w.ljust(col4)} |\n")
            fw.write(sep+"\n\n")

            # 6.3 焊点数量
            fw.write("焊点数量\n")
            headers = ["项目", "数量"]
            weld_count = steel_usage.get("wield_points", steel_usage.get("weld_points", None))
            weld_str = str(weld_count) if weld_count is not None else "-"
            col1 = len(headers[0])
            col2 = max(len(headers[1]), len(weld_str))
            sep = "+" + "-" * (col1 + 2) + "+" + "-" * (col2 + 2) + "+\n"
            fw.write(sep)
            fw.write(f"| {headers[0].ljust(col1)} | {headers[1].ljust(col2)} |\n")
            fw.write(sep)
            fw.write(f"| {'焊点总数'.ljust(col1)} | {weld_str.ljust(col2)} |\n")
            fw.write(sep)
            fw.write("\n")
        # 方法结束，TXT 文件已写入
        # 如果需要，可返回文件路径


