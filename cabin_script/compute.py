import re, copy, math, hashlib, json
import cabin_script.window as window

# 更新所有构件的截面参数，即在abaqus中输入的
def update_profile(params: dict):

    def get_type_and_size(param):
        # 该函数只能用于快速处理方钢管
        pattern = re.compile(r'[\sxX]+', re.IGNORECASE)
        result_dict = {}  # 存放最终结果的字典
        for part_name, part_type in param["parts"].items():
            if part_name != "steel_material":
                parts = re.split(pattern, part_type["type"].strip())
                type_ = parts[0]
                dimensions = list(map(float, parts[1:]))
                param_dict = {"type": type_}
                for i, dim in enumerate(dimensions):
                    key = chr(97 + i)  # 参数按照按a,b,c排序
                    param_dict[key] = dim
                result_dict[part_name] = param_dict
        return result_dict

        # 对于H型钢创建一个备用名称字典，存放参数

    h_alternative = {
        "HW 150x150": "HW 75x150x150x150x10x10x7",
        "HM 150x100": "HM 75x150x100x100x10x10x6",
        "HN 150x75": "HN 75x150x75x75x7x7x5",
        "HW 125x125": "HW 62.5x125x125x125x9x9x6.5",
        "HN 125x60": "HN 62.5x125x60x60x8x8x6",
        "HW 100x100": "HW 50x100x100x100x8x8x6",
        "HN 100x50": "HN 50x100x50x50x7x7x5"
    }
    # 接下来创建一个params的副本，将其中的H型钢的名称都替换掉
    params_copy = copy.deepcopy(params)
    params_copy["parts"]["cir_main_beam"]["type"] = h_alternative[params["parts"]["cir_main_beam"]["type"]]
    params_copy["parts"]["cir_secd_beam"]["type"] = h_alternative[params["parts"]["cir_secd_beam"]["type"]]
    result = get_type_and_size(params_copy)

    # 还需要将相关参数传入回原本的参数字典
    params["parts"]["main_beam_column"]["a"] = result["main_beam_column"]["a"]
    params["parts"]["main_beam_column"]["b"] = result["main_beam_column"]["a"]
    params["parts"]["main_beam_column"]["c"] = result["main_beam_column"]["b"]

    params["parts"]["cir_main_beam"]["a"] = result["cir_main_beam"]["a"]
    params["parts"]["cir_main_beam"]["b"] = result["cir_main_beam"]["b"]
    params["parts"]["cir_main_beam"]["c"] = result["cir_main_beam"]["c"]
    params["parts"]["cir_main_beam"]["d"] = result["cir_main_beam"]["d"]
    params["parts"]["cir_main_beam"]["e"] = result["cir_main_beam"]["e"]
    params["parts"]["cir_main_beam"]["f"] = result["cir_main_beam"]["f"]
    params["parts"]["cir_main_beam"]["g"] = result["cir_main_beam"]["g"]

    params["parts"]["cir_secd_beam"]["a"] = result["cir_secd_beam"]["a"]
    params["parts"]["cir_secd_beam"]["b"] = result["cir_secd_beam"]["b"]
    params["parts"]["cir_secd_beam"]["c"] = result["cir_secd_beam"]["c"]
    params["parts"]["cir_secd_beam"]["d"] = result["cir_secd_beam"]["d"]
    params["parts"]["cir_secd_beam"]["e"] = result["cir_secd_beam"]["e"]
    params["parts"]["cir_secd_beam"]["f"] = result["cir_secd_beam"]["f"]
    params["parts"]["cir_secd_beam"]["g"] = result["cir_secd_beam"]["g"]

    params["parts"]["cir_sup_beam"]["a1"] = result["cir_sup_beam"]["a"]
    params["parts"]["cir_sup_beam"]["b1"] = result["cir_sup_beam"]["b"]
    params["parts"]["cir_sup_beam"]["c1"] = result["cir_sup_beam"]["c"]
    params["parts"]["cir_sup_beam"]["d1"] = result["cir_sup_beam"]["d"]

    # 接下来考虑C型钢的处理，定义一个函数
    def get_c_type_params(param):
        # 函数接收的参数是刚刚计算得到的result
        # 首先计算形心位置
        a = param["parts"]["cir_sup_beam"]["a1"]
        b = param["parts"]["cir_sup_beam"]["b1"]
        c = param["parts"]["cir_sup_beam"]["c1"]
        d = param["parts"]["cir_sup_beam"]["d1"]
        x = ((a - 2 * d) * d * d / 2 + b * d * b + (c - d) * d * (b - d / 2) * 2) / (
                    (a - 2 * d) * d + b * d * 2 + (c - d) * d * 2)
        # 分别计算四个点的坐标
        x1 = b - x
        y1 = (a - d) / 2
        x2 = d / 2 - x
        y2 = (a - d) / 2
        x3 = d / 2 - x
        y3 = (d - a) / 2
        x4 = b - x
        y4 = (d - a) / 2
        param["parts"]["cir_sup_beam"]["a"] = x1
        param["parts"]["cir_sup_beam"]["b"] = y1
        param["parts"]["cir_sup_beam"]["c"] = x2
        param["parts"]["cir_sup_beam"]["d"] = y2
        param["parts"]["cir_sup_beam"]["e"] = x3
        param["parts"]["cir_sup_beam"]["f"] = y3
        param["parts"]["cir_sup_beam"]["g"] = x4
        param["parts"]["cir_sup_beam"]["h"] = y4
        param["parts"]["cir_sup_beam"]["i"] = d
        return param
    params = get_c_type_params(params)
    return params

# 更新舱体轴线距离
def update_axis_dis(params: dict):
    # 更新框架梁柱轴线距离
    params["cabin"]["length"]["axis_dis"] = params["cabin"]["length"]["value"] - params["parts"]["main_beam_column"][
        "a"]
    params["cabin"]["height"]["axis_dis"] = params["cabin"]["height"]["value"] - params["parts"]["main_beam_column"][
        "a"]
    params["cabin"]["width"]["axis_dis"] = params["cabin"]["width"]["value"] - params["parts"]["main_beam_column"]["a"]

    # 更新设备间轴线距离
    params["equip"]["length"]["axis_dis"] = params["equip"]["length"]["value"] - params["parts"]["main_beam_column"][
        "a"]
    params["equip"]["width"]["axis_dis"] = params["equip"]["width"]["value"] - params["parts"]["main_beam_column"]["a"]

    # 更新门窗轴线距离
    params["door"]["height"]["axis_dis"] = params["door"]["height"]["value"] + params["parts"]["cir_secd_beam"]["c"]
    params["door"]["width"]["axis_dis"] = params["door"]["width"]["value"] + params["parts"]["main_beam_column"]["a"]

    # 这个距离是轴线距离，是300 - 窗底次梁宽度一半 - 方钢管宽度一半
    params["door"]["ground_clear"]["axis_dis"] = params["door"]["ground_clear"]["value"] - \
                                                 params["parts"]["main_beam_column"]["a"] / 2 - \
                                                 params["parts"]["cir_secd_beam"]["c"] / 2
    params["door"]["top_clear"]["axis_dis"] = params["cabin"]["height"]["axis_dis"] - params["door"]["ground_clear"][
        "axis_dis"] - params["door"]["height"]["axis_dis"]

    params["window"]["height"]["axis_dis"] = params["window"]["height"]["value"] + params["parts"]["cir_secd_beam"]["c"]
    params["window"]["width"]["axis_dis"] = params["window"]["width"]["value"] + params["parts"]["main_beam_column"][
        "a"]

    # 这个距离是轴线距离，是900 - 窗底次梁宽度一半 - 方钢管宽度一半
    params["window"]["ground_clear"]["axis_dis"] = params["window"]["ground_clear"]["value"] - \
                                                   params["parts"]["main_beam_column"]["a"] / 2 - \
                                                   params["parts"]["cir_secd_beam"]["c"] / 2
    params["window"]["top_clear"]["axis_dis"] = params["cabin"]["height"]["axis_dis"] - \
                                                params["window"]["ground_clear"]["axis_dis"] - \
                                                params["window"]["height"]["axis_dis"]

    return params

