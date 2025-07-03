import copy, os, time, builtins
import pandas as pd
from datetime import datetime
from cabin_processor.submitter import Submitter
from cabin_result.log import print_to_log
builtins.print = print_to_log


# 构件迭代
class PartsIterator:
    def __init__(self, base_params: dict, base_dir: str, default_section_list: list=None,
                 allowable_mises: float = 335.0, allowable_deflection: float = 0.004, max_iter: int = 10,
    ):
        """
        base_params: 基础参数字典模板
        base_dir: 所有迭代工作目录的根路径
        default_section_list: Processor 默认使用的截面列表
        allowable_mises: 允许的最大应力阈值（MPa）
        max_iter: 最大迭代次数
        """
        if default_section_list is None:
            default_section_list = ["SHS 150x4", "HM 150x100", "HN 100x50", "C 80x40x20x2.5"]

        self.over_limit_df = pd.DataFrame()
        self._base_params = copy.deepcopy(base_params)
        self._base_dir = base_dir
        self._allowable_mises = allowable_mises
        self._allowable_deflection = allowable_deflection
        self._max_iter = max_iter
        self.final_df = pd.DataFrame()

        # 创建基础目录
        os.makedirs(self._base_dir, exist_ok=True)

        # 截面选项，每种截面类型按照理论重量从前往后排序
        self._section_options = {
            "cir_sup_beam": [
                "C 80x40x20x2.5", "C 80x40x20x3", "C 100x50x20x2.5", "C 120x50x20x2.5", "C 120x60x20x2.5",
                "C 100x50x20x3", "C 120x70x20x2.5", "C 120x50x20x3", "C 120x60x20x3", "C 200x50x20x2.5",
                "C 120x70x20x3", "C 180x70x20x2.5", "C 200x60x20x2.5", "C 220x60x20x2.5", "C 200x70x20x2.5",
                "C 180x60x20x3", "C 200x50x20x3", "C 180x70x20x3", "C 200x60x20x3", "C 200x70x20x3"
            ],
            "main_beam_column": [
                "SHS 150x4", "SHS 150x5", "SHS 150x6", "SHS 150x8"
            ],
            "cir_main_beam": [
                "HN 150x75", "HM 150x100", "HW 150x150"
            ],
            "cir_secd_beam": [
                "HN 100x50", "HW 100x100", "HN 125x60", "HW 125x125"
            ]
        }


        self._type_to_name = {}
        for category, opts in self._section_options.items():
            for opt in opts:
                key = opt.strip().strip('"').strip("'")
                self._type_to_name[key] = category

        # 存放类别键，顺序对应 Processor 构造时传入的 section 列表顺序
        self._category_order = []
        """
        长成下面这个样子
        ['main_beam_column', 'cir_main_beam', 'cir_secd_beam', 'cir_sup_beam']
        """
        # 当前索引记录，也就是每种类别迭代到第几种了
        self._current_indices = {}
        """
        长成下面这个样子
        {
        "main_beam_column": 0,    # 当前使用该类别第0个截面
        "cir_main_beam": 2,       # 当前使用该类别第2个截面
        "cir_secd_beam": 1        # 当前使用该类别第1个截面
        }
        """

        # 遍历 default_section_list，找出所属类别及索引
        for section in default_section_list:
            sec_clean = section.strip().strip('"').strip("'") # 去掉引号
            category = self._type_to_name.get(sec_clean)
            if category in self._category_order:
                continue
            self._category_order.append(category)
            idx = self._section_options[category].index(sec_clean)
            self._current_indices[category] = idx

        # 记录历史：列表，每条记录为 dict: iteration, category, part_ids, from, to, prev_max_mises, ratio
        self.history = []

    def run(self):
        """
        开始迭代流程，返回最终 DataFrame，同时在 self.over_limit_df 中保存每次迭代的超限信息
        """
        # 用于收集所有迭代的超限记录，最后转 DataFrame
        records = []

        df = pd.DataFrame()
        start_time = time.perf_counter()  # 记录开始时间
        iter_i = 0 # 记录迭代轮次
        win_width = float(self._base_params["window"]["width"])
        for iter_i in range(self._max_iter):
            # 为本轮创建唯一子目录，目录附上时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            subdir = os.path.join(self._base_dir, f"iter_{win_width}_{iter_i}_{timestamp}")
            os.makedirs(subdir, exist_ok=False)

            # 生成本轮 params，拷贝 base_params 并设置 work_path
            params = copy.deepcopy(self._base_params)
            params["work_path"] = subdir

            # 生成截面列表，顺序对应 category_order
            section_list = [] # 找到当前的所有截面配置
            for category in self._category_order:
                opts = self._section_options[category]
                idx = self._current_indices.get(category, 0)
                if idx < 0 or idx >= len(opts):
                    raise IndexError(f"\n[窗宽 {win_width} 第 {iter_i} 轮迭代] 类别 {category} 的当前索引 {idx} 超出范围")
                section_list.append(opts[idx])

            # 实例化 Submitter 并运行计算
            job = Submitter(params, section=section_list, iter_cnt=iter_i, allowable_mises=self._allowable_mises,
                                  allowable_deflection=self._allowable_deflection)

            if iter_i == 0:
                print("开始迭代分析，参数如下：")
                print(f"舱体长度：{params['cabin_length']}mm")
                print(f"窗户宽度：{params['window']['width']}mm")
                print(f"舱体左侧窗户位置：{params['window']['left']['locate']}")
                print(f"舱体右侧窗户位置：{params['window']['right']['locate']}")
                print(f"舱体对侧窗户数量：{params['window']['offside']['num']}")
                print(f"\n[窗宽 {win_width} 第 {iter_i} 轮迭代] 创建目录 {subdir} 运行计算，初始截面配置: {section_list}")
            else:
                print(f"\n[窗宽 {win_width} 第 {iter_i} 轮迭代] 创建目录 {subdir} 运行计算，更新后的截面配置: {section_list}")

            # 开始进行计算
            job.put_into_job()

            # 获取结果 DataFrame
            df = job.beam_mises_result.copy()
            df['type_clean'] = df['type'].astype(str).str.strip().str.strip('"').str.strip("'")

            # 计算是否超限
            df['allowable'] = self._allowable_mises
            df['exceed'] = df['max_mises'] - df['allowable']

            # 获取全局最大应力
            global_max = df['max_mises'].max()

            # 筛选超限
            over_df = df[df['exceed'] > 0].copy()

            # 如果列表是空的那么就不迭代了直接退出了
            if over_df.empty:
                # 记录本轮没有超限的情况
                print(
                    f"[窗宽 {win_width} 第 {iter_i} 轮迭代] 所有构件满足允许应力 {self._allowable_mises} MPa，最大应力 {global_max:.3f} MPa。")
                records.append({
                    'iter': iter_i,
                    'status': 'all_under_limit',
                    'category': None,
                    'part_ids': None,
                    'from_type': None,
                    'to_type': None,
                    'prev_max_mises': global_max,
                    'ratio': None,
                    'message': f"所有构件满足允许应力，最大应力 {global_max:.3f} MPa"
                })
                # create_docx_from_multiple_folders(self._base_dir, f"窗宽{win_width}迭代结果汇总.docx")
                elapsed = time.perf_counter() - start_time
                minutes = int(elapsed // 60)
                seconds = elapsed % 60
                print(f"迭代计算总时长: {elapsed:.2f} 秒（{minutes}分{seconds:.2f}秒）")
                # 在 self 中保存 DataFrame
                self.over_limit_df = pd.DataFrame(records)
                self.final_df = df.drop(columns=['type_clean', 'allowable', 'exceed'])
                return

            # 否则就继续进行迭代
            # 按类别统计超限情况，无赋值 SettingWithCopyWarning
            categories = over_df['type_clean'].map(self._type_to_name)
            over_df = over_df.assign(category=categories)
            cats_over = over_df['category'].unique()

            category_to_chinese = {
                "cir_sup_beam": "环向支撑梁",
                "cir_main_beam": "环向主梁",
                "cir_secd_beam": "环向次梁",
                "main_beam_column": "框架梁柱"
            }
            chinese_categories = [category_to_chinese.get(cat, cat) for cat in cats_over]

            print(f"[窗宽 {win_width} 第 {iter_i} 轮迭代] 以下类别存在应力超限: {chinese_categories}")

            # 存储本轮升级信息，分类别处理
            upgrades = {}
            for category in cats_over:
                # 更新一下构件名称
                if category == "cir_sup_beam":
                    part_name = "环向支撑梁"
                elif category == "cir_main_beam":
                    part_name = "环向主梁"
                elif category == "cir_secd_beam":
                    part_name = "环向次梁"
                else:
                    part_name = "框架梁"

                rows = over_df[over_df['category'] == category]

                # 获取该类别中最大应力构件
                idx_max = rows['max_mises'].idxmax()
                worst_row = df.loc[idx_max]
                curr_type = worst_row['type_clean']
                part_ids = rows['part_id'].tolist()
                prev_mises = worst_row['max_mises']
                ratio = (prev_mises - self._allowable_mises) / self._allowable_mises
                opts = self._section_options.get(category, [])
                curr_idx = self._current_indices.get(category)
                if curr_idx is None or not opts:
                    print(f"[窗宽 {win_width} 第 {iter_i} 轮迭代] 警告: 类别 {category} 未找到索引或无选项，跳过升级。")
                    # 记录无法升级的情况
                    records.append({
                        'iter': iter_i,
                        'status': 'no_option',
                        'category': category,
                        'part_ids': part_ids,
                        'from_type': curr_type,
                        'to_type': None,
                        'prev_max_mises': prev_mises,
                        'ratio': ratio,
                        'message': f"类别 {category} 无可用选项，跳过升级"
                    })
                    continue

                # 决定迭代步长
                if curr_type.startswith('C '):
                    if ratio >= 0.05:
                        step = 7
                    elif ratio >= 0.40:
                        step = 5
                    elif ratio >= 0.25:
                        step = 4
                    elif ratio >= 0.10:
                        step = 3
                    elif ratio >= 0.05:
                        step = 2
                    else:
                        step = 1
                else:
                    step = 1
                new_idx = curr_idx + step
                if new_idx >= len(opts):
                    new_idx = len(opts) - 1
                    print(
                        f"[窗宽 {win_width} 第 {iter_i} 轮迭代] 警告: 类别 {category} 构件截面类型 '{curr_type}' 根据超出比例 {ratio:.2%} 需要跳跃 {step} 步，但已达最强选项，使用最后一个选项 '{opts[new_idx]}'")
                new_type = opts[new_idx]

                # 打印本类别超限详情及升级信息
                print(
                    f"[窗宽 {win_width} 第 {iter_i} 轮迭代] {part_name}中构件 {part_ids} 出现同类别构件中的最大应力，当前{part_name}截面类型 '{curr_type}' 最大应力 {prev_mises:.3f} MPa，超出 {ratio:.2%}。在下轮迭代中将被升级为 '{new_type}'")

                # 记录升级信息到 records
                records.append({
                    'iter': iter_i,
                    'status': 'over_limit',
                    'category': category,
                    'part_ids': part_ids,
                    'from_type': curr_type,
                    'to_type': new_type,
                    'prev_max_mises': prev_mises,
                    'ratio': ratio,
                    'message': f"从 '{curr_type}' 升级到 '{new_type}'"
                })

                # 记录升级
                upgrades[category] = (curr_idx, new_idx, curr_type, new_type, part_ids, prev_mises, ratio)

            # 若无可升级类别，则终止
            if not upgrades:
                print(f"[窗宽 {win_width} 第 {iter_i} 轮迭代] 未找到可升级类别，迭代结束。请检查设计或材料。")
                # 记录本轮无升级
                records.append({
                    'iter': iter_i,
                    'status': 'no_upgrade_possible',
                    'category': None,
                    'part_ids': None,
                    'from_type': None,
                    'to_type': None,
                    'prev_max_mises': None,
                    'ratio': None,
                    'message': "未找到可升级类别"
                })
                break

            # 执行所有类别的升级
            for category, info in upgrades.items():
                _, new_idx, curr_type, new_type, part_ids, prev_mises, ratio = info
                self.history.append({
                    'iter': iter_i,
                    'category': category,
                    'part_ids': part_ids,
                    'from': curr_type,
                    'to': new_type,
                    'prev_max_mises': prev_mises,
                    'ratio': ratio,
                })
                self._current_indices[category] = new_idx

            # 继续下一轮
        # 迭代结束后（达到最大次数或 break）
        # create_docx_from_multiple_folders(self._base_dir, f"窗宽{win_width}迭代结果汇总.docx")
        elapsed = time.perf_counter() - start_time
        minutes = int(elapsed // 60)
        seconds = elapsed % 60
        print(f"[窗宽 {win_width} 第 {iter_i} 轮迭代] 达到最大迭代次数或遇到无法升级情况，迭代结束")
        # 最后一轮结果
        if not df.empty:
            global_max = df['max_mises'].max()
            print(f"迭代计算结束：全局最大应力 {global_max:.3f} MPa。")
            # 可以记录最后一轮无超限或全局最大信息
            records.append({
                'iter': iter_i,
                'status': 'ended',
                'category': None,
                'part_ids': None,
                'from_type': None,
                'to_type': None,
                'prev_max_mises': global_max,
                'ratio': None,
                'message': f"迭代结束，全局最大应力 {global_max:.3f} MPa"
            })

        print(f"迭代计算总时长: {elapsed:.2f} 秒（{minutes}分{seconds:.2f}秒）")
        # 将收集的 records 转为 DataFrame 并赋给 self
        self.over_limit_df = pd.DataFrame(records)
        self.final_df = df.drop(columns=['type_clean', 'allowable', 'exceed'], errors='ignore')
        return