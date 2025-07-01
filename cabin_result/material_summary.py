
# 计算最后的钢材总重量
def summarize_steel_usage(params, parts_info):
    steel_density = 7850.0
    steel_weight_dict = {
        # SHS 型号
        "SHS 150x4": 18.014,
        "SHS 150x5": 22.26,
        "SHS 150x6": 26.402,
        "SHS 150x8": 33.945,

        # C 型号
        "C 80x40x20x2.5": 3.925,
        "C 80x40x20x3": 4.71,
        "C 100x50x20x2.5": 4.71,
        "C 100x50x20x3": 5.652,
        "C 120x50x20x2.5": 5.103,
        "C 120x50x20x3": 6.123,
        "C 120x60x20x2.5": 5.495,
        "C 120x60x20x3": 6.594,
        "C 120x70x20x2.5": 5.888,
        "C 120x70x20x3": 7.065,
        "C 180x60x20x3": 8.007,
        "C 180x70x20x2.5": 7.065,
        "C 180x70x20x3": 8.478,
        "C 200x50x20x2.5": 6.673,
        "C 200x50x20x3": 8.007,
        "C 200x60x20x2.5": 7.065,
        "C 200x60x20x3": 8.478,
        "C 200x70x20x2.5": 7.458,
        "C 200x70x20x3": 8.949,
        "C 220x60x20x2.5": 7.4567,

        # H 型钢
        "HW 125x125": 23.6,
        "HN 125x60": 13.1,
        "HW 100x100": 16.9,
        "HN 100x50": 9.30,
        "HW 150x150": 31.1,
        "HM 150x100": 22.3,
        "HN 150x75": 14.0,
    }
    summary = {}

    for part_id, info in parts_info.items():
        steel_type = info.get("type")
        length_mm = info.get("length", 0)

        if steel_type is None:
            print(f"Warning: 构件 {part_id} 未指定 type，已跳过。")
            continue

        # 转换长度单位：mm -> m 并保留四位小数
        length_m = round(float(length_mm) / 1000.0, 4)

        if steel_type not in steel_weight_dict:
            print(f"Warning: 构件 {part_id} 的型号 '{steel_type}' 未在 steel_weight_dict 中找到，已跳过。")
            continue

        unit_w = steel_weight_dict[steel_type]  # kg/m

        if steel_type not in summary:
            summary[steel_type] = {
                "total_length_m": 0.0,
                "unit_weight_kg/m": unit_w,
                "total_weight_kg": 0.0,
            }

        summary_entry = summary[steel_type]

        current_length = round(summary_entry["total_length_m"], 4)
        new_length = round(current_length + length_m, 4)
        summary_entry["total_length_m"] = new_length
        part_weight = round(length_m * unit_w, 4)
        current_weight = round(summary_entry["total_weight_kg"], 4)
        new_weight = round(current_weight + part_weight, 4)
        summary_entry["total_weight_kg"] = new_weight

        # 接下来统计钢板面积
        door_area = params["door"]["height"]["axis_dis"] * params["door"]["width"]["axis_dis"] / 1000000.0
        win_num = params["window"]["right"]["num"] + params["window"]["left"]["num"] + params["window"]["offside"]["num"]
        win_area = params["window"]["height"]["axis_dis"] * params["window"]["width"]["axis_dis"] / 1000000.0
        total_win_area = win_num * win_area
        cabin_area = 2 * (params["cabin"]["height"]["axis_dis"] * params["cabin"]["length"]["axis_dis"] +
                          params["cabin"]["height"]["axis_dis"] * params["cabin"]["width"]["axis_dis"] +
                          params["cabin"]["length"]["axis_dis"] * params["cabin"]["width"]["axis_dis"]) / 1000000.0
        plate_area = cabin_area - total_win_area - door_area
        plate_volume = plate_area * 0.005
        plate_weight = plate_volume * steel_density

        summary["steel_plate"] = {
            "total_area_m": plate_area,
            "total_volume_m^3": plate_volume,
            "total_weight_kg": plate_weight
        }

    return summary

# 计算焊点数量
def summarize_wield_points(parts_info: dict, parts_info_processed: dict):
    # 统计思路是分两次统计
    # 首先对于框架梁柱而言按照一整根进行统计，priority为1.1的构件具有两个焊点
    points = 0
    for part_id, info in parts_info.items():
        # 框架梁柱，除了x方向的不统计
        if info["priority"] == 1.1:
            points += 2

        # 环向主梁，全部都要统计
        if info["priority"] == 2.0:
            points += 2

    # 接下来统计切分后的构件
    for part_id, info in parts_info_processed.items():
        if info["priority"] >= 3.0:
            points += 2
    return points