def update_sup_beam_dis(params:dict) -> dict:

    # 更新环向支撑梁的间距
    # 注意，顶部的环向主梁个数的传递位于下一个函数中，因其计算涉及到环向主梁的个数
    params["sup"]["mid"]["gap"] = params["window"]["height"]["axis_dis"]/(params["sup"]["mid"]["num"]+1) if params["sup"]["mid"]["num"] != 0 else 0
    params["sup"]["btm"]["gap"] = params["window"]["ground_clear"]["axis_dis"]/(params["sup"]["btm"]["num"]+1) if params["sup"]["btm"]["num"] != 0 else 0
    params["sup"]["up"]["gap"] = params["window"]["top_clear"]["axis_dis"]/(params["sup"]["up"]["num"]+1) if params["sup"]["up"]["num"] != 0 else 0

    # 传递顶部环向支撑梁的间距。这个间距是距离环向次梁的间距
    params["sup"]["top_side"]["gap"] = params["dis"]["offside"]["axis_gap"]["axis_gap"] / 2 if \
    params["sup"]["top_side"]["num"] != 0 else 0
    params["sup"]["top_mid"]["gap"] = params["window"]["width"]["axis_dis"] / 2 if params["sup"]["top_mid"][
                                                                                       "num"] != 0 else 0

    # 更新顶部剖面的偏移量（指的是输入的坐标整体要往这个方向加上多少，所以都是正值，方钢管不需要）
    params["parts"]["cir_secd_beam"]["move"] = (params["parts"]["main_beam_column"]["a"]-params["parts"]["cir_secd_beam"]["b"])/2
    params["parts"]["cir_sup_beam"]["move"] = (params["parts"]["main_beam_column"]["a"]-params["parts"]["cir_sup_beam"]["a1"])/2

    return params

# 为装配部件生成一份唯一ID信息
def gen_id(part_dict, length=10):

    # 提取关键参数并创建规范化的字典
    key_data = {
        "type": part_dict["type"],
        "center_coord": {
            "x": round(part_dict["center_coord"]["x"], 6),  # 浮点数精度处理
            "y": round(part_dict["center_coord"]["y"], 6),
            "z": round(part_dict["center_coord"]["z"], 6)
        },
        "dir": part_dict["dir"],  # 假设方向值为整数
        "length": round(part_dict["length"], 6)  # 浮点数精度处理
    }


    json_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
    hash_obj = hashlib.sha256(json_str.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    id_chars = []
    for j in range(0, len(hash_hex), 6):
        if len(id_chars) >= length:
            break


        hex_chunk = hash_hex[j:j + 6]
        nums = int(hex_chunk, 16)
        while nums > 0 and len(id_chars) < length:
            nums, index = divmod(nums, 62)
            id_chars.append(chars[index])
    while len(id_chars) < length:
        id_chars.append('0')

    return ''.join(id_chars)

# 计算侧面柱子的个数以及间距
def update_cir_main(params):

    d = params["window"]["width"]["axis_dis"]

    # 假设留余宽度为gap，则舱体侧面柱间距乘以个数应当满足以下不等式：
    # 200 ≤ gap < d+200
    # 即 200 ≤ l-d×n < d+200
    # 解得 (l-200-d)/d < n ≤ (l-200)/d

    # 计算舱体长度减去设备间宽度
    side_l = params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]
    side_n = math.floor((side_l-200.0)/d)
    side_gap = side_l-side_n*d
    params["dis"]["side"]["num"] = side_n
    params["dis"]["side"]["axis_gap"] = side_gap

    # 假设留余宽度为gap，则舱体对侧柱间距乘以个数应当满足以下不等式：
    # 200 ≤ gap < d+200
    # 即 200 ≤ [l-d×(n+1)]/2 < d+200
    # 解得 (l-400)/d - 1 < n ≤ (l-400)/d + 1，也就是说此时 n 可以取两个数，也就是说可以有两种情况

    offside_l = params["cabin"]["width"]["axis_dis"]
    offside_n1 = math.floor((offside_l-400.0)/d) + 1
    offside_n2 = offside_n1-1
    offside_gap1 = (offside_l-(offside_n1-1)*d)/2
    offside_gap2 = (offside_l - (offside_n2 - 1) * d) / 2
    params["dis"]["offside"]["num"]["num1"] = offside_n1
    params["dis"]["offside"]["num"]["num2"] = offside_n2
    params["dis"]["offside"]["axis_gap"]["axis_gap1"] = offside_gap1
    params["dis"]["offside"]["axis_gap"]["axis_gap2"] = offside_gap2

    # 记录最终选择的数字是多少
    if params["window"]["offside"]["num"] == 0:
        # 此时对侧不布置窗户，从节省材料的原则上来讲选择较少的数量
        num = params["dis"]["offside"]["num"]["num2"]
        axis_gap = params["dis"]["offside"]["axis_gap"]["axis_gap2"]

    elif params["window"]["offside"]["num"] == 1 or params["window"]["offside"]["num"] == 3:
        # 此时舱体对侧存在一或者三扇窗户，使用 dis -> offside -> num -> num1 或 num2，使用其中的偶数
        num = params["dis"]["offside"]["num"]["num1"] if params["dis"]["offside"]["num"]["num1"] % 2 == 0 else \
            params["dis"]["offside"]["num"]["num2"]
        axis_gap = params["dis"]["offside"]["axis_gap"]["axis_gap1"] if params["dis"]["offside"]["num"][
                                                                            "num1"] % 2 == 0 else \
            params["dis"]["offside"]["axis_gap"]["axis_gap2"]

    else:
        # 此时舱体对侧存在两扇窗户，使用 dis -> offside -> num -> num1 或 num2，使用其中的奇数
        num = params["dis"]["offside"]["num"]["num1"] if params["dis"]["offside"]["num"]["num1"] % 2 != 0 else \
            params["dis"]["offside"]["num"]["num2"]
        axis_gap = params["dis"]["offside"]["axis_gap"]["axis_gap1"] if params["dis"]["offside"]["num"][
                                                                            "num1"] % 2 != 0 else \
            params["dis"]["offside"]["axis_gap"]["axis_gap2"]


    params["dis"]["offside"]["num"]["num"] = num
    params["dis"]["offside"]["axis_gap"]["axis_gap"] = axis_gap

    return params

# 获取并更新所有主梁的中点坐标、梁方向、长度
def update_parts_info(params, info_params):

####################-----------------以下是所有框架梁柱的更新-------------------############################

    # 首先是最外侧的框架柱
    # 计算其中点坐标
    frame_column_coord_list = []
    cen_y = params["cabin"]["height"]["axis_dis"] / 2
    for x in range(2):
        for z in range(2):
            frame_column_coord_list.append(
                (x * params["cabin"]["length"]["axis_dis"], cen_y, z * params["cabin"]["width"]["axis_dis"]))

    for coord in frame_column_coord_list:

        column = {
            "type": params["parts"]["main_beam_column"]["type"],
            "center_coord": {
                "x": coord[0],
                "y": coord[1],
                "z": coord[2]
            },
            "dir": {
                "x": 0,
                "y": 1,
                "z": 0
            },
            "length": params["cabin"]["height"]["axis_dis"],
        }
        part_id = gen_id(column)
        info_params["frame_column"][part_id] = column

    # 额外计算设备间相关框架柱以及门框架柱
    # 首先是门框架柱
    column = {
        "type": params["parts"]["main_beam_column"]["type"],
        "center_coord": {
            "x": params["cabin"]["length"]["axis_dis"],
            "y": params["cabin"]["height"]["axis_dis"]/2,
            "z": params["door"]["width"]["axis_dis"]
        },
        "dir": {
            "x": 0,
            "y": 1,
            "z": 0
        },
        "length": params["cabin"]["height"]["axis_dis"],
    }
    part_id = gen_id(column)
    info_params["frame_column"][part_id] = column
    # 然后是设备间的三根柱子
    # 首先是设备间两端
    for i in range(2):
        column = {
            "type": params["parts"]["main_beam_column"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"],
                "y": params["cabin"]["height"]["axis_dis"] / 2,
                "z": i*params["cabin"]["width"]["axis_dis"]
            },
            "dir": {
                "x": 0,
                "y": 1,
                "z": 0
            },
            "length": params["cabin"]["height"]["axis_dis"],
        }
        part_id = gen_id(column)
        info_params["frame_column"][part_id] = column
    # 其次是中间两根柱子
    for i in range(2):

        column = {
            "type": params["parts"]["main_beam_column"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"] - i*params["equip"]["width"]["axis_dis"],
                "y": params["cabin"]["height"]["axis_dis"] / 2,
                "z": params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]
            },
            "dir": {
                "x": 0,
                "y": 1,
                "z": 0
            },
            "length": params["cabin"]["height"]["axis_dis"],
        }
        part_id = gen_id(column)
        info_params["frame_column"][part_id] = column

    # 接下来是三个面上窗户两侧的框架柱，在计算之前首先要判断是否存在窗户
    # 首先是右侧
    if params["window"]["right"]["num"] == 1:
        for i in range(2):

            column = {
                "type": params["parts"]["main_beam_column"]["type"],
                "center_coord": {
                    "x": max(params["window"]["right"]["locate"])*params["window"]["width"]["axis_dis"] - i*params["window"]["width"]["axis_dis"],
                    "y": params["cabin"]["height"]["axis_dis"]/2,
                    "z": 0.0
                },
                "dir": {
                    "x": 0,
                    "y": 1,
                    "z": 0
                },
                "length": params["cabin"]["height"]["axis_dis"],
            }
            part_id = gen_id(column)
            info_params["frame_column"][part_id] = column
    elif params["window"]["right"]["num"] >= 2:
        # 此时需要获取框架柱的位置列表
        column_list = window.find_win_frame_column(params["window"]["right"]["locate"])
        for i in range(len(column_list)):
            column = {
                "type": params["parts"]["main_beam_column"]["type"],
                "center_coord": {
                    "x": (column_list[i]-1)*params["window"]["width"]["axis_dis"],
                    "y": params["cabin"]["height"]["axis_dis"] / 2,
                    "z": 0.0
                },
                "dir": {
                    "x": 0,
                    "y": 1,
                    "z": 0
                },
                "length": params["cabin"]["height"]["axis_dis"],
            }
            part_id = gen_id(column)
            info_params["frame_column"][part_id] = column

    # 其次是左侧
    if params["window"]["left"]["num"] == 1:
        for i in range(2):

            column = {
                "type": params["parts"]["main_beam_column"]["type"],
                "center_coord": {
                    "x": max(params["window"]["left"]["locate"])*params["window"]["width"]["axis_dis"] - i*params["window"]["width"]["axis_dis"],
                    "y": params["cabin"]["height"]["axis_dis"]/2,
                    "z": params["cabin"]["width"]["axis_dis"]
                },
                "dir": {
                    "x": 0,
                    "y": 1,
                    "z": 0
                },
                "length": params["cabin"]["height"]["axis_dis"],
            }
            part_id = gen_id(column)
            info_params["frame_column"][part_id] = column
    elif params["window"]["left"]["num"] >= 2:
        column_list = window.find_win_frame_column(params["window"]["left"]["locate"])
        for i in range(len(column_list)):
            column = {
                "type": params["parts"]["main_beam_column"]["type"],
                "center_coord": {
                    "x": (column_list[i] - 1) * params["window"]["width"]["axis_dis"],
                    "y": params["cabin"]["height"]["axis_dis"] / 2,
                    "z": params["cabin"]["width"]["axis_dis"]
                },
                "dir": {
                    "x": 0,
                    "y": 1,
                    "z": 0
                },
                "length": params["cabin"]["height"]["axis_dis"],
            }
            part_id = gen_id(column)
            info_params["frame_column"][part_id] = column

    # 最后是对侧
    if params["window"]["offside"]["num"] != 0:
        for i in range(params["window"]["offside"]["num"]+1): # 窗户两侧柱子的个数

            column = {
                "type": params["parts"]["main_beam_column"]["type"],
                "center_coord": {
                    "x": 0.0,
                    "y": params["cabin"]["height"]["axis_dis"] / 2,
                    "z": (params["cabin"]["width"]["axis_dis"]-params["window"]["width"]["axis_dis"]*params["window"]["offside"]["num"])/2 + i*params["window"]["width"]["axis_dis"]
                },
                "dir": {
                    "x": 0,
                    "y": 1,
                    "z": 0
                },
                "length": params["cabin"]["height"]["axis_dis"],
            }
            part_id = gen_id(column)
            info_params["frame_column"][part_id] = column

