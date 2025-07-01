# 此处的函数都是为了赋予部件梁方向

# 用于将所有的部件放在一个字典中，取消一层汇总嵌套
def sort_all_parts(parts_info: dict):
    all_parts_info = {}
    for parts_name, parts in parts_info.items():
        for part_id, part_info in parts.items():
            all_parts_info[part_id] = part_info
    return all_parts_info

# 用于拆分构件，接收的是all_parts_info(上面的函数返回的结果)，返回的是一个字典
def split_segments_3d(all_parts_info):
    """
    输入：
        all_parts_info: dict，键为任意 ID，值为：
            {
                "center_coord": {"x": float, "y": float, "z": float},
                "dir":          {"x": 0 or 1, "y": 0 or 1, "z": 0 or 1},
                "length":      float,
                "type":        str,
                "offset":      {"x": float, "y": float, "z": float}
                "priority"    float
            }
        要求：
            - dir = (1,0,0) 表示线段沿 X 轴；
            - dir = (0,1,0) 表示沿 Y 轴；
            - dir = (0,0,1) 表示沿 Z 轴；
            - 其它情况会抛出 ValueError。
    输出：
        返回一个字典，每个键是新的子线段 ID（例如"原ID_index"），值为：
            {
                "center_coord": {"x": float, "y": float, "z": float},
                "dir":          {"x": 0 or 1, "y": 0 or 1, "z": 0 or 1},
                "length":      float,
                "type":        str,           # 来自原始杆件的 type
                "offset":      {"x": float, "y": float, "z": float}  # 继承自原始杆件
                "priority"    float
            }
    """
    eps = 1e-8  # 浮点比较容差

    # 分类存储并记录元数据，包括 offset
    x_segments = {}
    y_segments = {}
    z_segments = {}
    info = {}  # 存储 orientation, fixed_coords, start, end, dir, type, offset

    for sid, data in all_parts_info.items():
        cx = float(data["center_coord"]["x"])
        cy = float(data["center_coord"]["y"])
        cz = float(data["center_coord"]["z"])
        length = float(data["length"])
        dx = float(data["dir"]["x"])
        dy = float(data["dir"]["y"])
        dz = float(data["dir"]["z"])
        seg_type = data.get("type")
        offset = data.get("offset", {"x": 0.0, "y": 0.0, "z": 0.0})
        priority = float(data["priority"])

        if abs(dx - 1.0) < eps and abs(dy) < eps and abs(dz) < eps:
            # 沿 X 轴
            xmin = cx - length/2
            xmax = cx + length/2
            x_segments[sid] = (cy, cz, xmin, xmax)
            info[sid] = {
                "orientation": "X",
                "fixed_coords": {"y": cy, "z": cz},
                "start": xmin,
                "end": xmax,
                "dir": {"x": 1, "y": 0, "z": 0},
                "type": seg_type,
                "offset": offset,
                "priority": priority
            }
        elif abs(dx) < eps and abs(dy - 1.0) < eps and abs(dz) < eps:
            # 沿 Y 轴
            ymin = cy - length/2
            ymax = cy + length/2
            y_segments[sid] = (cx, cz, ymin, ymax)
            info[sid] = {
                "orientation": "Y",
                "fixed_coords": {"x": cx, "z": cz},
                "start": ymin,
                "end": ymax,
                "dir": {"x": 0, "y": 1, "z": 0},
                "type": seg_type,
                "offset": offset,
                "priority": priority
            }
        elif abs(dx) < eps and abs(dy) < eps and abs(dz - 1.0) < eps:
            # 沿 Z 轴
            zmin = cz - length/2
            zmax = cz + length/2
            z_segments[sid] = (cx, cy, zmin, zmax)
            info[sid] = {
                "orientation": "Z",
                "fixed_coords": {"x": cx, "y": cy},
                "start": zmin,
                "end": zmax,
                "dir": {"x": 0, "y": 0, "z": 1},
                "type": seg_type,
                "offset": offset,
                "priority": priority
            }
        else:
            raise ValueError(f"线段 {sid} 的 dir 值不合法：{data['dir']}，仅支持 (1,0,0)、(0,1,0) 或 (0,0,1)。")

    # 初始化切割坐标集合
    data_cuts = {sid: {meta["start"], meta["end"]} for sid, meta in info.items()}

    # 添加切点函数
    def add_cut(a_id, param):
        data_cuts[a_id].add(param)

    # X-Y 相交
    for xid, (y_x, z_x, x_min, x_max) in x_segments.items():
        for yid, (x_y, z_y, y_min, y_max) in y_segments.items():
            if abs(z_x - z_y) < eps and y_min - eps <= y_x <= y_max + eps and x_min - eps <= x_y <= x_max + eps:
                add_cut(xid, x_y)
                add_cut(yid, y_x)
    # X-Z 相交
    for xid, (y_x, z_x, x_min, x_max) in x_segments.items():
        for zid, (x_z, y_z, z_min, z_max) in z_segments.items():
            if abs(y_x - y_z) < eps and z_min - eps <= z_x <= z_max + eps and x_min - eps <= x_z <= x_max + eps:
                add_cut(xid, x_z)
                add_cut(zid, z_x)
    # Y-Z 相交
    for yid, (x_y, z_y, y_min, y_max) in y_segments.items():
        for zid, (x_z, y_z, z_min, z_max) in z_segments.items():
            if abs(x_y - x_z) < eps and z_min - eps <= z_y <= z_max + eps and y_min - eps <= y_z <= y_max + eps:
                add_cut(yid, y_z)
                add_cut(zid, z_y)

    # 生成子线段，存入字典
    result = {}
    for sid, cuts in data_cuts.items():
        meta = info[sid]
        orient = meta["orientation"]
        fixed = meta["fixed_coords"]
        seg_type = meta.get("type")
        offset = meta.get("offset")
        priority = meta.get("priority")

        # 排序并合并近似相同切点
        pts = sorted(cuts)
        merged = []
        prev = None
        for p in pts:
            if prev is None or abs(p - prev) > eps:
                merged.append(p)
                prev = p

        # 按段生成子线段，并组合新的 ID
        for idx in range(len(merged) - 1):
            a = merged[idx]
            b = merged[idx + 1]
            length = b - a
            if length < eps:
                continue
            if orient == "X":
                cx = (a + b) / 2.0; cy = fixed["y"]; cz = fixed["z"]
                dir_dict = {"x": 1, "y": 0, "z": 0}
            elif orient == "Y":
                cx = fixed["x"]; cy = (a + b) / 2.0; cz = fixed["z"]
                dir_dict = {"x": 0, "y": 1, "z": 0}
            else:  # "Z"
                cx = fixed["x"]; cy = fixed["y"]; cz = (a + b) / 2.0
                dir_dict = {"x": 0, "y": 0, "z": 1}
            # 新 ID，可根据需要调整命名规则
            new_id = f"{sid}_{idx}"
            result[new_id] = {
                "center_coord": {"x": cx, "y": cy, "z": cz},
                "dir": dir_dict,
                "length": length,
                "type": seg_type,
                "offset": offset,
                "priority": priority
            }
    return result

