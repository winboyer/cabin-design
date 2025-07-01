from cabin_processor.param_validation import ParamValidationError
import cabin_script.compute as compute
import cabin_script.beam as beam
import cabin_script.assembly as assembly
import cabin_script.head as head
import cabin_script.job as job
import cabin_script.load as load
import cabin_script.parts as parts
import cabin_script.copy_model as copy_model
import cabin_result.material_summary as summary
from typing import Dict, Any, List
import os, json

# 脚本生成
class Generator:
    def __init__(self, params: dict, section=None):

        if section is None:
            section = ["SHS 150x4", "HM 150x100", "HN 100x50", "C 80x40x20x2.5"]

        # 先检查输入是否正确
        input_errors = self._check_input_params(params)
        if input_errors:
            raise ParamValidationError(input_errors)

        # 初始参数
        self.params = {
    "name": "Model-1",
    "output": {
        "dir": "F:\\CAE\\cube"
    },
    "parts": {
        "steel_material": "Q355C",
        "main_beam_column": {
            "type": section[0],
            "move": {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            },
            "a": 150.0,
            "b": 150.0,
            "c": 8.0,
            "description": "前面几个参数是在abaqus创建时需要进行的输入"
        },
        "cir_main_beam": {
            "type": section[1],
            "move": {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            },
            "a": 75.0,
            "b": 150.0,
            "c": 150.0,
            "d": 150.0,
            "e": 10.0,
            "f": 10.0,
            "g": 7.0,
            "description": "前面几个参数是在abaqus创建时需要进行的输入"
        },
        "cir_secd_beam": {
            "type": section[2],
            "move": 12.5,
            "a": 62.5,
            "b": 125.0,
            "c": 125.0,
            "d": 125.0,
            "e": 9.0,
            "f": 9.0,
            "g": 6.5,
            "description": "前面几个参数是在abaqus创建时需要进行的输入"
        },
        "cir_sup_beam": {
            "type": section[3],
            "move": 15.0,
            "a1": 120.0,
            "b1": 70.0,
            "c1": 20.0,
            "d1": 3.0,
            "a": 44.30555555555556,
            "b": 58.5,
            "c": -24.194444444444443,
            "d": 58.5,
            "e": -24.194444444444443,
            "f": -58.5,
            "g": 44.30555555555556,
            "h": -58.5,
            "i": 3.0,
            "description": "前面几个参数是C型钢参数，后面几个abaqus中要输入的坐标点的数值"
        }
    },
    "cabin": {
        "length": {
            "value": 12000.0,
            "axis_dis": 11850.0
        },
        "height": {
            "value": 3300.0,
            "axis_dis": 3150.0
        },
        "width": {
            "value": 3600.0,
            "axis_dis": 3450.0
        }
    },
    "dis": {
        "value": 1200.0,
        "side": {
            "num": 8,
            "left_locate": 5,
            "right_locate": 4,
            "axis_gap": 1350.0,
            "description": "num指的是面内不包含两端的侧面柱个数，axis_gap为留余宽度，locate用于定位窗户处于哪一个位置，值不能等于1"
        },
        "offside": {
            "num": {
                "num1": 3,
                "num2": 2,
                "num": 2,
                "description": "num指的是面内不包含两端的柱子数量，偶数适用于布置一扇窗户，窗户居中布置，奇数适用于布置两扇窗户"
            },
            "axis_gap": {
                "axis_gap1": 525.0,
                "axis_gap2": 1125.0,
                "axis_gap": 1125.0,
                "description": "如果axis_gap2=1800，则说明窗户太宽，无法在对侧布置窗户"
            },
            "description": "对侧柱个数及留余宽度"
        }
    },
    "door": {
        "height": {
            "value": 2210.0,
            "axis_dis": 2335.0,
            "description": "axis_dis指的是上下次梁的间距，为门高度加上次梁翼缘宽度"
        },
        "width": {
            "value": 910.0,
            "axis_dis": 1060.0,
            "description": "axis_dis指的是左右柱子轴线距离，为门宽度加柱宽度"
        },
        "ground_clear": {
            "value": 300.0,
            "axis_dis": 162.5,
            "description": "axis_dis是门下面的梁到底梁之间的周线距离，为real_value减去环向次梁翼缘宽度的一半"
        },
        "top_clear": {
            "axis_dis": 652.5
        }
    },
    "window": {
        "width": {
            "value": 1050.0,
            "axis_dis": 1200.0
        },
        "height": {
            "value": 1500.0,
            "axis_dis": 1625.0
        },
        "ground_clear": {
            "value": 900.0,
            "axis_dis": 762.5,
            "description": "value是窗底离室外地面高度，axis_dis轴线距离"
        },
        "top_clear": {
            "axis_dis": 762.5
        },
        "right": {
            "num": 1,
            "locate": 4
        },
        "left": {
            "num": 1,
            "locate": 5
        },
        "offside": {
            "num": 1
        }
    },
    "equip": {
        "length": {
            "value": 1950.0,
            "axis_dis": 1800.0
        },
        "width": {
            "value": 1050.0,
            "axis_dis": 900.0
        }
    },
    "sup": {
        "mid": {
            "num": 1,
            "gap": 812.5
        },
        "btm": {
            "num": 0,
            "gap": 381.25
        },
        "up": {
            "num": 0,
            "gap": 381.25
        },
        "top_side": {
            "num": 0,
            "gap": 562.5
        },
        "top_mid": {
            "num": 0,
            "gap": 600.0
        },
        "description": "记录的是每个位置环向支撑梁的数量以及距离"
    },
    "load": {
        "ratio": {
            "dead": 1.3,
            "live": 1.5,
            "pres": 1.25
        },
        "basic": {
            "dead": 0.005,
            "live": 0.002,
            "pres": 0.03
        }
    }
}
        self._pass_params(params)

        # 执行参数校验
        errors = self._check_params()
        if errors:
            raise ParamValidationError(errors)

        # 以下是公共属性
        self.parts_info = {} # 切分前的所有构件的信息
        self.section = {
            "main_beam_column": section[0],
            "cir_main_column": section[1],
            "cir_secd_column": section[2],
            "cir_sup_column": section[3]
        } # 截面选型
        self.parts_info_processed = {} # 切分后的每一个部件的对应信息
        self.script = ""  # 存放的是脚本内容
        self.steel_usage = {} # 钢材用量，包括焊点个数

        # 以下是内部属性
        self._processed_dict = []
        self._parts_info = {
            "frame_column": {},
            "frame_beam_l": {},
            "frame_beam_short": {},
            "frame_beam_w": {},
            "cir_beam": {},
            "cir_column": {},
            "cir_secd_beam": {},
            "door_beam": {},
            "door_left_beam": {},
            "equip_beam_w_top": {},
            "equip_beam_l": {},
            "equip_beam_w": {},
            "window_beam_side": {},
            "window_beam_offside": {},
            "sup_beam_d": {},
            "sup_beam_dl": {},
            "sup_beam_el": {},
            "sup_beam_ew": {},
            "sup_beam_ew_top": {},
            "sup_beam_left": {},
            "sup_beam_left_wl": {},
            "sup_beam_left_wr": {},
            "sup_beam_offside": {},
            "sup_beam_offside_w": {},
            "sup_beam_right": {},
            "sup_beam_right_wl": {},
            "sup_beam_right_wr": {},
            "sup_beam_top": {}
        } # 只用于与有限元模型对照

        # 生成脚本内容
        self._generate_script()

        # 生成用钢量
        self.steel_usage = summary.summarize_steel_usage(self.params, self.parts_info)
        self.steel_usage["wield_points"] = summary.summarize_wield_points(self.parts_info, self.parts_info_processed)

    # 用于将脚本内容写入py文件
    def write_to_py(self) -> None:
        # 写入文件
        script_path = os.path.join(self.params["output"]["dir"], "cube.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(self.script)
        self._write_to_json()

    # 用于传递传入的参数，计算其余参数
    def _pass_params(self, params) -> None:

        self.params["cabin"]["length"]["value"] = float(params["cabin_length"])

        self.params["window"]["width"]["value"] = float(params["window"]["width"])
        self.params["window"]["right"]["num"] = params["window"]["right"]["num"]
        self.params["window"]["left"]["num"] = params["window"]["left"]["num"]
        self.params["window"]["offside"]["num"] = params["window"]["offside"]["num"]

        self.params["window"]["right"]["locate"] = params["window"]["right"]["locate"]
        self.params["window"]["left"]["locate"] = params["window"]["left"]["locate"]
        self.params["output"]["dir"] = params["work_path"]

        self.params["dis"]["side"]["left_locate"] = self.params["window"]["left"]["locate"]
        self.params["dis"]["side"]["right_locate"] = self.params["window"]["right"]["locate"]

        # 自动设置梁间距
        self._set_sup_beam()

        self.params = compute.update_profile(self.params)
        self.params = compute.update_cir_main(self.params)

    # 用于切分构件获取梁单元切向信息
    def _split_parts(self) -> None:

        self._parts_info = compute.update_parts_info(self.params, self._parts_info)
        self.parts_info = beam.sort_all_parts(self._parts_info) # 去除外层嵌套
        self.parts_info = compute.update_offset(self.params, self.parts_info) # 添加构件偏置信息
        self.parts_info = compute.update_priority(self.parts_info)

        self._processed_dict = beam.split_segments_3d(self.parts_info)

        for part_id, info in self._processed_dict.items():
            part_id = compute.gen_id(info)
            self.parts_info_processed[part_id] = info

    # 将所有构件信息以及钢材消耗量等存写入JSON文件
    def _write_to_json(self) -> None:

        json_path = self.params["output"]["dir"] + r"\\params.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.params, f, ensure_ascii=False, indent=4)  # type: ignore[arg-type]

        json_path = self.params["output"]["dir"] + r"\\parts_info.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.parts_info, f, ensure_ascii=False, indent=4)  # type: ignore[arg-type]

        json_path = self.params["output"]["dir"] + r"\\steel_usage.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.steel_usage, f, ensure_ascii=False, indent=4)  # type: ignore[arg-type]

    # 用于生成脚本内容
    def _generate_script(self) -> None:
        # 确定参数无误后再分割构件
        self._split_parts()

        out_path = self.params["output"]["dir"]
        os.makedirs(out_path, exist_ok=True)
        cpu_num = os.cpu_count() - 1

        # 生成各部分脚本
        a = head.gen_head(self.params)
        b = parts.gen_material()
        c = parts.gen_profile(self.params)
        d = parts.gen_section(self.params)
        e = parts.gen_parts(self.params)
        f = assembly.gen_assem_main_beam_column(self.params) + assembly.gen_assem_cir_secd_beam(self.params)
        g = assembly.gen_assem_cir_main_beam(self.params)
        h = assembly.gen_assem_door_beam_h(self.params)
        i = assembly.gen_assem_sup_beam(self.params)
        j = assembly.gen_assem_top_sup_beam(self.params)
        k = assembly.gen_assem_top_sup_beam_ew(self.params)
        l = assembly.gen_assem_all_parts(self.params, self.parts_info_processed)
        m = beam.gen_all_parts_dir(self._processed_dict, self.params)
        n = job.gen_mesh(50.0) + assembly.gen_assem_plate(self.params) + assembly.gen_tie()
        o = job.gen_bc(self.params) + job.gen_step() + load.gen_load_g(self.params) + job.gen_job(cpu_num) + load.gen_surf(self.params)
        p = load.gen_pressure(self.params) + load.gen_dead_live_load(self.params) + job.gen_node_element_set()
        q = copy_model.copy_model(self.params, cpu_num)
        self.script = a + b + c + d + e + f + g + h + i + j + k + l + m + n + o + p + q

    # 用于检查输入参数
    @staticmethod
    def _check_input_params(input_params: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        # cabin_length: 长度，必须为正整数
        if "cabin_length" not in input_params:
            errors.append("缺少 'cabin_length' 参数。")
        else:
            val = input_params["cabin_length"]
            try:
                # 先尝试转换为整数
                cabin_length = int(val)
                if cabin_length <= 0:
                    errors.append(f"'cabin_length' 必须为正整数 (>0)，当前值: {val}")
            except (ValueError, TypeError):
                errors.append(f"'cabin_length' 必须是可转换为整数的值，且为正整数 (>0)；当前值: {val}")

        # window 整体必须存在且为 dict
        window = input_params.get("window")
        if window is None:
            errors.append("缺少 'window' 字段，应为 dict。")
        elif not isinstance(window, dict):
            errors.append("'window' 字段格式不正确，应为 dict。")
        else:
            # window.width: 视为长度，必须为正整数
            if "width" not in window:
                errors.append("缺少 'window.width' 参数。")
            else:
                val = window["width"]
                try:
                    width = int(val)
                    if width <= 0:
                        errors.append(f"'window.width' 必须为正整数 (>0)，当前值: {val}")
                except (ValueError, TypeError):
                    errors.append(f"'window.width' 必须是可转换为整数的值，且为正整数 (>0)；当前值: {val}")

            # 通用函数：检查 side 字段
            def check_side(side_name: str):
                side = window.get(side_name)
                if side is None:
                    errors.append(f"缺少 'window.{side_name}' 字段，应为 dict。")
                    return
                if not isinstance(side, dict):
                    errors.append(f"'window.{side_name}' 格式不正确，应为 dict。")
                    return
                # num: 数量，必须为整型且 >= 0
                if "num" not in side:
                    errors.append(f"缺少 'window.{side_name}.num' 参数。")
                    return
                num_val = side["num"]
                try:
                    num_int = int(num_val)
                    if num_int < 0:
                        errors.append(f"'window.{side_name}.num' 必须为非负整数 (>=0)，当前值: {num_val}")
                except (ValueError, TypeError):
                    errors.append(
                        f"'window.{side_name}.num' 必须是可转换为整数的值，且为非负整数 (>=0)；当前值: {num_val}")
                    return
                # 如果 num == 1，需要 locate：定位值，必须为整型且 >0
                if num_int == 1:
                    if "locate" not in side:
                        errors.append(f"当 'window.{side_name}.num' 为 1 时，缺少 'window.{side_name}.locate' 参数。")
                    else:
                        loc_val = side["locate"]
                        try:
                            loc_int = int(loc_val)
                            if loc_int <= 0:
                                errors.append(f"'window.{side_name}.locate' 必须为正整数 (>0)，当前值: {loc_val}")
                        except (ValueError, TypeError):
                            errors.append(
                                f"'window.{side_name}.locate' 必须是可转换为整数的值，且为正整数 (>0)；当前值: {loc_val}")

            check_side("offside")
            check_side("left")
            check_side("right")

        # 检查 work_path，必须为字符串，且路径存在
        if "work_path" not in input_params:
            errors.append("缺少 'work_path' 参数。")
        else:
            wp = input_params["work_path"]
            if not isinstance(wp, str):
                errors.append(f"'work_path' 必须为字符串类型，当前类型: {type(wp).__name__}；当前值: {wp}")
            else:
                if not os.path.exists(wp):
                    errors.append(f"'work_path' 对应的路径不存在: {wp}，请创建")

                elif not os.path.isdir(wp):
                   errors.append(f"'work_path' 应当是一个目录，但不是: {wp}")

        return errors

    # 用于检查计算参数
    def _check_params(self) -> list:

        errors = []
        # 1. 窗户宽度范围
        width = self.params["window"]["width"]["value"]
        if not (350.0 <= width <= 1350.0):
            errors.append("窗户宽度只能位于 350.0mm ~ 1350.0mm 之间，请修改。")
            return errors
        if width > 1250.0:
            errors.append("窗户宽度超过1250.0mm会导致钢板受力超限，请修改。")
            return errors

        # 2. 检测对侧窗户数量，特殊情况：offside num == 3 时最大宽度 866
        offside_num = self.params["window"]["offside"]["num"]
        if offside_num not in [0, 1, 2, 3]:
            errors.append("对侧窗户数量只能为0到3的整数，请修改")
        if offside_num == 3:
            width = self.params["window"]["width"]["value"]
            if width > 866.0:
                errors.append("当舱体对侧布置三扇窗户时，窗户宽度只能位于 350.0mm ~ 866.0mm 之间，请修改。")


        # 3. 检测左侧窗户数量与定位
        left_num = self.params["window"]["left"]["num"]
        if left_num not in [0, 1]:
            errors.append("左侧窗户只能为0或1，请修改")
        if left_num != 0:
            left_loc = self.params["dis"]["side"]["left_locate"]
            max_side = self.params["dis"]["side"]["num"]
            if not (2 <= left_loc <= max_side):
                errors.append(f"左侧窗户定位只能选择 2 ~ {max_side}，请重新选择。")

        # 4. 右侧窗户定位
        right_num = self.params["window"]["right"]["num"]
        if right_num not in [0, 1]:
            errors.append("右侧窗户只能为0或1，请修改")
        if right_num != 0:
            right_loc = self.params["dis"]["side"]["right_locate"]
            max_side = self.params["dis"]["side"]["num"]
            if not (2 <= right_loc <= max_side):
                errors.append(f"右侧窗户定位只能选择 2 ~ {max_side}，请重新选择。")

        # 5. 其他校验：检查 output.dir 是否存在
        try:
            out_dir = self.params["output"]["dir"]
            if not isinstance(out_dir, str) or not out_dir:
                errors.append("输出目录 output.dir 必须为非空字符串。")
        except KeyError:
            errors.append("缺少输出目录参数 output.dir。")
        except Exception as e:
            errors.append(f"输出目录参数格式错误: {e}")

        return errors

    # 用于自动调节支撑梁布置
    def _set_sup_beam(self) -> None:

        # 接下来记录变化的值，只需要取两者之间的最大值
        # 挨着门的那一侧
        win_left_change = (self.params["cabin"]["length"]["axis_dis"] - self.params["equip"]["width"]["axis_dis"] -
                          (self.params["dis"]["side"]["num"] * self.params["dis"]["value"]))
        changes = max(win_left_change, self.params["dis"]["value"])

        # 以下说的都是轴线距离，是窗宽加上150mm
        # 当窗宽超过750的时候，需要在顶部中间添加支撑梁
        if changes >= 900.0:
            self.params["sup"]["top_mid"]["num"] = 1
        # 当窗宽超过1100的时候，需要在窗户高度范围内添加两根支撑梁
        if changes >= 1250.0:
            self.params["sup"]["mid"]["num"] = 2
        # 当窗宽超过1200的时候，需要在窗户上下边缘添加一根支撑梁
        if changes >= 1300.0:
            self.params["sup"]["btm"]["num"] = 1
            self.params["sup"]["up"]["num"] = 1

        # 对于顶部边缘，只需要跟顶部中间的宽度限值进行比较然即可
        # 顶部边缘
        top_edge_fixed = self.params["cabin"]["width"]["axis_dis"] - self.params["dis"]["offside"]["axis_gap"][
            "axis_gap"]
        if top_edge_fixed>= 900.0:
            self.params["sup"]["top_side"]["num"] = 1