####################-----------------以下是所有框架梁的更新-------------------############################
    # 随后是所有的框架梁（长度方向）
    frame_beam_coord_list = []
    cen_x = params["cabin"]["length"]["axis_dis"] / 2
    for y in range(2):
        for z in range(2):
            frame_beam_coord_list.append(
                (cen_x, y * params["cabin"]["height"]["axis_dis"], z * params["cabin"]["width"]["axis_dis"]))

    for coord in frame_beam_coord_list:
        beam = {
            "type": params["parts"]["main_beam_column"]["type"],
            "center_coord": {
                "x": coord[0],
                "y": coord[1],
                "z": coord[2]
            },
            "dir": {
                "x": 1,
                "y": 0,
                "z": 0
            },
            "length": params["cabin"]["length"]["axis_dis"],
        }
        part_id = gen_id(beam)
        info_params["frame_beam_l"][part_id] = beam
    # 随后是设备间处的两根短横梁
    for i in range(2):

        beam = {
            "type": params["parts"]["main_beam_column"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]/2,
                "y": i*params["cabin"]["height"]["axis_dis"],
                "z": params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]
            },
            "dir": {
                "x": 1,
                "y": 0,
                "z": 0
            },
            "length": params["equip"]["width"]["axis_dis"],
        }
        part_id = gen_id(beam)
        info_params["frame_beam_short"][part_id] = beam

    # 随后是所有的框架梁（宽度方向）
    # 首先是最外侧的梁
    frame_beam_coord_list = []
    cen_z = params["cabin"]["width"]["axis_dis"] / 2
    for x in range(2):
        for y in range(2):
            frame_beam_coord_list.append(
                (x*params["cabin"]["length"]["axis_dis"], y*params["cabin"]["height"]["axis_dis"], cen_z))

    for coord in frame_beam_coord_list:

        beam = {
            "type": params["parts"]["main_beam_column"]["type"],
            "center_coord": {
                "x": coord[0],
                "y": coord[1],
                "z": coord[2]
            },
            "dir": {
                "x": 0,
                "y": 0,
                "z": 1
            },
            "length": params["cabin"]["width"]["axis_dis"],
        }
        part_id = gen_id(beam)
        info_params["frame_beam_w"][part_id] = beam

    # 其次是设备间上下的两根横梁
    for i in range(2):

        beam = {
            "type": params["parts"]["main_beam_column"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"],
                "y": i*params["cabin"]["height"]["axis_dis"],
                "z": params["cabin"]["width"]["axis_dis"]/2
            },
            "dir": {
                "x": 0,
                "y": 0,
                "z": 1
            },
            "length": params["cabin"]["width"]["axis_dis"],
        }
        part_id = gen_id(beam)
        info_params["frame_beam_w"][part_id] = beam