# 用于处理上面的函数分割后的列表，分别返回每一个面的构件列表
def sort_parts_by_faces(parts_dict : dict, params : dict):

    right_list = []     # 这个用于存放舱体右侧所有构件的信息，这个面上 Z=0
    offside_list = []   # 这个用于存放舱体对侧所有构件的信息，这个面上 X=0
    left_list = []      # 这个用于存放舱体左侧所有构件的信息，这个面上 Z=舱体宽度
    door_side_list = [] # 这个用于存放舱体门所在侧所有构件的信息，这个面上 X=舱体长度
    top_list = []       # 这个用于存放舱体底部的构件信息，这个面上 Y=舱体高度
    btm_list = []       # 这个用于存放舱体底部的构件信息，这个面上 Y=0
    el_list = []        # 这个用于存放设备间长度方向的构件信息，这个面上 X=舱体长度-设备间宽度
    ew_list = []        # 这个用于存放设备间宽度方向的构件信息，这个面上 Z=舱体宽度-设备间长度

    for part_id, part_info in parts_dict.items():
            if part_info["center_coord"]["z"] == 0:
                right_list.append(part_info)
            elif part_info["center_coord"]["x"] == 0:
                offside_list.append(part_info)
            elif part_info["center_coord"]["z"] == params["cabin"]["width"]["axis_dis"]:
                left_list.append(part_info)
            elif part_info["center_coord"]["x"] == params["cabin"]["length"]["axis_dis"]:
                door_side_list.append(part_info)
            elif part_info["center_coord"]["y"] == params["cabin"]["height"]["axis_dis"]:
                top_list.append(part_info)
            elif part_info["center_coord"]["y"] == 0:
                btm_list.append(part_info)
            elif part_info["center_coord"]["x"] == params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]:
                el_list.append(part_info)
            elif part_info["center_coord"]["z"] == params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]:
                ew_list.append(part_info)

    return right_list, offside_list, left_list, door_side_list, top_list, btm_list, el_list, ew_list

# 用于指派合并后的部件的梁方向
def gen_part_dir(parts_list : list, face: str):
    """
    face说明的是这一个列表中的构件位于哪一个面上
    其中可选值为：
    r: 右面，此时横向构件的方向为(0.0, 0.0, -1.0)，竖向构件的方向为(-1.0, 0.0, 0.0)
    l: 左面，此时横向构件的方向为(0.0, 0.0, -1.0)，竖向构件的方向为(-1.0, 0.0, 0.0)
    o: 门的对面，此时横向构件的方向为(0.0, 0.0, -1.0)，竖向构件的方向为(-1.0, 0.0, 0.0)
    d: 门所在面，此时横向构件的方向为(0.0, 0.0, -1.0)，竖向构件的方向为(-1.0, 0.0, 0.0)
    t: 顶面，此时都是横向构件
    b: 底面，此时都是横向杆件
    el: 设备间长度方向，此时等同于o或者d
    ew: 设备间宽度方向，此时等同于r或者l
    """
    s = f"""
p = mdb.models['Model-1'].parts['cabin_frame']
e = p.edges
"""
    for part_info in parts_list:
        # 首先去找到其方向
        if face == "r" or face == "l" or face == "ew":
            n_h = "(0.0, 0.0, -1.0)"
            n_v = "(-1.0, 0.0, 0.0)"
            if part_info["type"].startswith("C "):
                n_h = "(0.0, 1.0, 0.0)"
            elif part_info["type"].startswith("H"):
                n_h = "(0.0, 1.0, 0.0)"
        elif face == "o" or face == "d" or face == "el":
            n_h = "(1.0, 0.0, 0.0)"
            n_v = "(-1.0, 0.0, 0.0)"
            if part_info["type"].startswith("C "):
                n_h = "(0.0, 1.0, 0.0)"
            elif part_info["type"].startswith("H"):
                n_h = "(0.0, 1.0, 0.0)"
                n_v = "(0.0, 0.0, 1.0)"
        elif face == "t" or face == "b":
            if part_info["dir"]["x"] == 1:
                n_h = "(0.0, 0.0, -1.0)"
                n_v = None
            else:
                n_h = "(1.0, 0.0, 0.0)"
                n_v = None
        else:
            n_h = "(1.0, 0.0, 0.0)"
            n_v = "(-1.0, 0.0, 0.0)"



        if part_info["dir"]["y"] != 1: # 此时说明是水平构件
            s += f"""
edges = e.findAt((({part_info["center_coord"]["x"]}, {part_info["center_coord"]["y"]}, {part_info["center_coord"]["z"]}), ))
region=regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['cabin_frame']
p.assignBeamSectionOrientation(region=region, method=N1_COSINES, n1={n_h})
"""
        else:                           # 此时说明是竖直构件
            s += f"""
edges = e.findAt((({part_info["center_coord"]["x"]}, {part_info["center_coord"]["y"]}, {part_info["center_coord"]["z"]}), ))
region=regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['cabin_frame']
p.assignBeamSectionOrientation(region=region, method=N1_COSINES, n1={n_v})
"""
    return s

# 用于将上面几个函数合并为一个函数供主窗口调用
def gen_all_parts_dir(parts_dict, params):
    right_list, offside_list, left_list, door_side_list, top_list, btm_list, el_list, ew_list = sort_parts_by_faces(parts_dict, params)
    s_r = gen_part_dir(right_list, "r")
    s_o = gen_part_dir(offside_list, "o")
    s_l = gen_part_dir(left_list, "l")
    s_d = gen_part_dir(door_side_list, "d")
    s_t = gen_part_dir(top_list, "t")
    s_b = gen_part_dir(btm_list, "b")
    s_el = gen_part_dir(el_list, "el")
    s_ew = gen_part_dir(ew_list, "ew")
    s = s_r + s_o + s_l + s_d + s_t + s_b + s_el + s_ew
    return s