####################-----------------以上统计完了所有方钢管的位置-------------------############################
####################-----------------接下来统计环向主梁以及柱子的位置-------------------############################
    # 首先统计两个顶面
    for i in range(params["dis"]["side"]["num"]):

        beam = {
            "type": params["parts"]["cir_main_beam"]["type"],
            "center_coord": {
                "x": (i+1)*params["window"]["width"]["axis_dis"],
                "y": params["cabin"]["height"]["axis_dis"],
                "z": params["cabin"]["width"]["axis_dis"] / 2
            },
            "dir": {
                "x": 0,
                "y": 0,
                "z": 1
            },
            "length": params["cabin"]["width"]["axis_dis"],
        }
        part_id = gen_id(beam)
        info_params["cir_beam"][part_id] = beam

        beam = {
            "type": params["parts"]["cir_main_beam"]["type"],
            "center_coord": {
                "x": (i + 1) * params["window"]["width"]["axis_dis"],
                "y": 0.0,
                "z": params["cabin"]["width"]["axis_dis"] / 2
            },
            "dir": {
                "x": 0,
                "y": 0,
                "z": 1
            },
            "length": params["cabin"]["width"]["axis_dis"],
        }
        part_id = gen_id(beam)
        info_params["cir_beam"][part_id] = beam

    # 接下来是两个带窗户的面

    # 首先统计右侧
    # 统计之前先看这个面上有没有窗户，没有的话可以直接统计
    if params["window"]["right"]["num"] == 0:
        for i in range(params["dis"]["side"]["num"]):

            column = {
                "type": params["parts"]["cir_main_beam"]["type"],
                "center_coord": {
                    "x": (i + 1) * params["window"]["width"]["axis_dis"],
                    "y": params["cabin"]["height"]["axis_dis"]/2,
                    "z": 0.0
                },
                "dir": {
                    "x": 0,
                    "y": 1,
                    "z": 0
                },
                "length": params["cabin"]["height"]["axis_dis"],
            }
            part_id = gen_id(column)
            info_params["cir_column"][part_id] = column
    # 如果存在窗户的话则需要分开进行统计
    elif params["window"]["right"]["num"] == 1:
        # 此时分别记录窗户左右两边的环向主梁的个数
        # 首先记录窗户左侧，注意此时窗户不能位于最左端，要不然就没有环向主梁（柱）存在了
        if max(params["window"]["right"]["locate"]) != params["dis"]["side"]["num"]:
            for i in range(params["dis"]["side"]["num"]-max(params["window"]["right"]["locate"])):

                column = {
                    "type": params["parts"]["cir_main_beam"]["type"],
                    "center_coord": {
                        "x": params["dis"]["side"]["num"]*params["window"]["width"]["axis_dis"]-i*params["window"]["width"]["axis_dis"],
                        "y": params["cabin"]["height"]["axis_dis"] / 2,
                        "z": 0.0
                    },
                    "dir": {
                        "x": 0,
                        "y": 1,
                        "z": 0
                    },
                    "length": params["cabin"]["height"]["axis_dis"],
                }
                part_id = gen_id(column)
                info_params["cir_column"][part_id] = column
        # 接着记录窗户右侧
        if max(params["window"]["right"]["locate"]) != 2:
            for i in range(max(params["window"]["right"]["locate"])-2):

                column = {
                    "type": params["parts"]["cir_main_beam"]["type"],
                    "center_coord": {
                        "x": (i+1)*params["window"]["width"]["axis_dis"],
                        "y": params["cabin"]["height"]["axis_dis"] / 2,
                        "z": 0.0
                    },
                    "dir": {
                        "x": 0,
                        "y": 1,
                        "z": 0
                    },
                    "length": params["cabin"]["height"]["axis_dis"],
                }
                part_id = gen_id(column)
                info_params["cir_column"][part_id] = column
    elif params["window"]["right"]["num"] >= 2:
        main_column_list = window.find_win_main_column(params["window"]["right"]["locate"], params)
        for i in range(len(main_column_list)):
            column = {
                "type": params["parts"]["cir_main_beam"]["type"],
                "center_coord": {
                    "x": (main_column_list[i] - 1) * params["window"]["width"]["axis_dis"],
                    "y": params["cabin"]["height"]["axis_dis"] / 2,
                    "z": 0.0
                },
                "dir": {
                    "x": 0,
                    "y": 1,
                    "z": 0
                },
                "length": params["cabin"]["height"]["axis_dis"],
            }
            part_id = gen_id(column)
            info_params["cir_column"][part_id] = column

    # 随后统计左侧，方法同上
    if params["window"]["left"]["num"] == 0:
        for i in range(params["dis"]["side"]["num"]):

            beam = {
                "type": params["parts"]["cir_main_beam"]["type"],
                "center_coord": {
                    "x": (i + 1) * params["window"]["width"]["axis_dis"],
                    "y": params["cabin"]["height"]["axis_dis"]/2,
                    "z": params["cabin"]["width"]["axis_dis"]
                },
                "dir": {
                    "x": 0,
                    "y": 1,
                    "z": 0
                },
                "length": params["cabin"]["height"]["axis_dis"],
            }
            part_id = gen_id(beam)
            info_params["cir_column"][part_id] = beam
    # 如果存在窗户的话则需要分开进行统计
    elif params["window"]["left"]["num"] == 1:
        # 此时分别记录窗户左右两边的环向主梁的个数
        # 首先记录窗户左侧（也就是远离门的那一侧），注意此时窗户不能位于最左端
        if max(params["window"]["left"]["locate"]) != 2:
            for i in range(max(params["window"]["left"]["locate"])-2):

                column = {
                    "type": params["parts"]["cir_main_beam"]["type"],
                    "center_coord": {
                        "x": (i+1)*params["window"]["width"]["axis_dis"],
                        "y": params["cabin"]["height"]["axis_dis"] / 2,
                        "z": params["cabin"]["width"]["axis_dis"]
                    },
                    "dir": {
                        "x": 0,
                        "y": 1,
                        "z": 0
                    },
                    "length": params["cabin"]["height"]["axis_dis"],
                }
                part_id = gen_id(column)
                info_params["cir_column"][part_id] = column
        # 随后记录窗户右侧（也就是靠近门的那一侧），此时窗户不能位于最靠近门的那一边
        if max(params["window"]["left"]["locate"]) != params["dis"]["side"]["num"]:
            for i in range(params["dis"]["side"]["num"]-max(params["window"]["left"]["locate"])):

                column = {
                    "type": params["parts"]["cir_main_beam"]["type"],
                    "center_coord": {
                        "x": params["dis"]["side"]["num"]*params["window"]["width"]["axis_dis"]-i*params["window"]["width"]["axis_dis"],
                        "y": params["cabin"]["height"]["axis_dis"] / 2,
                        "z": params["cabin"]["width"]["axis_dis"]
                    },
                    "dir": {
                        "x": 0,
                        "y": 1,
                        "z": 0
                    },
                    "length": params["cabin"]["height"]["axis_dis"],
                }
                part_id = gen_id(column)
                info_params["cir_column"][part_id] = column
    elif params["window"]["left"]["num"] >= 2:

        main_column_list = window.find_win_main_column(params["window"]["left"]["locate"], params)
        for i in range(len(main_column_list)):
            column = {
                "type": params["parts"]["cir_main_beam"]["type"],
                "center_coord": {
                    "x": (main_column_list[i] - 1) * params["window"]["width"]["axis_dis"],
                    "y": params["cabin"]["height"]["axis_dis"] / 2,
                    "z": params["cabin"]["width"]["axis_dis"]
                },
                "dir": {
                    "x": 0,
                    "y": 1,
                    "z": 0
                },
                "length": params["cabin"]["height"]["axis_dis"],
            }
            part_id = gen_id(column)
            info_params["cir_column"][part_id] = column

    # 最后统计对侧，方法也差不多
    if params["window"]["offside"]["num"] == 0:
        for i in range(params["dis"]["offside"]["num"]["num"]):

            column = {
                "type": params["parts"]["cir_main_beam"]["type"],
                "center_coord": {
                    "x": 0.0,
                    "y": params["cabin"]["height"]["axis_dis"] / 2,
                    "z": params["dis"]["offside"]["axis_gap"]["axis_gap"] + i * params["window"]["width"]["axis_dis"]
                },
                "dir": {
                    "x": 0,
                    "y": 1,
                    "z": 0
                },
                "length": params["cabin"]["height"]["axis_dis"],
            }
            part_id = gen_id(column)
            info_params["cir_column"][part_id] = column

    # 有窗户的话要看这时候还有没有环向主梁
    elif params["dis"]["offside"]["num"]["num"] > (params["window"]["offside"]["num"]+1):
        # 此时存在环向主梁
        # 首先统计左侧，也就是面向这一面的左侧
        # 此时一侧的环向主梁的个数为如下：
        n = int((params["dis"]["offside"]["num"]["num"]-params["window"]["offside"]["num"]-1)/2)

        # 首先记录一侧
        for i in range(n):

            column = {
                "type": params["parts"]["cir_main_beam"]["type"],
                "center_coord": {
                    "x": 0.0,
                    "y": params["cabin"]["height"]["axis_dis"] / 2,
                    "z": params["dis"]["offside"]["axis_gap"]["axis_gap"] + i*params["window"]["width"]["axis_dis"]
                },
                "dir": {
                    "x": 0,
                    "y": 1,
                    "z": 0
                },
                "length": params["cabin"]["height"]["axis_dis"],
            }
            part_id = gen_id(column)
            info_params["cir_column"][part_id] = column

        # 其次记录另一侧
        for i in range(n):

            column = {
                "type": params["parts"]["cir_main_beam"]["type"],
                "center_coord": {
                    "x": 0.0,
                    "y": params["cabin"]["height"]["axis_dis"] / 2,
                    "z": params["cabin"]["width"]["axis_dis"]-params["dis"]["offside"]["axis_gap"]["axis_gap"] - i * params["window"]["width"]["axis_dis"]
                },
                "dir": {
                    "x": 0,
                    "y": 1,
                    "z": 0
                },
                "length": params["cabin"]["height"]["axis_dis"],
            }
            part_id = gen_id(column)
            info_params["cir_column"][part_id] = column

    # 接下来统计设备间长度方向中间固定的那一根柱子

    column = {
        "type": params["parts"]["cir_main_beam"]["type"],
        "center_coord": {
            "x": params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"],
            "y": params["cabin"]["height"]["axis_dis"] / 2,
            "z": params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]/2
        },
        "dir": {
            "x": 0,
            "y": 1,
            "z": 0
        },
        "length": params["cabin"]["height"]["axis_dis"],
    }
    part_id = gen_id(column)
    info_params["cir_column"][part_id] = column
####################-----------------以上统计完了所有环向主梁的位置-------------------############################
####################-----------------接下来统计所有环向次梁的位置-------------------############################
    # 首先是门上下的环向次梁
    for i in range(2):

        beam = {
            "type": params["parts"]["cir_secd_beam"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"],
                "y": params["door"]["ground_clear"]["axis_dis"]+i*params["door"]["height"]["axis_dis"],
                "z": params["door"]["width"]["axis_dis"]/2
            },
            "dir": {
                "x": 0,
                "y": 0,
                "z": 1
            },
            "length": params["door"]["width"]["axis_dis"],
        }
        part_id = gen_id(beam)
        info_params["door_beam"][part_id] = beam

    # 随后是舱体长度方向的四根环向次梁
    cen_x = params["cabin"]["length"]["axis_dis"]/2
    coord_list = []
    for y in range(2):
        for z in range(2):
            coord_list.append((cen_x, params["window"]["ground_clear"]["axis_dis"]+y*params["window"]["height"]["axis_dis"], z*params["cabin"]["width"]["axis_dis"]))
    for coord in coord_list:

        beam = {
            "type": params["parts"]["cir_secd_beam"]["type"],
            "center_coord": {
                "x": coord[0],
                "y": coord[1],
                "z": coord[2]
            },
            "dir": {
                "x": 1,
                "y": 0,
                "z": 0
            },
            "length": params["cabin"]["length"]["axis_dis"],
        }
        part_id = gen_id(beam)
        info_params["window_beam_side"][part_id] = beam

    # 随后是舱体对侧的两根环向次梁
    for i in range(2):

        beam = {
            "type": params["parts"]["cir_secd_beam"]["type"],
            "center_coord": {
                "x": 0.0,
                "y": params["window"]["ground_clear"]["axis_dis"]+i*params["window"]["height"]["axis_dis"],
                "z": params["cabin"]["width"]["axis_dis"]/2
            },
            "dir": {
                "x": 0,
                "y": 0,
                "z": 1
            },
            "length": params["cabin"]["width"]["axis_dis"],
        }
        part_id = gen_id(beam)
        info_params["window_beam_offside"][part_id] = beam

    # 随后是门左侧的环向次梁
    for i in range(2):

        beam = {
            "type": params["parts"]["cir_secd_beam"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"],
                "y": params["window"]["ground_clear"]["axis_dis"] + i * params["window"]["height"]["axis_dis"],
                "z": (params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]-params["door"]["width"]["axis_dis"])/2+params["door"]["width"]["axis_dis"]
            },
            "dir": {
                "x": 0,
                "y": 0,
                "z": 1
            },
            "length": params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]-params["door"]["width"]["axis_dis"],
        }
        part_id = gen_id(beam)
        info_params["door_left_beam"][part_id] = beam

    # 随后是设备间长度方向
    for i in range(2):

        beam = {
            "type": params["parts"]["cir_secd_beam"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"],
                "y": params["window"]["ground_clear"]["axis_dis"] + i * params["window"]["height"]["axis_dis"],
                "z": params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]/2
            },
            "dir": {
                "x": 0,
                "y": 0,
                "z": 1
            },
            "length": params["equip"]["length"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["equip_beam_l"][part_id] = beam

    # 随后是设备间宽度方向
    for i in range(2):

        beam = {
            "type": params["parts"]["cir_secd_beam"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]/2,
                "y": params["window"]["ground_clear"]["axis_dis"] + i * params["window"]["height"]["axis_dis"],
                "z": params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]
            },
            "dir": {
                "x": 1,
                "y": 0,
                "z": 0
            },
            "length": params["equip"]["width"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["equip_beam_w"][part_id] = beam

    # 接下来统计上下两个顶面上的环向次梁，这一部分不包括门上面那一块延长出来的
    cen_x = (params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"])/2
    coord_list = []
    for z in range(params["dis"]["offside"]["num"]["num"]):
        for y in range(2):
            coord_list.append((cen_x, y*params["cabin"]["height"]["axis_dis"], params["dis"]["offside"]["axis_gap"]["axis_gap"]+z*params["window"]["width"]["axis_dis"]))
    for coord in coord_list:

        beam = {
            "type": params["parts"]["cir_secd_beam"]["type"],
            "center_coord": {
                "x": coord[0],
                "y": coord[1],
                "z": coord[2]
            },
            "dir": {
                "x": 1,
                "y": 0,
                "z": 0
            },
            "length": params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["cir_secd_beam"][part_id] = beam

    # 统计设备间上部中间那一根次梁

    beam = {
        "type": params["parts"]["cir_secd_beam"]["type"],
        "center_coord": {
            "x": params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]/2,
            "y": params["cabin"]["height"]["axis_dis"],
            "z": params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]/2
        },
        "dir": {
            "x": 1,
            "y": 0,
            "z": 0
        },
        "length": params["equip"]["width"]["axis_dis"]
    }
    part_id = gen_id(beam)
    info_params["equip_beam_w_top"][part_id] = beam

    # 最后来统计门上面那一块环向次梁的布置，首先还是要计算有几根会被延伸出去
    num = params["dis"]["offside"]["num"]["num"]
    if num == 3:
        # 此时只会外延一根，但要注意底面也有
        for i in range(2):

            beam = {
                "type": params["parts"]["cir_secd_beam"]["type"],
                "center_coord": {
                    "x": params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]/2,
                    "y": i*params["cabin"]["height"]["axis_dis"],
                    "z": params["dis"]["offside"]["axis_gap"]["axis_gap"]
                },
                "dir": {
                    "x": 1,
                    "y": 0,
                    "z": 0
                },
                "length": params["equip"]["width"]["axis_dis"]
            }
            part_id = gen_id(beam)
            info_params["equip_beam_w_top"][part_id] = beam
    elif num == 5 or num == 7:
        # 此时一定会有两根外延出去
        for y in range(2):
            for i in range(2):

                beam = {
                    "type": params["parts"]["cir_secd_beam"]["type"],
                    "center_coord": {
                        "x": params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"] / 2,
                        "y": y*params["cabin"]["height"]["axis_dis"],
                        "z": params["dis"]["offside"]["axis_gap"]["axis_gap"] + i*params["window"]["width"]["axis_dis"]
                    },
                    "dir": {
                        "x": 1,
                        "y": 0,
                        "z": 0
                    },
                    "length": params["equip"]["width"]["axis_dis"]
                }
                part_id = gen_id(beam)
                info_params["equip_beam_w_top"][part_id] = beam
    else:
        # 此时需要额外计算会有几根外延
        n = int(num / 2)
        # 计算距离差值
        d = params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"] - \
            params["dis"]["offside"]["axis_gap"]["axis_gap"] - (num - 2) / 2 * params["window"]["width"]["axis_dis"]
        if d <= 200.0:
            # 此时不可以外延
            n -= 1
        for y in range(2):
            for i in range(n):

                beam = {
                    "type": params["parts"]["cir_secd_beam"]["type"],
                    "center_coord": {
                        "x": params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"] / 2,
                        "y": y * params["cabin"]["height"]["axis_dis"],
                        "z": params["dis"]["offside"]["axis_gap"]["axis_gap"] + i * params["window"]["width"]["axis_dis"]
                    },
                    "dir": {
                        "x": 1,
                        "y": 0,
                        "z": 0
                    },
                    "length": params["equip"]["width"]["axis_dis"]
                }
                part_id = gen_id(beam)
                info_params["equip_beam_w_top"][part_id] = beam
####################-----------------接下来统计所有环向支撑梁的位置-------------------############################
    # 首先是门上的环向支撑梁
    beam = {
        "type": params["parts"]["cir_sup_beam"]["type"],
        "center_coord": {
            "x": params["cabin"]["length"]["axis_dis"],
            "y": params["cabin"]["height"]["axis_dis"]-params["door"]["top_clear"]["axis_dis"]/2,
            "z": params["door"]["width"]["axis_dis"]/2
        },
        "dir": {
            "x": 0,
            "y": 0,
            "z": 1
        },
        "length": params["door"]["width"]["axis_dis"]
    }
    part_id = gen_id(beam)
    info_params["sup_beam_d"][part_id] = beam
    # 接下来统计上部支撑梁个数
    if params["sup"]["up"]["num"] == 1:
        # 首先统计右侧这个面
        beam = {
            "type": params["parts"]["cir_sup_beam"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"]/2,
                "y": params["cabin"]["height"]["axis_dis"] - params["window"]["top_clear"]["axis_dis"]/2,
                "z": 0.0
            },
            "dir": {
                "x": 1,
                "y": 0,
                "z": 0
            },
            "length": params["cabin"]["length"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["sup_beam_right"][part_id] = beam

        # 其次统计背面
        beam = {
            "type": params["parts"]["cir_sup_beam"]["type"],
            "center_coord": {
                "x": 0.0,
                "y": params["cabin"]["height"]["axis_dis"] - params["window"]["top_clear"]["axis_dis"] / 2,
                "z": params["cabin"]["width"]["axis_dis"]/2
            },
            "dir": {
                "x": 0,
                "y": 0,
                "z": 1
            },
            "length": params["cabin"]["width"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["sup_beam_offside"][part_id] = beam

        # 其次统计左面
        beam = {
            "type": params["parts"]["cir_sup_beam"]["type"],
            "center_coord": {
                "x": (params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"])/2,
                "y": params["cabin"]["height"]["axis_dis"] - params["window"]["top_clear"]["axis_dis"] / 2,
                "z": params["cabin"]["width"]["axis_dis"]
            },
            "dir": {
                "x": 1,
                "y": 0,
                "z": 0
            },
            "length": params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["sup_beam_left"][part_id] = beam

        # 随后是设备间长度方向
        beam = {
            "type": params["parts"]["cir_sup_beam"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"],
                "y": params["cabin"]["height"]["axis_dis"] - params["window"]["top_clear"]["axis_dis"] / 2,
                "z": params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]/2
            },
            "dir": {
                "x": 0,
                "y": 0,
                "z": 1
            },
            "length": params["equip"]["length"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["sup_beam_el"][part_id] = beam

        # 随后是设备间宽度方向
        beam = {
            "type": params["parts"]["cir_sup_beam"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]/2,
                "y": params["cabin"]["height"]["axis_dis"] - params["window"]["top_clear"]["axis_dis"] / 2,
                "z": params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]
            },
            "dir": {
                "x": 1,
                "y": 0,
                "z": 0
            },
            "length": params["equip"]["width"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["sup_beam_ew"][part_id] = beam

        # 随后是门左侧
        beam = {
            "type": params["parts"]["cir_sup_beam"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"],
                "y": params["cabin"]["height"]["axis_dis"] - params["window"]["top_clear"]["axis_dis"] / 2,
                "z": (params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"] - params["door"]["width"]["axis_dis"])/2 + params["door"]["width"]["axis_dis"]
            },
            "dir": {
                "x": 0,
                "y": 0,
                "z": 1
            },
            "length": params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"] - params["door"]["width"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["sup_beam_dl"][part_id] = beam

    # 接下来统计下部支撑梁个数
    if params["sup"]["btm"]["num"] == 1:
        # 首先统计右侧这个面
        beam = {
            "type": params["parts"]["cir_sup_beam"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"]/2,
                "y": params["window"]["ground_clear"]["axis_dis"]/2,
                "z": 0.0
            },
            "dir": {
                "x": 1,
                "y": 0,
                "z": 0
            },
            "length": params["cabin"]["length"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["sup_beam_right"][part_id] = beam

        # 其次统计背面
        beam = {
            "type": params["parts"]["cir_sup_beam"]["type"],
            "center_coord": {
                "x": 0.0,
                "y": params["window"]["ground_clear"]["axis_dis"]/2,
                "z": params["cabin"]["width"]["axis_dis"]/2
            },
            "dir": {
                "x": 0,
                "y": 0,
                "z": 1
            },
            "length": params["cabin"]["width"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["sup_beam_offside"][part_id] = beam

        # 其次统计左面
        beam = {
            "type": params["parts"]["cir_sup_beam"]["type"],
            "center_coord": {
                "x": (params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"])/2,
                "y": params["window"]["ground_clear"]["axis_dis"]/2,
                "z": params["cabin"]["width"]["axis_dis"]
            },
            "dir": {
                "x": 1,
                "y": 0,
                "z": 0
            },
            "length": params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["sup_beam_left"][part_id] = beam

        # 随后是设备间长度方向
        beam = {
            "type": params["parts"]["cir_sup_beam"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"],
                "y": params["window"]["ground_clear"]["axis_dis"]/2,
                "z": params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]/2
            },
            "dir": {
                "x": 0,
                "y": 0,
                "z": 1
            },
            "length": params["equip"]["length"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["sup_beam_el"][part_id] = beam

        # 随后是设备间宽度方向
        beam = {
            "type": params["parts"]["cir_sup_beam"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]/2,
                "y": params["window"]["ground_clear"]["axis_dis"]/2,
                "z": params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]
            },
            "dir": {
                "x": 1,
                "y": 0,
                "z": 0
            },
            "length": params["equip"]["width"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["sup_beam_ew"][part_id] = beam

        # 随后是门左侧
        beam = {
            "type": params["parts"]["cir_sup_beam"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"],
                "y": params["window"]["ground_clear"]["axis_dis"]/2,
                "z": (params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"] - params["door"]["width"]["axis_dis"])/2 + params["door"]["width"]["axis_dis"]
            },
            "dir": {
                "x": 0,
                "y": 0,
                "z": 1
            },
            "length": params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"] - params["door"]["width"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["sup_beam_dl"][part_id] = beam

    # 接下来统计上下两个顶面
    # 首先统计边上
    if params["sup"]["top_side"]["num"] == 1:
        for z in range(2):
            for y in range(2):
                beam = {
                    "type": params["parts"]["cir_sup_beam"]["type"],
                    "center_coord": {
                        "x": (params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"])/ 2,
                        "y": y * params["cabin"]["height"]["axis_dis"],
                        "z": params["dis"]["offside"]["axis_gap"]["axis_gap"]/2 + z * (params["cabin"]["width"]["axis_dis"]-params["dis"]["offside"]["axis_gap"]["axis_gap"])
                    },
                    "dir": {
                        "x": 1,
                        "y": 0,
                        "z": 0
                    },
                    "length": params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]
                }
                part_id = gen_id(beam)
                info_params["sup_beam_top"][part_id] = beam

    # 接下来统计中间
    if params["sup"]["top_mid"]["num"] == 1:
        for y in range(2):
            for i in range(params["dis"]["offside"]["num"]["num"]-1):
                beam = {
                    "type": params["parts"]["cir_sup_beam"]["type"],
                    "center_coord": {
                        "x": (params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]) / 2,
                        "y": y * params["cabin"]["height"]["axis_dis"],
                        "z": params["dis"]["offside"]["axis_gap"]["axis_gap"] + params["window"]["width"]["axis_dis"]/2 + i * params["window"]["width"]["axis_dis"]
                    },
                    "dir": {
                        "x": 1,
                        "y": 0,
                        "z": 0
                    },
                    "length": params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]
                }
                part_id = gen_id(beam)
                info_params["sup_beam_top"][part_id] = beam

    # 最后统计侧面中间的地方，首先统计两个没有窗户的地方，也就是设备间长宽方向以及门左侧的
    # 首先统计设备间长度方向
    for i in range (params["sup"]["mid"]["num"]):
        beam = {
            "type": params["parts"]["cir_sup_beam"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"],
                "y": params["window"]["ground_clear"]["axis_dis"] + (i+1)*params["sup"]["mid"]["gap"],
                "z": params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]/2
            },
            "dir": {
                "x": 0,
                "y": 0,
                "z": 1
            },
            "length": params["equip"]["length"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["sup_beam_el"][part_id] = beam

        # 首先统计设备间宽度方向
        beam = {
            "type": params["parts"]["cir_sup_beam"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]/2,
                "y": params["window"]["ground_clear"]["axis_dis"] + (i + 1) * params["sup"]["mid"]["gap"],
                "z": params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]
            },
            "dir": {
                "x": 1,
                "y": 0,
                "z": 0
            },
            "length": params["equip"]["width"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["sup_beam_ew"][part_id] = beam

        # 再统计门左侧的
        beam = {
            "type": params["parts"]["cir_sup_beam"]["type"],
            "center_coord": {
                "x": params["cabin"]["length"]["axis_dis"],
                "y": params["window"]["ground_clear"]["axis_dis"] + (i + 1) * params["sup"]["mid"]["gap"],
                "z": (params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]-params["door"]["width"]["axis_dis"])/2+params["door"]["width"]["axis_dis"]
            },
            "dir": {
                "x": 0,
                "y": 0,
                "z": 1
            },
            "length": params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]-params["door"]["width"]["axis_dis"]
        }
        part_id = gen_id(beam)
        info_params["sup_beam_dl"][part_id] = beam

    # 接下来统计舱体右侧，这种情况要区分有没有窗户
    if params["window"]["right"]["num"] == 0:
        for i in range(params["sup"]["mid"]["num"]):
            beam = {
                "type": params["parts"]["cir_sup_beam"]["type"],
                "center_coord": {
                    "x": params["cabin"]["length"]["axis_dis"]/2,
                    "y": params["window"]["ground_clear"]["axis_dis"] + (i + 1) * params["sup"]["mid"]["gap"],
                    "z": 0.0
                },
                "dir": {
                    "x": 1,
                    "y": 0,
                    "z": 0
                },
                "length": params["cabin"]["length"]["axis_dis"]
            }
            part_id = gen_id(beam)
            info_params["sup_beam_dl"][part_id] = beam
    elif params["window"]["right"]["num"] == 1:
        # 此时存在窗户，需要分别按照窗户两端进行统计，首先统计右边
        for i in range(params["sup"]["mid"]["num"]):
            beam = {
                "type": params["parts"]["cir_sup_beam"]["type"],
                "center_coord": {
                    "x": (max(params["window"]["right"]["locate"])-1)*params["window"]["width"]["axis_dis"]/2,
                    "y": params["window"]["ground_clear"]["axis_dis"] + (i + 1) * params["sup"]["mid"]["gap"],
                    "z": 0.0
                },
                "dir": {
                    "x": 1,
                    "y": 0,
                    "z": 0
                },
                "length": (max(params["window"]["right"]["locate"])-1)*params["window"]["width"]["axis_dis"]
            }
            part_id = gen_id(beam)
            info_params["sup_beam_right_wr"][part_id] = beam

            # 再统计窗户左侧
            beam = {
                "type": params["parts"]["cir_sup_beam"]["type"],
                "center_coord": {
                    "x": (params["cabin"]["length"]["axis_dis"]-params["window"]["width"]["axis_dis"]*max(params["window"]["right"]["locate"]))/2+params["window"]["width"]["axis_dis"]*max(params["window"]["right"]["locate"]),
                    "y": params["window"]["ground_clear"]["axis_dis"] + (i + 1) * params["sup"]["mid"]["gap"],
                    "z": 0.0
                },
                "dir": {
                    "x": 1,
                    "y": 0,
                    "z": 0
                },
                "length": params["cabin"]["length"]["axis_dis"]-params["window"]["width"]["axis_dis"]*max(params["window"]["right"]["locate"])
            }
            part_id = gen_id(beam)
            info_params["sup_beam_right_wl"][part_id] = beam
    elif params["window"]["right"]["num"] >= 2:
        # 此时还是要讨论空隙数量，没有空隙最好
        gap_list =  window.find_gap_locate(params["window"]["right"]["locate"])
        # 无论窗户之间有没有缝隙，左右两侧的都是要统计的
        # 首先是窗户右侧
        for i in range(params["sup"]["mid"]["num"]):
            beam = {
                "type": params["parts"]["cir_sup_beam"]["type"],
                "center_coord": {
                    "x": (min(params["window"]["right"]["locate"]) - 1) * params["window"]["width"]["axis_dis"] / 2,
                    "y": params["window"]["ground_clear"]["axis_dis"] + (i + 1) * params["sup"]["mid"]["gap"],
                    "z": 0.0
                },
                "dir": {
                    "x": 1,
                    "y": 0,
                    "z": 0
                },
                "length": (min(params["window"]["right"]["locate"]) - 1) * params["window"]["width"]["axis_dis"]
            }
            part_id = gen_id(beam)
            info_params["sup_beam_right_wr"][part_id] = beam

            # 再统计窗户左侧
            beam = {
                "type": params["parts"]["cir_sup_beam"]["type"],
                "center_coord": {
                    "x": (params["cabin"]["length"]["axis_dis"] - params["window"]["width"]["axis_dis"] * max(
                        params["window"]["right"]["locate"])) / 2 + params["window"]["width"]["axis_dis"] * max(
                        params["window"]["right"]["locate"]),
                    "y": params["window"]["ground_clear"]["axis_dis"] + (i + 1) * params["sup"]["mid"]["gap"],
                    "z": 0.0
                },
                "dir": {
                    "x": 1,
                    "y": 0,
                    "z": 0
                },
                "length": params["cabin"]["length"]["axis_dis"] - params["window"]["width"]["axis_dis"] * max(
                    params["window"]["right"]["locate"])
            }
            part_id = gen_id(beam)
            info_params["sup_beam_right_wl"][part_id] = beam
        if len(gap_list) == 0:
            pass
        else:
            # 此时窗户之间存在间隙
            for i in range(len(gap_list)):
                for k in range(params["sup"]["mid"]["num"]):
                    beam = {
                        "type": params["parts"]["cir_sup_beam"]["type"],
                        "center_coord": {
                            "x": (gap_list[i]-1) * params["window"]["width"]["axis_dis"] + params["window"]["width"]["axis_dis"] / 2,
                            "y": params["window"]["ground_clear"]["axis_dis"] + (k + 1) * params["sup"]["mid"]["gap"],
                            "z": 0.0
                        },
                        "dir": {
                            "x": 1,
                            "y": 0,
                            "z": 0
                        },
                        "length": params["window"]["width"]["axis_dis"]
                    }
                    part_id = gen_id(beam)
                    info_params["sup_beam_right_wm"][part_id] = beam

    # 接下来统计舱体左侧，这种情况跟上面的情况差不多
    if params["window"]["left"]["num"] == 0:
        for i in range(params["sup"]["mid"]["num"]):
            beam = {
                "type": params["parts"]["cir_sup_beam"]["type"],
                "center_coord": {
                    "x": (params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"])/2,
                    "y": params["window"]["ground_clear"]["axis_dis"] + (i + 1) * params["sup"]["mid"]["gap"],
                    "z": params["cabin"]["width"]["axis_dis"]
                },
                "dir": {
                    "x": 1,
                    "y": 0,
                    "z": 0
                },
                "length": params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]
            }
            part_id = gen_id(beam)
            info_params["sup_beam_left"][part_id] = beam
    elif params["window"]["left"]["num"] == 1:
        # 此时存在窗户，需要分别按照窗户两端进行统计，首先统计左边
        for i in range(params["sup"]["mid"]["num"]):
            beam = {
                "type": params["parts"]["cir_sup_beam"]["type"],
                "center_coord": {
                    "x": (max(params["window"]["left"]["locate"])-1)*params["window"]["width"]["axis_dis"]/2,
                    "y": params["window"]["ground_clear"]["axis_dis"] + (i + 1) * params["sup"]["mid"]["gap"],
                    "z": params["cabin"]["width"]["axis_dis"]
                },
                "dir": {
                    "x": 1,
                    "y": 0,
                    "z": 0
                },
                "length": (max(params["window"]["left"]["locate"])-1)*params["window"]["width"]["axis_dis"]
            }
            part_id = gen_id(beam)
            info_params["sup_beam_left_wl"][part_id] = beam

            # 再统计窗户右侧
            beam = {
                "type": params["parts"]["cir_sup_beam"]["type"],
                "center_coord": {
                    "x": (params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]-params["window"]["width"]["axis_dis"]*max(params["window"]["left"]["locate"]))/2+params["window"]["width"]["axis_dis"]*max(params["window"]["left"]["locate"]),
                    "y": params["window"]["ground_clear"]["axis_dis"] + (i + 1) * params["sup"]["mid"]["gap"],
                    "z": params["cabin"]["width"]["axis_dis"]
                },
                "dir": {
                    "x": 1,
                    "y": 0,
                    "z": 0
                },
                "length": params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]-params["window"]["width"]["axis_dis"]*max(params["window"]["left"]["locate"])
            }
            part_id = gen_id(beam)
            info_params["sup_beam_left_wr"][part_id] = beam
    elif params["window"]["left"]["num"] >= 2:
        # 此时还是要讨论空隙数量，没有空隙最好
        gap_list = window.find_gap_locate(params["window"]["left"]["locate"])
        # 无论窗户之间有没有缝隙，左右两侧的都是要统计的
        for i in range(params["sup"]["mid"]["num"]):
            # 首先统计窗户左侧
            beam = {
                "type": params["parts"]["cir_sup_beam"]["type"],
                "center_coord": {
                    "x": (min(params["window"]["left"]["locate"])-1)*params["window"]["width"]["axis_dis"]/2,
                    "y": params["window"]["ground_clear"]["axis_dis"] + (i + 1) * params["sup"]["mid"]["gap"],
                    "z": params["cabin"]["width"]["axis_dis"]
                },
                "dir": {
                    "x": 1,
                    "y": 0,
                    "z": 0
                },
                "length": (min(params["window"]["left"]["locate"])-1)*params["window"]["width"]["axis_dis"]
            }
            part_id = gen_id(beam)
            info_params["sup_beam_left_wl"][part_id] = beam

            # 再统计窗户右侧
            beam = {
                "type": params["parts"]["cir_sup_beam"]["type"],
                "center_coord": {
                    "x": (params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]-params["window"]["width"]["axis_dis"]*max(params["window"]["left"]["locate"]))/2+params["window"]["width"]["axis_dis"]*max(params["window"]["left"]["locate"]),
                    "y": params["window"]["ground_clear"]["axis_dis"] + (i + 1) * params["sup"]["mid"]["gap"],
                    "z": params["cabin"]["width"]["axis_dis"]
                },
                "dir": {
                    "x": 1,
                    "y": 0,
                    "z": 0
                },
                "length": params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]-params["window"]["width"]["axis_dis"]*max(params["window"]["left"]["locate"])
            }
            part_id = gen_id(beam)
            info_params["sup_beam_left_wr"][part_id] = beam
        if len(gap_list) == 0:
            pass
        else:
            # 此时窗户之间存在间隙
            for i in range(len(gap_list)):
                for k in range(params["sup"]["mid"]["num"]):
                    beam = {
                        "type": params["parts"]["cir_sup_beam"]["type"],
                        "center_coord": {
                            "x": (gap_list[i]-1) * params["window"]["width"]["axis_dis"] + params["window"]["width"]["axis_dis"] / 2,
                            "y": params["window"]["ground_clear"]["axis_dis"] + (k + 1) * params["sup"]["mid"]["gap"],
                            "z": params["cabin"]["width"]["axis_dis"]
                        },
                        "dir": {
                            "x": 1,
                            "y": 0,
                            "z": 0
                        },
                        "length": params["window"]["width"]["axis_dis"]
                    }
                    part_id = gen_id(beam)
                    info_params["sup_beam_left_wm"][part_id] = beam

    # 接下来统计舱体对侧，还是要区分有没有窗户
    if params["window"]["offside"]["num"] == 0:
        for i in range(params["sup"]["mid"]["num"]):
            beam = {
                "type": params["parts"]["cir_sup_beam"]["type"],
                "center_coord": {
                    "x": 0.0,
                    "y": params["window"]["ground_clear"]["axis_dis"] + (i + 1) * params["sup"]["mid"]["gap"],
                    "z": params["cabin"]["width"]["axis_dis"]/2
                },
                "dir": {
                    "x": 0,
                    "y": 0,
                    "z": 1
                },
                "length": params["cabin"]["width"]["axis_dis"]
            }
            part_id = gen_id(beam)
            info_params["sup_beam_offside"][part_id] = beam
    else:
        # 此时对侧存在窗户
        for i in range(2):
            for y in range(params["sup"]["mid"]["num"]):
                beam = {
                    "type": params["parts"]["cir_sup_beam"]["type"],
                    "center_coord": {
                        "x": 0.0,
                        "y": params["window"]["ground_clear"]["axis_dis"] + (y + 1) * params["sup"]["mid"]["gap"],
                        "z": (params["cabin"]["width"]["axis_dis"]-params["window"]["offside"]["num"]*params["window"]["width"]["axis_dis"])/4 + i*(params["cabin"]["width"]["axis_dis"]-(params["cabin"]["width"]["axis_dis"]-params["window"]["offside"]["num"]*params["window"]["width"]["axis_dis"])/2)
                    },
                    "dir": {
                        "x": 0,
                        "y": 0,
                        "z": 1
                    },
                    "length": (params["cabin"]["width"]["axis_dis"]-params["window"]["offside"]["num"]*params["window"]["width"]["axis_dis"])/2
                }
                part_id = gen_id(beam)
                info_params["sup_beam_offside_w"][part_id] = beam

    # 最后统计门上方外延出来的所有环向支撑梁的位置信息
    # 首先需要记录最外侧的
    if params["sup"]["top_side"]["num"] == 1:
        for y in range(2):
            beam = {
                    "type": params["parts"]["cir_sup_beam"]["type"],
                    "center_coord": {
                        "x": params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]/2,
                        "y": y * params["cabin"]["height"]["axis_dis"],
                        "z": params["dis"]["offside"]["axis_gap"]["axis_gap"]/2
                    },
                    "dir": {
                        "x": 1,
                        "y": 0,
                        "z": 0
                    },
                    "length": params["equip"]["width"]["axis_dis"]
                }
            part_id = gen_id(beam)
            info_params["sup_beam_ew_top"][part_id] = beam

    # 随后需要记录内侧的
    if params["sup"]["top_mid"]["num"] == 1:
        num = params["dis"]["offside"]["num"]["num"]
        # n为会外延出去的的环向次梁的数量
        if num == 3:
            # 此时只会外延一根
            n = 1
        elif num == 5 or num == 7:
            # 此时一定会有两根外延出去
            n = int(math.floor(num / 2))
        else:
            # 此时需要计算到底会有几个会延伸出去
            n = int(num / 2)
            # 计算距离差值
            d = params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"] - \
                params["dis"]["offside"]["axis_gap"]["axis_gap"] - (num - 2) / 2 * params["window"]["width"]["axis_dis"]
            if d <= 200.0:
                # 此时不可以外延
                n = int(n - 1)

        n -= 1  # 此时记录的是一定会有的环向支撑梁的数量
        n += 1  # 此时把外一个给加上
        dis = params["dis"]["offside"]["axis_gap"]["axis_gap"] + params["sup"]["top_mid"]["gap"] + (n - 1) * \
              params["window"]["width"]["axis_dis"]
        if params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"] - dis <= 200:
            # 此时说明不能加了，已经超限了
            n -= 1

        # 随后开始记录
        for i in range(n):
            for y in range(2):
                beam = {
                    "type": params["parts"]["cir_sup_beam"]["type"],
                    "center_coord": {
                        "x": params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]/2,
                        "y": y * params["cabin"]["height"]["axis_dis"],
                        "z": params["dis"]["offside"]["axis_gap"]["axis_gap"]+params["sup"]["top_mid"]["gap"]+i * params["window"]["width"]["axis_dis"]
                    },
                    "dir": {
                        "x": 1,
                        "y": 0,
                        "z": 0
                    },
                    "length": params["equip"]["width"]["axis_dis"]
                }
                part_id = gen_id(beam)
                info_params["sup_beam_ew_top"][part_id] = beam

    return info_params

# 为每一根构件新增偏置信息
def update_offset(params: dict, parts_info: dict):
    for part_id, part_info in parts_info.items():
        # 接下来统计每一个面,首先统计右侧
        if part_info["center_coord"]["z"] == 0:
            if part_info["type"].startswith("SHS") or part_info["type"][3:6] == "150":
                parts_info[part_id]["offset"] = {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                }
            else:
                if part_info["type"].startswith("C"):
                    parts_info[part_id]["offset"] = {
                    "x": 0.0,
                    "y": 0.0,
                    "z": -params["parts"]["cir_sup_beam"]["move"]
                    }
                else:
                    parts_info[part_id]["offset"] = {
                        "x": 0.0,
                        "y": 0.0,
                        "z": -params["parts"]["cir_secd_beam"]["move"]
                    }
        # 然后统计对侧
        elif part_info["center_coord"]["x"] == 0:
            if part_info["type"].startswith("SHS") or part_info["type"][3:6] == "150":
                parts_info[part_id]["offset"] = {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                }
            else:
                if part_info["type"].startswith("C"):
                    parts_info[part_id]["offset"] = {
                    "x": -params["parts"]["cir_sup_beam"]["move"],
                    "y": 0.0,
                    "z": 0.0
                    }
                else:
                    parts_info[part_id]["offset"] = {
                        "x": -params["parts"]["cir_secd_beam"]["move"],
                        "y": 0.0,
                        "z": 0.0
                    }
        # 然后统计底部
        elif part_info["center_coord"]["y"] == 0:
            if part_info["type"].startswith("SHS") or part_info["type"][3:6] == "150":
                parts_info[part_id]["offset"] = {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                }
            else:
                if part_info["type"].startswith("C"):
                    parts_info[part_id]["offset"] = {
                    "x": 0.0,
                    "y": -params["parts"]["cir_sup_beam"]["move"],
                    "z": 0.0
                    }
                else:
                    parts_info[part_id]["offset"] = {
                        "x": 0.0,
                        "y": -params["parts"]["cir_secd_beam"]["move"],
                        "z": 0.0
                    }
        # 然后统计顶部
        elif part_info["center_coord"]["y"] == params["cabin"]["height"]["axis_dis"]:
            if part_info["type"].startswith("SHS") or part_info["type"][3:6] == "150":
                parts_info[part_id]["offset"] = {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                }
            else:
                if part_info["type"].startswith("C"):
                    parts_info[part_id]["offset"] = {
                    "x": 0.0,
                    "y": params["parts"]["cir_sup_beam"]["move"],
                    "z": 0.0
                    }
                else:
                    parts_info[part_id]["offset"] = {
                        "x": 0.0,
                        "y": params["parts"]["cir_secd_beam"]["move"],
                        "z": 0.0
                    }
        # 然后统计左侧，包括舱体宽度方向
        elif part_info["center_coord"]["z"] == params["cabin"]["width"]["axis_dis"] or part_info["center_coord"]["z"] == params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]:
            if part_info["type"].startswith("SHS") or part_info["type"][3:6] == "150":
                parts_info[part_id]["offset"] = {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                }
            else:
                if part_info["type"].startswith("C"):
                    parts_info[part_id]["offset"] = {
                    "x": 0.0,
                    "y": 0.0,
                    "z": params["parts"]["cir_sup_beam"]["move"]
                    }
                else:
                    parts_info[part_id]["offset"] = {
                        "x": 0.0,
                        "y": 0.0,
                        "z": params["parts"]["cir_secd_beam"]["move"]
                    }
        # 最后的是门这个方向的
        else:
            if part_info["type"].startswith("SHS") or part_info["type"][3:6] == "150":
                parts_info[part_id]["offset"] = {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                }
            else:
                if part_info["type"].startswith("C"):
                    parts_info[part_id]["offset"] = {
                    "x": params["parts"]["cir_sup_beam"]["move"],
                    "y": 0.0,
                    "z": 0.0
                    }
                else:
                    parts_info[part_id]["offset"] = {
                        "x": params["parts"]["cir_secd_beam"]["move"],
                        "y": 0.0,
                        "z": 0.0
                    }
    return parts_info

# 为构件添加对应优先级信息
def update_priority(parts_info: dict) -> dict:
    for part_id, info in parts_info.items():
        if info["type"].startswith("SHS"):
            if info["dir"]["x"] == 1:
                info["priority"] = 1.0
            else:
                info["priority"] = 1.1

        elif info["type"] in ["HN 150x75", "HM 150x100", "HW 150x150"]:
            info["priority"] = 2.0

        elif info["type"] in ["HN 100x50", "HW 100x100", "HN 125x60", "HW 125x125"]:
            info["priority"] = 3.0

        else:
            info["priority"] = 4.0
    return parts_info



