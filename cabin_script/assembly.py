import math

# 装配框架梁柱（不包含窗户两侧的加强柱）
def gen_assem_main_beam_column(params):
    s = f"""
# 导入柱子
a1 = mdb.models['Model-1'].rootAssembly
a1.DatumCsysByDefault(CARTESIAN)
p = mdb.models['Model-1'].parts['frame_column']
a1.Instance(name='frame_column-1', part=p, dependent=ON)
a1.LinearInstancePattern(instanceList=('frame_column-1', ), direction1=(1.0, 
    0.0, 0.0), direction2=(0.0, 0.0, 1.0), number1=2, number2=2, 
    spacing1={params["cabin"]["length"]["axis_dis"]}, spacing2={params["cabin"]["width"]["axis_dis"]})

# 导入纵梁
p = mdb.models['Model-1'].parts['frame_beam_length']
a1.Instance(name='frame_beam_length-1', part=p, dependent=ON)
a1.LinearInstancePattern(instanceList=('frame_beam_length-1', ), direction1=(
    0.0, 1.0, 0.0), direction2=(0.0, 0.0, 1.0), number1=2, number2=2, 
    spacing1={params["cabin"]["height"]["axis_dis"]}, spacing2={params["cabin"]["width"]["axis_dis"]})

# 导入横梁
p = mdb.models['Model-1'].parts['frame_beam_width']
a1.Instance(name='frame_beam_width-1', part=p, dependent=ON)
a1.rotate(instanceList=('frame_beam_width-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.LinearInstancePattern(instanceList=('frame_beam_width-1', ), direction1=(
    1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=2, 
    spacing1={params["cabin"]["length"]["axis_dis"]}, spacing2={params["cabin"]["height"]["axis_dis"]})

# 设备间柱
a1.LinearInstancePattern(instanceList=('frame_column-1-lin-2-2', ), 
    direction1=(0.0, 0.0, -1.0), direction2=(-1.0, 0.0, 0.0), number1=2, 
    number2=2, spacing1={params["equip"]["length"]["axis_dis"]}, spacing2={params["equip"]["width"]["axis_dis"]})
a1.LinearInstancePattern(instanceList=('frame_column-1-lin-2-1', ), 
    direction1=(-1.0, 0.0, 0.0), direction2=(0.0, -1.0, 0.0), number1=2, 
    number2=1, spacing1={params["equip"]["width"]["axis_dis"]}, spacing2=1.0)

# 设备间梁
a1.LinearInstancePattern(instanceList=('frame_beam_width-1-lin-2-1', 
    'frame_beam_width-1-lin-2-2'), direction1=(-1.0, 0.0, 0.0), direction2=(
    0.0, -1.0, 0.0), number1=2, number2=1, spacing1={params["equip"]["width"]["axis_dis"]}, spacing2=1.0)
p = mdb.models['Model-1'].parts['frame_beam_short']
a1.Instance(name='frame_beam_short-1', part=p, dependent=ON)
a1.translate(instanceList=('frame_beam_short-1', ), vector=({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, 0.0, 
    {params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]}))
a1.LinearInstancePattern(instanceList=('frame_beam_short-1', ), direction1=(
    0.0, 1.0, 0.0), direction2=(0.0, -1.0, 0.0), number1=2, number2=1, 
    spacing1={params["cabin"]["height"]["axis_dis"]}, spacing2=1.0)

# 门另一侧的柱子
a1.LinearInstancePattern(instanceList=('frame_column-1-lin-2-1', ), 
    direction1=(0.0, 0.0, 1.0), direction2=(0.0, -1.0, 0.0), number1=2, 
    number2=1, spacing1={params["door"]["width"]["axis_dis"]}, spacing2=1.0)
"""
    return s

# 装配门窗环向次梁、门上方支撑梁以及设备间环向次梁，同时还有上下两个面的环向次梁
def gen_assem_cir_secd_beam(params):
    s = f"""
a = mdb.models['Model-1'].rootAssembly
# 门次梁
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['door_beam']
a.Instance(name='door_beam-1', part=p, dependent=ON)
a.rotate(instanceList=('door_beam-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a.translate(instanceList=('door_beam-1', ), vector=({params["cabin"]["length"]["axis_dis"]}, {params["door"]["ground_clear"]["axis_dis"]}, 0.0))
a.LinearInstancePattern(instanceList=('door_beam-1', ), direction1=(0.0, 1.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, spacing1={params["door"]["height"]["axis_dis"]}, 
    spacing2=1.0)

# 门支撑梁
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_d']
a.Instance(name='sup_beam_d-1', part=p, dependent=ON)
a.rotate(instanceList=('sup_beam_d-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a.translate(instanceList=('sup_beam_d-1', ), vector=({params["cabin"]["length"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"] - params["door"]["top_clear"]["axis_dis"] / 2}, 0.0))

# 侧面窗户次梁
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['window_beam_side']
a.Instance(name='window_beam_side-1', part=p, dependent=ON)
a.translate(instanceList=('window_beam_side-1', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"]}, 0.0))
a.LinearInstancePattern(instanceList=('window_beam_side-1', ), direction1=(0.0, 
    1.0, 0.0), direction2=(0.0, 0.0, 1.0), number1=2, number2=2, 
    spacing1={params["window"]["height"]["axis_dis"]}, spacing2={params["cabin"]["width"]["axis_dis"]})

# 对侧窗户次梁
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['window_beam_offside']
a.Instance(name='window_beam_offside-1', part=p, dependent=ON)
a.rotate(instanceList=('window_beam_offside-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a.translate(instanceList=('window_beam_offside-1', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"]}, 0.0))
a.LinearInstancePattern(instanceList=('window_beam_offside-1', ), direction1=(
    0.0, 1.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, 
    spacing1={params["window"]["height"]["axis_dis"]}, spacing2=1.0)

# 设备间环向次梁
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['equip_beam_length']
a.Instance(name='equip_beam_length-1', part=p, dependent=ON)
a.rotate(instanceList=('equip_beam_length-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a.translate(instanceList=('equip_beam_length-1', ), vector=({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, {params["window"]["ground_clear"]["axis_dis"] + params["window"]["height"]["axis_dis"]}, 
    {params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]}))
a.LinearInstancePattern(instanceList=('equip_beam_length-1', ), direction1=(
0.0, -1.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, 
spacing1={params["window"]["height"]["axis_dis"]}, spacing2=1.0)
p = mdb.models['Model-1'].parts['equip_beam_width']
a.Instance(name='equip_beam_width-1', part=p, dependent=ON)
a = mdb.models['Model-1'].rootAssembly
a.translate(instanceList=('equip_beam_width-1', ), vector=({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, {params["window"]["ground_clear"]["axis_dis"] + params["window"]["height"]["axis_dis"]}, 
    {params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]}))
a.LinearInstancePattern(instanceList=('equip_beam_width-1', ), direction1=(
    0.0, -1.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, 
    spacing1={params["window"]["height"]["axis_dis"]}, spacing2=1.0)

# 门左侧环向次梁
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['door_left_beam']
a.Instance(name='door_left_beam-1', part=p, dependent=ON)
a = mdb.models['Model-1'].rootAssembly
a.rotate(instanceList=('door_left_beam-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a.translate(instanceList=('door_left_beam-1', ), vector=({params["cabin"]["length"]["axis_dis"]}, {params["window"]["ground_clear"]["axis_dis"] + params["window"]["height"]["axis_dis"]}, 
    {params["door"]["width"]["axis_dis"]}))
a.LinearInstancePattern(instanceList=('door_left_beam-1', ), direction1=(
    0.0, -1.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, 
    spacing1={params["window"]["height"]["axis_dis"]}, spacing2=1.0)

# 设备间环向次梁（柱以及顶部中点梁）
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_column']
a.Instance(name='cir_column-equip', part=p, dependent=ON)
a = mdb.models['Model-1'].rootAssembly
a.translate(instanceList=('cir_column-equip', ), vector=({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, 0.0, {params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"] / 2}))
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['equip_beam_w_top']
a.Instance(name='equip_beam_w_top-1', part=p, dependent=ON)
a = mdb.models['Model-1'].rootAssembly
a.translate(instanceList=('equip_beam_w_top-1', ), vector=({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}, {params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"] / 2}))
"""
    return s

# 装配环向主梁以及窗户两侧的框架梁，顺便把上下的环向次梁也装配了
def gen_assem_cir_main_beam(params):
    s = f"""
# 装配上下环向主梁
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_beam']
a.Instance(name='cir_beam-1', part=p, dependent=ON)
a = mdb.models['Model-1'].rootAssembly
a.rotate(instanceList=('cir_beam-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a.translate(instanceList=('cir_beam-1', ), vector=({params["dis"]["value"]}, 0.0, 0.0))
a.LinearInstancePattern(instanceList=('cir_beam-1', ), direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1={params["dis"]["side"]["num"]}, number2=2, spacing1={params["dis"]["value"]}, 
    spacing2={params["cabin"]["height"]["axis_dis"]}) 
"""
    if params["window"]["left"]["num"] != 0:
        # 此时舱体左侧存在窗户
        if params["dis"]["side"]["left_locate"] == params["dis"]["side"]["num"]:
            # 此时说明窗户在最靠近门的那个位置
            left_num = params["dis"]["side"]["num"] - 2  # 这个参数是侧面柱子中除了窗户两侧的方钢管之外其余的H型钢柱子数量
            s += f"""
# 此时阵列的是左侧的窗户，为了避免可能的名称冲突，重新导入框架柱（命名为'frame_column-2'）
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['frame_column']
a.Instance(name='frame_column-2', part=p, dependent=ON)
a.translate(instanceList=('frame_column-2', ), vector=({params["dis"]["value"] * params["dis"]["side"]["num"]}, 0.0, {params["cabin"]["width"]["axis_dis"]}))
a.LinearInstancePattern(instanceList=('frame_column-2', ), direction1=(-1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, spacing1={params["dis"]["value"]}, 
    spacing2=1.0)

# 装配并阵列左侧环向主梁（柱）
## 为了避免可能的名称冲突，重新导入一个部件（命名为'cir_column-2'）
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_column']
a.Instance(name='cir_column-2', part=p, dependent=ON)
a.translate(instanceList=('cir_column-2', ), vector=({params["dis"]["value"]}, 0.0, {params["cabin"]["width"]["axis_dis"]}))
# 阵列左侧
a.LinearInstancePattern(instanceList=('cir_column-2', ), direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1={left_num}, number2=1, spacing1={params["dis"]["value"]}, 
    spacing2=1.0)
"""
        else:
            # 此时说明窗户的位置位于中间的某个位置
            locate = params["dis"]["side"]["left_locate"]  # 窗户位置
            num = params["dis"]["side"]["num"]  # 柱子的数量
            s += f"""
# 首先导入框架柱（命名为'frame_column-3'）
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['frame_column']
a.Instance(name='frame_column-3', part=p, dependent=ON)
a.translate(instanceList=('frame_column-3', ), vector=({params["dis"]["value"] * locate}, 0.0, {params["cabin"]["width"]["axis_dis"]}))
a.LinearInstancePattern(instanceList=('frame_column-3', ), direction1=(-1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, spacing1={params["dis"]["value"]}, 
    spacing2=1.0)
"""
            if locate == num - 1:
                # 此时说明窗户位于从门数位置数第二个空间内，接下来开始装配其他的柱子
                s += f"""
# 随后首先将靠近门一侧的环向主梁（柱）移动过来，这个是不用阵列的
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_column']
# 这里的环向次梁（柱）也是重新导入的（命名为'cir_column-3'）
a.Instance(name='cir_column-3', part=p, dependent=ON)
a.translate(instanceList=('cir_column-3', ), vector=({params["dis"]["value"] * num}, 0.0, {params["cabin"]["width"]["axis_dis"]}))
# 接下来需要导入另一边需要阵列的
p = mdb.models['Model-1'].parts['cir_column']
# 这里的环向次梁（柱）也是重新导入的（命名为'cir_column-4'）
a.Instance(name='cir_column-4', part=p, dependent=ON)
a.translate(instanceList=('cir_column-4', ), vector=({params["dis"]["value"]}, 0.0, {params["cabin"]["width"]["axis_dis"]}))
a.LinearInstancePattern(instanceList=('cir_column-4', ), direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1={num - 3}, number2=1, spacing1={params["dis"]["value"]}, 
    spacing2=1.0)
"""
            elif locate == 2:
                # 此时说明窗户位于远离门的位置的第二个空隙内，此时只需要阵列一个方向即可
                s += f"""
# 随后首先将靠近门一侧的环向主梁（柱）移动过来
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_column']
# 这里的环向次梁（柱）也是重新导入的（命名为'cir_column-5'）
a.Instance(name='cir_column-5', part=p, dependent=ON)
a.translate(instanceList=('cir_column-5', ), vector=({params["dis"]["value"] * num}, 0.0, {params["cabin"]["width"]["axis_dis"]}))
a.LinearInstancePattern(instanceList=('cir_column-5', ), direction1=(-1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1={num - locate}, number2=1, spacing1={params["dis"]["value"]}, 
    spacing2=1.0)
    """
            else:
                # 此时说明窗户位于从门数位置数第二个空间内，则两侧的柱都需要阵列
                s += f"""
# 随后首先将靠近门一侧的环向主梁（柱）移动过来
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_column']
# 这里的环向次梁（柱）也是重新导入的（命名为'cir_column-5'）
a.Instance(name='cir_column-5', part=p, dependent=ON)
a.translate(instanceList=('cir_column-5', ), vector=({params["dis"]["value"] * num}, 0.0, {params["cabin"]["width"]["axis_dis"]}))
a.LinearInstancePattern(instanceList=('cir_column-5', ), direction1=(-1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1={num - locate}, number2=1, spacing1={params["dis"]["value"]}, 
    spacing2=1.0)
# 接下来需要导入另一边需要阵列的
p = mdb.models['Model-1'].parts['cir_column']
# 这里的环向次梁（柱）也是重新导入的（命名为'cir_column-6'）
a.Instance(name='cir_column-6', part=p, dependent=ON)
a.translate(instanceList=('cir_column-6', ), vector=({params["dis"]["value"]}, 0.0, {params["cabin"]["width"]["axis_dis"]}))
a.LinearInstancePattern(instanceList=('cir_column-6', ), direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1={locate - 2}, number2=1, spacing1={params["dis"]["value"]}, 
    spacing2=1.0)
"""
    else:
        # 此时左侧不存在窗户，选择柱子挨个阵列即可，命名为"cir_column-ll"
        s += f"""
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_column']
a.Instance(name='cir_column-ll', part=p, dependent=ON)
a.translate(instanceList=('cir_column-ll', ), vector=({params["dis"]["value"]}, 0.0, {params["cabin"]["width"]["axis_dis"]}))
a.LinearInstancePattern(instanceList=('cir_column-ll', ), direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1={params["dis"]["side"]["num"]}, number2=1, spacing1={params["dis"]["value"]}, 
    spacing2=1.0)
"""

    if params["window"]["right"]["num"] != 0:
        # 此时舱体右侧存在窗户
        if params["dis"]["side"]["right_locate"] == params["dis"]["side"]["num"]:
            # 此时说明是在最靠近门的边上
            right_num = params["dis"]["side"]["num"] - 2
            s += f"""
# 此时阵列的是右侧的窗户，为了避免可能的名称冲突，重新导入框架柱（命名为'frame_column-4'）
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['frame_column']
a.Instance(name='frame_column-4', part=p, dependent=ON)
a.translate(instanceList=('frame_column-4', ), vector=({params["dis"]["value"] * params["dis"]["side"]["num"]}, 0.0, 0.0))
a.LinearInstancePattern(instanceList=('frame_column-4', ), direction1=(-1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, spacing1={params["dis"]["value"]}, 
    spacing2=1.0)

# 装配并阵列右侧环向主梁（柱）
## 为了避免可能的名称冲突，重新导入一个部件（命名为'cir_column-7'）
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_column']
a.Instance(name='cir_column-7', part=p, dependent=ON)
a.translate(instanceList=('cir_column-7', ), vector=({params["dis"]["value"]}, 0.0, 0.0))
# 阵列左侧
a.LinearInstancePattern(instanceList=('cir_column-7', ), direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1={right_num}, number2=1, spacing1={params["dis"]["value"]}, 
    spacing2=1.0)
"""
        else:
            # 此时说明窗户的位置位于中间位置
            locate = params["dis"]["side"]["right_locate"]  # 窗户位置
            num = params["dis"]["side"]["num"]  # 窗户可以存在的空间总数
            s += f"""
# 首先导入框架柱（命名为'frame_column-5）
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['frame_column']
a.Instance(name='frame_column-5', part=p, dependent=ON)
a.translate(instanceList=('frame_column-5', ), vector=({params["dis"]["value"] * locate}, 0.0, 0.0))
a.LinearInstancePattern(instanceList=('frame_column-5', ), direction1=(-1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, spacing1={params["dis"]["value"]}, 
    spacing2=1.0)
"""
            if locate == num - 1:
                # 此时说明窗户位于从门数位置数第二个空间内，接下来开始装配其他的柱子
                s += f"""
# 随后首先将靠近门一侧的环向主梁（柱）移动过来，这个是不用阵列的
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_column']
# 这里的环向次梁（柱）也是重新导入的（命名为'cir_column-8'）
a.Instance(name='cir_column-8', part=p, dependent=ON)
a.translate(instanceList=('cir_column-8', ), vector=({params["dis"]["value"] * num}, 0.0, 0.0))
# 接下来需要导入另一边需要阵列的
p = mdb.models['Model-1'].parts['cir_column']
# 这里的环向次梁（柱）也是重新导入的（命名为'cir_column-9'）
a.Instance(name='cir_column-9', part=p, dependent=ON)
a.translate(instanceList=('cir_column-9', ), vector=({params["dis"]["value"]}, 0.0, 0.0))
a.LinearInstancePattern(instanceList=('cir_column-9', ), direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1={num - 3}, number2=1, spacing1={params["dis"]["value"]}, 
    spacing2=1.0)
"""
            elif locate == 2:
                # 此时说明窗户位于远离门的位置的第二个空隙内，此时只需要阵列一个方向即可
                s += f"""
# 随后首先将靠近门一侧的环向主梁（柱）移动过来
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_column']
# 这里的环向次梁（柱）也是重新导入的（命名为'cir_column-10'）
a.Instance(name='cir_column-10', part=p, dependent=ON)
a.translate(instanceList=('cir_column-10', ), vector=({params["dis"]["value"] * num}, 0.0, 0.0))
a.LinearInstancePattern(instanceList=('cir_column-10', ), direction1=(-1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1={num - locate}, number2=1, spacing1={params["dis"]["value"]}, 
    spacing2=1.0)
    """
            else:
                # 此时说明窗户位于从门数位置数第二个空间内，则两侧的柱都需要阵列
                s += f"""
# 随后首先将靠近门一侧的环向主梁（柱）移动过来
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_column']
# 这里的环向次梁（柱）也是重新导入的（命名为'cir_column-10'）
a.Instance(name='cir_column-10', part=p, dependent=ON)
a.translate(instanceList=('cir_column-10', ), vector=({params["dis"]["value"] * num}, 0.0, 0.0))
a.LinearInstancePattern(instanceList=('cir_column-10', ), direction1=(-1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1={num - locate}, number2=1, spacing1={params["dis"]["value"]}, 
    spacing2=1.0)
# 接下来需要导入另一边需要阵列的
p = mdb.models['Model-1'].parts['cir_column']
# 这里的环向次梁（柱）也是重新导入的（命名为'cir_column-11'）
a.Instance(name='cir_column-11', part=p, dependent=ON)
a.translate(instanceList=('cir_column-11', ), vector=({params["dis"]["value"]}, 0.0, 0.0))
a.LinearInstancePattern(instanceList=('cir_column-11', ), direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1={locate - 2}, number2=1, spacing1={params["dis"]["value"]}, 
    spacing2=1.0)
"""
    else:
        # 此时右侧不存在窗户，选择柱子挨个阵列即可，命名为"cir_column-rr"
        s += f"""
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_column']
a.Instance(name='cir_column-rr', part=p, dependent=ON)
a.translate(instanceList=('cir_column-rr', ), vector=({params["dis"]["value"]}, 0.0, 0.0))
a.LinearInstancePattern(instanceList=('cir_column-rr', ), direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 1.0, 0.0), number1={params["dis"]["side"]["num"]}, number2=1, spacing1={params["dis"]["value"]}, 
    spacing2=1.0)
"""

    # 接下来考虑对侧窗户的数量
    num = params["dis"]["offside"]["num"]["num"]
    axis_gap = params["dis"]["offside"]["axis_gap"]["axis_gap"]

    if params["window"]["offside"]["num"] == 1:
        s += f"""
## 此时阵列的是对侧的窗户，且仅有一扇，为了避免可能的名称冲突，重新导入框架柱（命名为'frame_column-6'）
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['frame_column']
a.Instance(name='frame_column-6', part=p, dependent=ON)
a.translate(instanceList=('frame_column-6', ), vector=(0.0, 0.0, {axis_gap + (num / 2 - 1) * params["dis"]["value"]}))
a.LinearInstancePattern(instanceList=('frame_column-6', ), direction1=(1.0, 0.0, 
0.0), direction2=(0.0, 0.0, 1.0), number1=1, number2=2, spacing1=1.0, 
spacing2={params["dis"]["value"]})
"""
        if num != 2:
            # 如果只有两根柱子的话就没有必要再阵列环向次梁（柱）了
            s += f"""
## 接下来导入除了框架柱外的环向主梁（柱），为了避免可能的名称冲突，重新导入环向主梁（柱）（命名为'cir_column-12'）
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_column']
a.Instance(name='cir_column-12', part=p, dependent=ON)
a.translate(instanceList=('cir_column-12', ), vector=(0.0, 0.0, {axis_gap}))
a.LinearInstancePattern(instanceList=('cir_column-12', ), direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 0.0, 1.0), number1=1, number2={int(num / 2 - 1)}, spacing1=1.0, 
    spacing2={params["dis"]["value"]})
## 此时完成了右侧的环向次梁（柱）的阵列，再去阵列左侧，步骤同上，重新导入环向主梁（柱）（命名为'cir_column-13'）
a.Instance(name='cir_column-13', part=p, dependent=ON)
a.translate(instanceList=('cir_column-13', ), vector=(0.0, 0.0, {axis_gap + (num / 2 + 1) * params["dis"]["value"]}))
a.LinearInstancePattern(instanceList=('cir_column-13', ), direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 0.0, 1.0), number1=1, number2={int(num / 2 - 1)}, spacing1=1.0, 
    spacing2={params["dis"]["value"]})
"""
    elif params["window"]["offside"]["num"] == 2:
        # 此时舱体对侧存在两扇窗户，使用 dis -> offside -> num -> num1 或 num2，使用其中的奇数
        s += f"""
## 此时阵列的是对侧的窗户，且有两扇，为了避免可能的名称冲突，重新导入框架柱（命名为'frame_column-7'）
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['frame_column']
a.Instance(name='frame_column-7', part=p, dependent=ON)
a.translate(instanceList=('frame_column-7', ), vector=(0.0, 0.0, {axis_gap + math.floor(num / 2 - 1) * params["dis"]["value"]}))
a.LinearInstancePattern(instanceList=('frame_column-7', ), direction1=(1.0, 0.0, 
0.0), direction2=(0.0, 0.0, 1.0), number1=1, number2=3, spacing1=1.0, 
spacing2={params["dis"]["value"]})
"""
        if num == 5:
            # 如果只有两根柱子的话就没有必要再阵列环向次梁（柱）了
            s += f"""
## 接下来导入除了框架柱外的环向主梁（柱），为了避免可能的名称冲突，重新导入环向主梁（柱）（命名为'cir_column-14'）
## 此时总共有5根柱子，除去中间3根左右两侧只有1根，只需要导入不需要阵列
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_column']
a.Instance(name='cir_column-14', part=p, dependent=ON)
a.translate(instanceList=('cir_column-14', ), vector=(0.0, 0.0, {axis_gap}))
## 此时完成了右侧的环向次梁（柱）的布置，再去阵列左侧，步骤同上，重新导入环向主梁（柱）（命名为'cir_column-15'）
a.Instance(name='cir_column-15', part=p, dependent=ON)
a.translate(instanceList=('cir_column-15', ), vector=(0.0, 0.0, {params["cabin"]["width"]["axis_dis"] - axis_gap}))
"""
        elif num == 7:
            s += f"""
## 接下来导入除了框架柱外的环向主梁（柱），为了避免可能的名称冲突，重新导入环向主梁（柱）（命名为'cir_column-16'）
## 此时总共有7根柱子，除去中间3根左右两侧只有2根，需要阵列
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_column']
a.Instance(name='cir_column-16', part=p, dependent=ON)
a.translate(instanceList=('cir_column-16', ), vector=(0.0, 0.0, {axis_gap}))
a.LinearInstancePattern(instanceList=('cir_column-16', ), direction1=(1.0, 0.0, 
0.0), direction2=(0.0, 0.0, 1.0), number1=1, number2=2, spacing1=1.0, 
spacing2={params["dis"]["value"]})
## 此时完成了右侧的环向次梁（柱）的布置，再去阵列左侧，步骤同上，重新导入环向主梁（柱）（命名为'cir_column-17'）
a.Instance(name='cir_column-17', part=p, dependent=ON)
a.translate(instanceList=('cir_column-17', ), vector=(0.0, 0.0, {params["cabin"]["width"]["axis_dis"] - axis_gap}))
a.LinearInstancePattern(instanceList=('cir_column-17', ), direction1=(1.0, 0.0, 
0.0), direction2=(0.0, 0.0, -1.0), number1=1, number2=2, spacing1=1.0, 
spacing2={params["dis"]["value"]})
"""
    elif params["window"]["offside"]["num"] == 3:
        # 此时存在三扇窗户，此时存在一种极端情况，就是三扇窗刚好占满整个面
        s += f"""
## 此时阵列的是对侧的窗户，且有三扇，为了避免可能的名称冲突，重新导入框架柱（命名为'frame_column-8'）
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['frame_column']
a.Instance(name='frame_column-8', part=p, dependent=ON)
a.translate(instanceList=('frame_column-8', ), vector=(0.0, 0.0, {axis_gap + math.floor(num / 2 - 2) * params["dis"]["value"]}))
a.LinearInstancePattern(instanceList=('frame_column-8', ), direction1=(1.0, 0.0, 
0.0), direction2=(0.0, 0.0, 1.0), number1=1, number2=4, spacing1=1.0, 
spacing2={params["dis"]["value"]})
"""
        if num != 4:
            # 如果仅有四根柱子的话就没有必要继续布置柱子了
            s += f"""
## 接下来导入除了框架柱外的环向主梁（柱），为了避免可能的名称冲突，重新导入环向主梁（柱）（命名为'cir_column-18'）
## 此时总共有5根柱子，除去中间3根左右两侧只有1根，只需要导入不需要阵列
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_column']
a.Instance(name='cir_column-18', part=p, dependent=ON)
a.translate(instanceList=('cir_column-18', ), vector=(0.0, 0.0, {axis_gap}))
## 此时完成了右侧的环向次梁（柱）的布置，再去阵列左侧，步骤同上，重新导入环向主梁（柱）（命名为'cir_column-19'）
a.Instance(name='cir_column-19', part=p, dependent=ON)
a.translate(instanceList=('cir_column-19', ), vector=(0.0, 0.0, {params["cabin"]["width"]["axis_dis"] - axis_gap}))
"""
    else:
        # 此时对侧不布置窗户，处于节省材料考虑选取较少的
        s += f"""
# 此时对侧不布置窗户，所有的柱子都是环向主梁（柱）（命名为'cir_column-20'）
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_column']
a.Instance(name='cir_column-20', part=p, dependent=ON)
a.translate(instanceList=('cir_column-20', ), vector=(0.0, 0.0, {axis_gap}))
a.LinearInstancePattern(instanceList=('cir_column-20', ), direction1=(1.0, 0.0, 
    0.0), direction2=(0.0, 0.0, 1.0), number1=1, number2={num}, spacing1=1.0, 
    spacing2={params["dis"]["value"]})
"""

    # 接下来装配上下两个面的环向次梁
    s += f"""
# 首先装配上方的环向次梁
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_secd_beam_top']
a.Instance(name='cir_secd_beam_top-1', part=p, dependent=ON)
a.translate(instanceList=('cir_secd_beam_top-1',), vector=(0.0, {params["cabin"]["height"]["axis_dis"]}, {params["dis"]["offside"]["axis_gap"]["axis_gap"]}))
a.LinearInstancePattern(instanceList=('cir_secd_beam_top-1',), direction1=(0.0, 0.0, 1.0), direction2=(0.0, 1.0, 0.0),
    number1={params["dis"]["offside"]["num"]["num"]}, number2=1,
    spacing1={params["dis"]["value"]}, spacing2={params["cabin"]["height"]["axis_dis"]})
# 其次装配下方
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['cir_secd_beam_btm']
a.Instance(name='cir_secd_beam_btm-1', part=p, dependent=ON)
a.translate(instanceList=('cir_secd_beam_btm-1',), vector=(0.0, 0.0, {params["dis"]["offside"]["axis_gap"]["axis_gap"]}))
a.LinearInstancePattern(instanceList=('cir_secd_beam_btm-1',), direction1=(0.0, 0.0, 1.0), direction2=(0.0, 1.0, 0.0),
    number1={params["dis"]["offside"]["num"]["num"]}, number2=1,
    spacing1={params["dis"]["value"]}, spacing2={params["cabin"]["height"]["axis_dis"]})
"""
    return s

# 装配门顶部的环向次梁
def gen_assem_door_beam_h(params):
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
            params["dis"]["offside"]["axis_gap"]["axis_gap"] - (num - 2) / 2 * params["dis"]["value"]
        if d <= 200.0:
            # 此时不可以外延
            n = int(n-1)

    if n == 1:
        s = f"""
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['equip_beam_w_top']
# 为了避免命名冲突，重新进行命名（命名为'equip_beam_w_top_door'）
a.Instance(name='equip_beam_w_top_door', part=p, dependent=ON)
a = mdb.models['Model-1'].rootAssembly
a.translate(instanceList=('equip_beam_w_top_door', ), vector=({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}, {params["dis"]["offside"]["axis_gap"]["axis_gap"]}))
# 再导入下部的
p = mdb.models['Model-1'].parts['equip_beam_w_btm']
a.Instance(name='equip_beam_w_btm_door', part=p, dependent=ON)
a = mdb.models['Model-1'].rootAssembly
a.translate(instanceList=('equip_beam_w_btm_door', ), vector=({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, 0.0, {params["dis"]["offside"]["axis_gap"]["axis_gap"]}))

"""
    else:
        s = f"""
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['equip_beam_w_top']
# 为了避免命名冲突，重新进行命名（命名为'equip_beam_w_top_door'）
a.Instance(name='equip_beam_w_top_door', part=p, dependent=ON)
a = mdb.models['Model-1'].rootAssembly
a.translate(instanceList=('equip_beam_w_top_door', ), vector=({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}, {params["dis"]["offside"]["axis_gap"]["axis_gap"]}))
a.LinearInstancePattern(instanceList=('equip_beam_w_top_door', ), direction1=(0.0, 
    0.0, 1.0), direction2=(0.0, -1.0, 0.0), number1={int(n)}, number2=1, 
    spacing1={params["dis"]["value"]}, spacing2={params["cabin"]["height"]["axis_dis"]})
# 再导入下方的
p = mdb.models['Model-1'].parts['equip_beam_w_btm']
a.Instance(name='equip_beam_w_btm_door', part=p, dependent=ON)
a = mdb.models['Model-1'].rootAssembly
a.translate(instanceList=('equip_beam_w_btm_door', ), vector=({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, 0.0, {params["dis"]["offside"]["axis_gap"]["axis_gap"]}))
a.LinearInstancePattern(instanceList=('equip_beam_w_btm_door', ), direction1=(0.0, 
    0.0, 1.0), direction2=(0.0, -1.0, 0.0), number1={int(n)}, number2=1, 
    spacing1={params["dis"]["value"]}, spacing2={params["cabin"]["height"]["axis_dis"]})
"""
    return s

# 装配所有侧面的环向支撑梁
def gen_assem_sup_beam(params):
    s = ""

    # 首先获取几个相关的参数
    dis = params["dis"]["value"] # 窗户轴线距离
    ln = params["window"]["left"]["num"] # 左侧窗户数量
    ll = params["window"]["left"]["locate"] # 左侧窗户位置
    rn = params["window"]["right"]["num"] # 右侧窗户数量
    rl = params["window"]["right"]["locate"] # 右侧窗户位置
    on = params["window"]["offside"]["num"] # 对侧窗户数量，不需要单独说明位置
    mid_num = params["sup"]["mid"]["num"]
    mid_gap = params["sup"]["mid"]["gap"]
    btm_num = params["sup"]["btm"]["num"]
    btm_gap = params["sup"]["btm"]["gap"]
    up_num = params["sup"]["up"]["num"]
    up_gap = params["sup"]["up"]["gap"]

    # 首先装配底部的环向支撑梁
    # 在此引入的所有部件的结尾命名都为"-1"
    if btm_num != 0:
        # 首先装配右侧
        s += f"""
# 右侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_right']
a1.Instance(name='sup_beam_right-1', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('sup_beam_right-1', ), vector=(0.0, {btm_gap}, 0.0))
# 对侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_offside']
a1.Instance(name='sup_beam_offside-1', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.rotate(instanceList=('sup_beam_offside-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('sup_beam_offside-1', ), vector=(0.0, {btm_gap}, 0.0))
# 左侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_left']
a1.Instance(name='sup_beam_left-1', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('sup_beam_left-1', ), vector=(0.0, {btm_gap}, {params["cabin"]["width"]["axis_dis"]}))
# 设备间长度方向
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_el']
a1.Instance(name='sup_beam_el-1', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.rotate(instanceList=('sup_beam_el-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('sup_beam_el-1', ), vector=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, {btm_gap}, {params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]}))
# 设备间宽度方向
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_ew']
a1.Instance(name='sup_beam_ew-1', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('sup_beam_ew-1', ), vector=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, {btm_gap}, {params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]}))
# 门左侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_dl']
a1.Instance(name='sup_beam_dl-1', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.rotate(instanceList=('sup_beam_dl-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('sup_beam_dl-1', ), vector=({params["cabin"]["length"]["axis_dis"]}, {btm_gap}, {params["door"]["width"]["axis_dis"]}))
"""

    # 随后装配顶部的环向支撑梁
    # 在此引入的所有部件的结尾命名都为"-2"
    if up_num != 0:
        # 首先装配右侧
        s += f"""
# 右侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_right']
a1.Instance(name='sup_beam_right-2', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('sup_beam_right-2', ), vector=(0.0, {params["cabin"]["height"]["axis_dis"]-up_gap}, 0.0))
# 对侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_offside']
a1.Instance(name='sup_beam_offside-2', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.rotate(instanceList=('sup_beam_offside-2', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('sup_beam_offside-2', ), vector=(0.0, {params["cabin"]["height"]["axis_dis"]-up_gap}, 0.0))
# 左侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_left']
a1.Instance(name='sup_beam_left-2', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('sup_beam_left-2', ), vector=(0.0, {params["cabin"]["height"]["axis_dis"]-up_gap}, {params["cabin"]["width"]["axis_dis"]}))
# 设备间长度方向
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_el']
a1.Instance(name='sup_beam_el-2', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.rotate(instanceList=('sup_beam_el-2', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('sup_beam_el-2', ), vector=({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]-up_gap}, {params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]}))
# 设备间宽度方向
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_ew']
a1.Instance(name='sup_beam_ew-2', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('sup_beam_ew-2', ), vector=({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]-up_gap}, {params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]}))
# 门左侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_dl']
a1.Instance(name='sup_beam_dl-2', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.rotate(instanceList=('sup_beam_dl-2', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('sup_beam_dl-2', ), vector=({params["cabin"]["length"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]-up_gap}, {params["door"]["width"]["axis_dis"]}))
"""

    # 最后装配中间的环向支撑梁
    # 在此引入的所有部件的结尾命名都为"-3"
    if mid_num != 0:
        # 首先判断是否需要阵列操作，也就是看支撑梁的个数是否大于1、

        # 等于1的时候不需要阵列
        if mid_num == 1:
            # 首先去安装舱体右侧的支撑梁，此时需要判断是否有窗户，如果没有窗户直接就可以安装
            if rn == 0:
                s += f"""
# 首先是右侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_right']
a1.Instance(name='sup_beam_right-3', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_right-3', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"]+mid_gap}, 0.0))
"""
            else: # 此时右侧存在窗户，需要分别引入窗户左右的梁然后分别移动
                s += f"""
# 首先移动窗户右侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_right_wr']
a1.Instance(name='sup_beam_right_wr-3', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_right_wr-3', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"]+mid_gap}, 0.0))
# 再移动窗户左侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_right_wl']
a1.Instance(name='sup_beam_right_wl-3', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_right_wl-3', ), vector=({rl*dis}, {params["window"]["ground_clear"]["axis_dis"]+mid_gap}, 0.0))
"""

            # 接下来安装舱体对侧的支撑梁，同样还是要判断是否存在窗户
            if on == 0:
                s += f"""
# 装配对侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_offside']
a1.Instance(name='sup_beam_offside-3', part=p, dependent=ON)
a1.rotate(instanceList=('sup_beam_offside-3', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('sup_beam_offside-3', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"]+mid_gap}, 0.0))
"""
            else:
                # 此时对侧存在窗户
                s += f"""
# 装配对侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_offside_w']
a1.Instance(name='sup_beam_offside_w-3', part=p, dependent=ON)
a1.rotate(instanceList=('sup_beam_offside_w-3', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('sup_beam_offside_w-3', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"]+mid_gap}, 0.0))
# 向水平方向阵列
a1.LinearInstancePattern(instanceList=('sup_beam_offside_w-3', ), direction1=(
    0.0, 0.0, 1.0), direction2=(1.0, 0.0, 0.0), number1=2, number2=1, 
    spacing1={params["cabin"]["width"]["axis_dis"]-(params["cabin"]["width"]["axis_dis"]-params["window"]["offside"]["num"]*params["dis"]["value"])/2}, spacing2=1.0)
"""

            # 接下来安装舱体左侧的支撑梁，同样还是要判断是否存在窗户
            if ln == 0:
                s += f"""
# 舱体左侧支撑梁
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_left']
a1.Instance(name='sup_beam_left-3', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_left-3', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"] + mid_gap}, {params["cabin"]["width"]["axis_dis"]}))
"""
            else:
                s += f"""
# 首先移动窗户右侧（靠近舱门一侧）
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_left_wr']
a1.Instance(name='sup_beam_left_wr-3', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_left_wr-3', ), vector=({ll * dis}, {params["window"]["ground_clear"]["axis_dis"] + mid_gap}, {params["cabin"]["width"]["axis_dis"]}))
# 再移动窗户左侧（远离舱门一侧）
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_left_wl']
a1.Instance(name='sup_beam_left_wl-3', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_left_wl-3', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"] + mid_gap}, {params["cabin"]["width"]["axis_dis"]}))
"""

            # 其余的就是不存在窗户的面，逐个面上进行阵列就好了
            s += f"""
# 首先是设备间长度方向
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_el']
a1.Instance(name='sup_beam_el-3', part=p, dependent=ON)
a1.rotate(instanceList=('sup_beam_el-3', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('sup_beam_el-3', ), vector=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, {params["window"]["ground_clear"]["axis_dis"]+mid_gap}, {params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]}))
# 其次是设备间宽度方向
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_ew']
a1.Instance(name='sup_beam_ew-3', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_ew-3', ), vector=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, {params["window"]["ground_clear"]["axis_dis"]+mid_gap}, 0.0))
# 最后是门的左侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_dl']
a1.Instance(name='sup_beam_dl-3', part=p, dependent=ON)
a1.rotate(instanceList=('sup_beam_dl-3', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('sup_beam_dl-3', ), vector=({params["cabin"]["length"]["axis_dis"]}, {params["window"]["ground_clear"]["axis_dis"]+mid_gap}, {params["door"]["width"]["axis_dis"]}))
"""

        # 此时右侧存在多根支撑梁，需要在高度方向进行阵列，注意还是要判断有无窗户
        else:
            if rn == 0:
                # 此时不存在窗户
                s += f"""
# 首先是右侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_right']
a1.Instance(name='sup_beam_right-3', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_right-3', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"]+mid_gap}, 0.0))
a1 = mdb.models['Model-1'].rootAssembly
a1.LinearInstancePattern(instanceList=('sup_beam_right-3', ), direction1=(
    0.0, 1.0, 0.0), direction2=(0.0, 0.0, 1.0), number1={mid_num}, number2=1, 
    spacing1={mid_gap}, spacing2=1.0)
"""
            else:
                # 此时存在窗户，需要左右两端分别进行阵列
                s += f"""
# 首先移动窗户右侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_right_wr']
a1.Instance(name='sup_beam_right_wr-3', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_right_wr-3', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"]+mid_gap}, 0.0))
a1.LinearInstancePattern(instanceList=('sup_beam_right_wr-3', ), direction1=(
    0.0, 1.0, 0.0), direction2=(0.0, 0.0, 1.0), number1={mid_num}, number2=1, 
    spacing1={mid_gap}, spacing2=1.0)
# 再移动窗户左侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_right_wl']
a1.Instance(name='sup_beam_right_wl-3', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_right_wl-3', ), vector=({rl*dis}, {params["window"]["ground_clear"]["axis_dis"]+mid_gap}, 0.0))
a1.LinearInstancePattern(instanceList=('sup_beam_right_wl-3', ), direction1=(
    0.0, 1.0, 0.0), direction2=(0.0, 0.0, 1.0), number1={mid_num}, number2=1, 
    spacing1={mid_gap}, spacing2=1.0)
"""

            if on == 0:
                s += f"""
# 装配对侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_offside']
a1.Instance(name='sup_beam_offside-3', part=p, dependent=ON)
a1.rotate(instanceList=('sup_beam_offside-3', ), axisPoint=(0.0, 0.0, 0.0), 
axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('sup_beam_offside-3', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"] + mid_gap}, 0.0))
a1.LinearInstancePattern(instanceList=('sup_beam_offside-3', ), direction1=(
    0.0, 1.0, 0.0), direction2=(1.0, 0.0, 0.0), number1={mid_num}, number2=1, 
    spacing1={mid_gap}, spacing2=1.0)
"""
            else:
                # 此时对侧存在窗户
                s += f"""
# 装配对侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_offside_w']
a1.Instance(name='sup_beam_offside_w-3', part=p, dependent=ON)
a1.rotate(instanceList=('sup_beam_offside_w-3', ), axisPoint=(0.0, 0.0, 0.0), 
axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('sup_beam_offside_w-3', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"] + mid_gap}, 0.0))
# 向水平以及高度方向方向阵列
a1.LinearInstancePattern(instanceList=('sup_beam_offside_w-3', ), direction1=(
    0.0, 0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1=2, number2={mid_num}, 
    spacing1={params["cabin"]["width"]["axis_dis"] - (params["cabin"]["width"]["axis_dis"] - params["window"]["offside"]["num"] * params["dis"]["value"]) / 2}, spacing2={mid_gap})
"""

            if ln == 0:
                s += f"""
# 舱体左侧支撑梁
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_left']
a1.Instance(name='sup_beam_left-3', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_left-3', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"] + mid_gap}, {params["cabin"]["width"]["axis_dis"]}))
a1.LinearInstancePattern(instanceList=('sup_beam_left-3', ), direction1=(
    0.0, 1.0, 0.0), direction2=(0.0, 0.0, 1.0), number1={mid_num}, number2=1, 
    spacing1={mid_gap}, spacing2=1.0)
"""
            else:
                s += f"""
# 首先移动窗户右侧（靠近舱门一侧）
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_left_wr']
a1.Instance(name='sup_beam_left_wr-3', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_left_wr-3', ), vector=({ll * dis}, {params["window"]["ground_clear"]["axis_dis"] + mid_gap}, {params["cabin"]["width"]["axis_dis"]}))
a1.LinearInstancePattern(instanceList=('sup_beam_left_wr-3', ), direction1=(
    0.0, 1.0, 0.0), direction2=(0.0, 0.0, 1.0), number1={mid_num}, number2=1, 
    spacing1={mid_gap}, spacing2=1.0)
# 再移动窗户左侧（远离舱门一侧）
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_left_wl']
a1.Instance(name='sup_beam_left_wl-3', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_left_wl-3', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"] + mid_gap}, {params["cabin"]["width"]["axis_dis"]}))
a1.LinearInstancePattern(instanceList=('sup_beam_left_wl-3', ), direction1=(
    0.0, 1.0, 0.0), direction2=(0.0, 0.0, 1.0), number1={mid_num}, number2=1, 
    spacing1={mid_gap}, spacing2=1.0)
"""

                # 其余的就是不存在窗户的面，逐个面上进行阵列就好了

        s += f"""
# 首先是设备间长度方向
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_el']
a1.Instance(name='sup_beam_el-3', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.rotate(instanceList=('sup_beam_el-3', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('sup_beam_el-3', ), vector=({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, {params["window"]["ground_clear"]["axis_dis"] + mid_gap}, {params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]}))
a1.LinearInstancePattern(instanceList=('sup_beam_el-3', ), direction1=(
    0.0, 0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1=1, number2={mid_num}, 
    spacing1=0.0, spacing2={mid_gap})
# 其次是设备间宽度方向
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_ew']
a1.Instance(name='sup_beam_ew-3', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_ew-3', ), vector=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, {params["window"]["ground_clear"]["axis_dis"]+mid_gap}, {params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]}))
a1.LinearInstancePattern(instanceList=('sup_beam_ew-3', ), direction1=(
    0.0, 0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1=1, number2={mid_num}, 
    spacing1=0.0, spacing2={mid_gap})
# 最后是门的左侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_dl']
a1.Instance(name='sup_beam_dl-3', part=p, dependent=ON)
a1.rotate(instanceList=('sup_beam_dl-3', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('sup_beam_dl-3', ), vector=({params["cabin"]["length"]["axis_dis"]}, {params["window"]["ground_clear"]["axis_dis"]+mid_gap}, {params["door"]["width"]["axis_dis"]}))
a1.LinearInstancePattern(instanceList=('sup_beam_dl-3', ), direction1=(
    0.0, 0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1=1, number2={mid_num}, 
    spacing1=0.0, spacing2={mid_gap})
"""

    return s

# 装配顶部以及底部的环向支撑梁
def gen_assem_top_sup_beam(params):
    s = ""
    # 这个地方的构思是：
    # 1. 边缘两个间隙部分单独给出中间是否布置1个环向支撑（最多只能有一个）
    # 2. 中间所有柱子的空隙之间是否布置一个环向支撑（最多只能有一个）
    # 3. 这个地方目前没有考虑门上面外延的那一部分，还需要修改

    # 首先从边缘的环向支撑梁入手
    if params["sup"]["top_side"]["num"] == 1:
        s += f"""
# 导入部件
# 首先导入底部
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_btm']
a1.Instance(name='sup_beam_btm-1', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_btm-1', ), vector=(0.0, 0.0, {params["sup"]["top_side"]["gap"]}))
a1.LinearInstancePattern(instanceList=('sup_beam_btm-1', ), direction1=(0.0, 
    0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, 
    spacing1={params["cabin"]["width"]["axis_dis"]-params["sup"]["top_side"]["gap"]*2}, spacing2={params["cabin"]["height"]["axis_dis"]})
# 其次导入顶部
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_top']
a1.Instance(name='sup_beam_top-1', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_top-1', ), vector=(0.0, {params["cabin"]["height"]["axis_dis"]}, {params["sup"]["top_side"]["gap"]}))
a1.LinearInstancePattern(instanceList=('sup_beam_top-1', ), direction1=(0.0, 
    0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, 
    spacing1={params["cabin"]["width"]["axis_dis"]-params["sup"]["top_side"]["gap"]*2}, spacing2={params["cabin"]["height"]["axis_dis"]})
"""
    # 接下来处理中间部分的环向支撑梁
    if params["sup"]["top_mid"]["num"] == 1:
        s += f"""
# 导入部件
# 首先导入底部
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_btm']
a1.Instance(name='sup_beam_btm-2', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_btm-2', ), vector=(0.0, 0.0, {params["dis"]["offside"]["axis_gap"]["axis_gap"]+params["sup"]["top_mid"]["gap"]}))
a1.LinearInstancePattern(instanceList=('sup_beam_btm-2', ), direction1=(0.0, 
    0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1={params["dis"]["offside"]["num"]["num"]-1}, number2=1, 
    spacing1={params["sup"]["top_mid"]["gap"]*2}, spacing2={params["cabin"]["height"]["axis_dis"]})
# 其次导入顶部
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_top']
a1.Instance(name='sup_beam_top-2', part=p, dependent=ON)
a1.translate(instanceList=('sup_beam_top-2', ), vector=(0.0, {params["cabin"]["height"]["axis_dis"]}, {params["dis"]["offside"]["axis_gap"]["axis_gap"]+params["sup"]["top_mid"]["gap"]}))
a1.LinearInstancePattern(instanceList=('sup_beam_top-2', ), direction1=(0.0, 
    0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1={params["dis"]["offside"]["num"]["num"]-1}, number2=1, 
    spacing1={params["sup"]["top_mid"]["gap"]*2}, spacing2={params["cabin"]["height"]["axis_dis"]})
"""

    return s

# 装配门上部的环向支撑梁
def gen_assem_top_sup_beam_ew(params):
    s = ""
    # 这个地方的思路是
    # 1.首先看最外侧是否布置了环向支撑梁，如果布置了的话就直接外延出来
    # 2.如果中间也布置了的话，先看外延出来了几根
    if params["sup"]["top_side"]["num"] == 1:
        # 此时外延一根，包括上下两个面的
        s += f"""
# 首先移动上面的
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_ew_top']
a1.Instance(name='sup_beam_ew_top-1', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('sup_beam_ew_top-1', ), vector=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}, 
    {params["dis"]["offside"]["axis_gap"]["axis_gap"]/2}))
# 再移动下面的
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_ew_btm']
a1.Instance(name='sup_beam_ew_btm-1', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('sup_beam_ew_btm-1', ), vector=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, 0.0, 
    {params["dis"]["offside"]["axis_gap"]["axis_gap"]/2}))
"""
    if params["sup"]["top_mid"]["num"] == 1:
        # 此时一定会有外延数量-1根的环向支撑梁
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
                params["dis"]["offside"]["axis_gap"]["axis_gap"] - (num - 2) / 2 * params["dis"]["value"]
            if d <= 200.0:
                # 此时不可以外延
                n = int(n - 1)

        n -= 1 # 此时记录的是一定会有的环向支撑梁的数量
        if n == 1:
            s += f"""
# 先移动上面的
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_ew_top']
a1.Instance(name='sup_beam_ew_top-2', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('sup_beam_ew_top-2', ), vector=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}, 
    {params["dis"]["offside"]["axis_gap"]["axis_gap"]+params["sup"]["top_mid"]["gap"]}))
# 再移动下面的
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_ew_btm']
a1.Instance(name='sup_beam_ew_btm-2', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('sup_beam_ew_btm-2', ), vector=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, 0.0,
    {params["dis"]["offside"]["axis_gap"]["axis_gap"]+params["sup"]["top_mid"]["gap"]}))
"""
        elif n > 1:
            # 此时需要阵列
            s += f"""
# 先移动上面的
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_ew_top']
a1.Instance(name='sup_beam_ew_top-2', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('sup_beam_ew_top-2', ), vector=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}, 
    {params["dis"]["offside"]["axis_gap"]["axis_gap"]+params["sup"]["top_mid"]["gap"]}))
a1.LinearInstancePattern(instanceList=('sup_beam_ew_top-2', ), direction1=(0.0, 
    0.0, 1.0), direction2=(0.0, 0.0, 0.0), number1={n}, number2=1, 
    spacing1={params["window"]["width"]["axis_dis"]}, spacing2=1.0)
# 再移动下面的
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_ew_btm']
a1.Instance(name='sup_beam_ew_btm-2', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('sup_beam_ew_btm-2', ), vector=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, 0.0,
    {params["dis"]["offside"]["axis_gap"]["axis_gap"]+params["sup"]["top_mid"]["gap"]}))
a1.LinearInstancePattern(instanceList=('sup_beam_ew_btm-2', ), direction1=(0.0, 
    0.0, 1.0), direction2=(0.0, 0.0, 0.0), number1={n}, number2=1, 
    spacing1={params["window"]["width"]["axis_dis"]}, spacing2=1.0)
"""

        # 接下来就需要判断如果再外延一根的话距离会不会超限
        n += 1
        dis = params["dis"]["offside"]["axis_gap"]["axis_gap"] + params["sup"]["top_mid"]["gap"] + (n-1)*params["window"]["width"]["axis_dis"]
        if params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"] - dis > 200:
            # 此时说明并不会超限，那么需要将这一根也伸出来
            s += f"""
# 首先移动上面的
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_ew_top']
a1.Instance(name='sup_beam_ew_top-3', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('sup_beam_ew_top-3', ), vector=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}, 
    {dis}))
# 再移动下面的
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['sup_beam_ew_btm']
a1.Instance(name='sup_beam_ew_btm-3', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('sup_beam_ew_btm-3', ), vector=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, 0.0, 
    {dis}))
"""
    return s

# 合并所有部件，形成框架整体
def gen_assem_all_parts(params, parts_info_processed : dict):
    s =  f"""
a1 = mdb.models['Model-1'].rootAssembly
# 收集所有实例
all_instances = tuple(a1.instances.values())

# 一次性合并
a1.InstanceFromBooleanMerge(
    name='cabin_frame', 
    instances=all_instances, 
    originalInstances=DELETE, 
    domain=GEOMETRY
)

# 合并之后先把框架删除掉
del a1.features['cabin_frame-1']

# 需要反转一些梁的切向
# 需要反转的面如下：
# 1.舱体右面
# 2.舱体前面
# 3.设备间宽度面
"""
    # 寻找需要反转切向的杆件中心坐标
    coords_list = []
    for part_id, part_info in parts_info_processed.items():
        if part_info["type"].startswith(("C", "H")): # 检查是否以 "C" 或 "H" 开头
            # 首先寻找舱体右侧
            if part_info["center_coord"]["z"] == 0:
                coords_list.append((part_info["center_coord"]["x"], part_info["center_coord"]["y"], part_info["center_coord"]["z"]))
            # 随后寻找门一侧
            elif part_info["center_coord"]["x"] == params["cabin"]["length"]["axis_dis"]:
                coords_list.append(
                    (part_info["center_coord"]["x"], part_info["center_coord"]["y"], part_info["center_coord"]["z"]))
            # 随后寻找设备间长度一侧
            elif part_info["center_coord"]["x"] == params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]:
                coords_list.append(
                    (part_info["center_coord"]["x"], part_info["center_coord"]["y"], part_info["center_coord"]["z"]))
    s += f"""
p = mdb.models['Model-1'].parts['cabin_frame']
e = p.edges
coord_list = {coords_list}
edges = e.findAt(*tuple((coord,) for coord in coord_list))
regions = regionToolset.Region(edges=edges)
p.flipTangent(regions=regions)
"""
    return s

# 装配蒙皮钢板，并将其合并为一个部件
def gen_assem_plate(params):
    s = ""
    # 首先来装配右侧
    if params["window"]["right"]["num"] == 0:
        s += f"""
# 导入右侧一整块板
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_r_whole']
a1.Instance(name='plate_r_whole-1', part=p, dependent=ON)
"""
    else:
        s += f"""
# 首先装配窗户以及上下位置
# 窗户
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_window']
a1.Instance(name='plate_window_r-1', part=p, dependent=ON)
a1.translate(instanceList=('plate_window_r-1', ), vector=({(params["window"]["right"]["locate"]-1)*params["window"]["width"]["axis_dis"]}, {params["window"]["ground_clear"]["axis_dis"]}, 0.0))
# 窗户上方
p = mdb.models['Model-1'].parts['plate_window_up']
a1.Instance(name='plate_window_up_r-1', part=p, dependent=ON)
a1.translate(instanceList=('plate_window_up_r-1', ), vector=({(params["window"]["right"]["locate"]-1)*params["window"]["width"]["axis_dis"]}, {params["window"]["ground_clear"]["axis_dis"]+params["window"]["height"]["axis_dis"]}, 0.0))
# 窗户下方
p = mdb.models['Model-1'].parts['plate_window_down']
a1.Instance(name='plate_window_down_r-1', part=p, dependent=ON)
a1.translate(instanceList=('plate_window_down_r-1', ), vector=({(params["window"]["right"]["locate"]-1)*params["window"]["width"]["axis_dis"]}, 0.0, 0.0))
# 窗户右侧
p = mdb.models['Model-1'].parts['plate_r_wr']
a1.Instance(name='plate_r_wr-1', part=p, dependent=ON)
# 窗户左侧
p = mdb.models['Model-1'].parts['plate_r_wl']
a1.Instance(name='plate_r_wl-1', part=p, dependent=ON)
a1.translate(instanceList=('plate_r_wl-1', ), vector=({params["window"]["right"]["locate"]*params["window"]["width"]["axis_dis"]}, 0.0, 0.0))
"""

    # 装配左侧
    if params["window"]["left"]["num"] == 0:
        s += f"""
# 导入左侧一整块不含设备间的板
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_l_whole']
a1.Instance(name='plate_l_whole-1', part=p, dependent=ON)
a1.translate(instanceList=('plate_l_whole-1', ), vector=(0.0, 0.0, {params["cabin"]["width"]["axis_dis"]}))
"""
    else:
        s += f"""
# 首先装配窗户以及上下位置
# 窗户
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_window']
a1.Instance(name='plate_window_l-1', part=p, dependent=ON)
a1.translate(instanceList=('plate_window_l-1', ), vector=({(params["window"]["left"]["locate"] - 1) * params["window"]["width"]["axis_dis"]}, {params["window"]["ground_clear"]["axis_dis"]}, {params["cabin"]["width"]["axis_dis"]}))
# 窗户上方
p = mdb.models['Model-1'].parts['plate_window_up']
a1.Instance(name='plate_window_up_l-1', part=p, dependent=ON)
a1.translate(instanceList=('plate_window_up_l-1', ), vector=({(params["window"]["left"]["locate"] - 1) * params["window"]["width"]["axis_dis"]}, {params["window"]["ground_clear"]["axis_dis"] + params["window"]["height"]["axis_dis"]}, {params["cabin"]["width"]["axis_dis"]}))
# 窗户下方
p = mdb.models['Model-1'].parts['plate_window_down']
a1.Instance(name='plate_window_down_l-1', part=p, dependent=ON)
a1.translate(instanceList=('plate_window_down_l-1', ), vector=({(params["window"]["left"]["locate"] - 1) * params["window"]["width"]["axis_dis"]}, 0.0, {params["cabin"]["width"]["axis_dis"]}))
# 窗户左侧
p = mdb.models['Model-1'].parts['plate_l_wl']
a1.Instance(name='plate_l_wl-1', part=p, dependent=ON)
a1.translate(instanceList=('plate_l_wl-1', ), vector=(0.0, 0.0, {params["cabin"]["width"]["axis_dis"]}))
# 窗户右侧
p = mdb.models['Model-1'].parts['plate_l_wr']
a1.Instance(name='plate_l_wr-1', part=p, dependent=ON)
a1.translate(instanceList=('plate_l_wr-1', ), vector=({params["window"]["left"]["locate"] * params["window"]["width"]["axis_dis"]}, 0.0, {params["cabin"]["width"]["axis_dis"]}))
"""

    # 接下来装配对侧
    if params["window"]["offside"]["num"] == 0:
        s += f"""
# 导入对侧一整块板
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_off_whole']
a1.Instance(name='plate_off_whole-1', part=p, dependent=ON)
a1.rotate(instanceList=('plate_off_whole-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
"""
    else:
        # 如果只有一扇窗户的话不需要阵列
        if params["window"]["offside"]["num"] == 1:
            s += f"""
# 首先装配窗户以及上下位置
# 窗户
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_window']
a1.Instance(name='plate_window_o-1', part=p, dependent=ON)
a1.rotate(instanceList=('plate_window_o-1', ), axisPoint=(0.0, 0.0, 0.0),
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0) 
a1.translate(instanceList=('plate_window_o-1', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"]}, {(params["cabin"]["width"]["axis_dis"]-params["window"]["width"]["axis_dis"])/2}))
# 窗户上方
p = mdb.models['Model-1'].parts['plate_window_up']
a1.Instance(name='plate_window_up_o-1', part=p, dependent=ON)
a1.rotate(instanceList=('plate_window_up_o-1', ), axisPoint=(0.0, 0.0, 0.0),
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0) 
a1.translate(instanceList=('plate_window_up_o-1', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"] + params["window"]["height"]["axis_dis"]}, {(params["cabin"]["width"]["axis_dis"]-params["window"]["width"]["axis_dis"])/2}))
# 窗户下方
p = mdb.models['Model-1'].parts['plate_window_down']
a1.Instance(name='plate_window_down_o-1', part=p, dependent=ON)
a1.rotate(instanceList=('plate_window_down_o-1', ), axisPoint=(0.0, 0.0, 0.0),
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0) 
a1.translate(instanceList=('plate_window_down_o-1', ), vector=(0.0, 0.0, {(params["cabin"]["width"]["axis_dis"]-params["window"]["width"]["axis_dis"])/2}))
# 窗户两侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_off_w']
a1.Instance(name='plate_off_w-1', part=p, dependent=ON)
a1.rotate(instanceList=('plate_off_w-1', ), axisPoint=(0.0, 0.0, 0.0),
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0) 
a1.LinearInstancePattern(instanceList=('plate_off_w-1', ), direction1=(0.0, 
    0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, 
    spacing1={(params["cabin"]["width"]["axis_dis"]-params["window"]["width"]["axis_dis"])/2+params["window"]["width"]["axis_dis"]}, spacing2=1.0)
"""
        else:
            # 此时存在多扇窗户需要阵列才可以
            s += f"""
# 首先装配窗户以及上下位置
# 窗户
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_window']
a1.Instance(name='plate_window_o-1', part=p, dependent=ON)
a1.rotate(instanceList=('plate_window_o-1', ), axisPoint=(0.0, 0.0, 0.0),
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0) 
a1.translate(instanceList=('plate_window_o-1', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"]}, {(params["cabin"]["width"]["axis_dis"]-params["window"]["width"]["axis_dis"]*params["window"]["offside"]["num"])/2}))
a1.LinearInstancePattern(instanceList=('plate_window_o-1', ), direction1=(0.0, 
    0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1={params["window"]["offside"]["num"]}, number2=1, 
    spacing1={params["window"]["width"]["axis_dis"]}, spacing2=1.0)

# 窗户上方
p = mdb.models['Model-1'].parts['plate_window_up']
a1.Instance(name='plate_window_up_o-1', part=p, dependent=ON)
a1.rotate(instanceList=('plate_window_up_o-1', ), axisPoint=(0.0, 0.0, 0.0),
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0) 
a1.translate(instanceList=('plate_window_up_o-1', ), vector=(0.0, {params["window"]["ground_clear"]["axis_dis"] + params["window"]["height"]["axis_dis"]}, {(params["cabin"]["width"]["axis_dis"]-params["window"]["width"]["axis_dis"]*params["window"]["offside"]["num"])/2}))
a1.LinearInstancePattern(instanceList=('plate_window_up_o-1', ), direction1=(0.0, 
    0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1={params["window"]["offside"]["num"]}, number2=1, 
    spacing1={params["window"]["width"]["axis_dis"]}, spacing2=1.0)

# 窗户下方
p = mdb.models['Model-1'].parts['plate_window_down']
a1.Instance(name='plate_window_down_o-1', part=p, dependent=ON)
a1.rotate(instanceList=('plate_window_down_o-1', ), axisPoint=(0.0, 0.0, 0.0),
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0) 
a1.translate(instanceList=('plate_window_down_o-1', ), vector=(0.0, 0.0, {(params["cabin"]["width"]["axis_dis"]-params["window"]["width"]["axis_dis"]*params["window"]["offside"]["num"])/2}))
a1.LinearInstancePattern(instanceList=('plate_window_down_o-1', ), direction1=(0.0, 
    0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1={params["window"]["offside"]["num"]}, number2=1, 
    spacing1={params["window"]["width"]["axis_dis"]}, spacing2=1.0)

# 窗户两侧
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_off_w']
a1.Instance(name='plate_off_w-1', part=p, dependent=ON)
a1.rotate(instanceList=('plate_off_w-1', ), axisPoint=(0.0, 0.0, 0.0),
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0) 
a1.LinearInstancePattern(instanceList=('plate_off_w-1', ), direction1=(0.0, 
    0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, 
    spacing1={(params["cabin"]["width"]["axis_dis"]-params["window"]["width"]["axis_dis"]*params["window"]["offside"]["num"])/2+params["window"]["width"]["axis_dis"]*params["window"]["offside"]["num"]}, spacing2=1.0)
"""

    # 接下来装配顶部以及底部
    s += f"""
# 导入顶部舱体部分的板
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_top_cabin']
a1.Instance(name='plate_top_cabin-1', part=p, dependent=ON)
a1.translate(instanceList=('plate_top_cabin-1', ), vector=(0.0, {params["cabin"]["height"]["axis_dis"]}, 0.0))
a1.rotate(instanceList=('plate_top_cabin-1', ), axisPoint=(0.0, {params["cabin"]["height"]["axis_dis"]}, 0.0), 
    axisDirection=(1.0, 0.0, 0.0), angle=90.0)
a1.LinearInstancePattern(instanceList=('plate_top_cabin-1', ), direction1=(0.0, 
    -1.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, 
    spacing1={params["cabin"]["height"]["axis_dis"]}, spacing2=1.0)
"""

    # 再找到设备间上方的
    s += f"""
# 导入设备间上方板
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_top_equip']
a1.Instance(name='plate_top_equip-1', part=p, dependent=ON)
a1.translate(instanceList=('plate_top_equip-1', ), vector=({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}, {params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]}))
a1.rotate(instanceList=('plate_top_equip-1', ), axisPoint=({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}, {params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]}),
    axisDirection=(1.0, 0.0, 0.0), angle=90.0) 
a1.LinearInstancePattern(instanceList=('plate_top_equip-1', ), direction1=(0.0, 
    -1.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, 
    spacing1={params["cabin"]["height"]["axis_dis"]}, spacing2=1.0)
"""

    # 再找到门上方的
    s += f"""
# 导入门上方板
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_top_door']
a1.Instance(name='plate_top_door-1', part=p, dependent=ON)
a1.translate(instanceList=('plate_top_door-1', ), vector=({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}, 0.0))
a1.rotate(instanceList=('plate_top_door-1', ), axisPoint=({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}, 0.0),
    axisDirection=(1.0, 0.0, 0.0), angle=90.0) 
a1.LinearInstancePattern(instanceList=('plate_top_door-1', ), direction1=(0.0, 
    -1.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, 
    spacing1={params["cabin"]["height"]["axis_dis"]}, spacing2=1.0)
"""

    # 再者是设备间宽度方向的
    s += f"""
# 导入两个设备间宽度板
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_equip_w']
a1.Instance(name='plate_equip_w-1', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.translate(instanceList=('plate_equip_w-1', ), vector=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, 0.0, {params["cabin"]["width"]["axis_dis"]}))
a1.LinearInstancePattern(instanceList=('plate_equip_w-1', ), direction1=(0.0, 
    0.0, -1.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, 
    spacing1={params["equip"]["length"]["axis_dis"]}, spacing2=1.0)
f41 = a.instances['plate_equip_w-1'].faces
faces41 = f41.findAt((({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"] / 2}, {params["cabin"]["height"]["axis_dis"]/2}, {params["cabin"]["width"]["axis_dis"]}), ))
f42 = a.instances['plate_equip_w-1-lin-2-1'].faces
faces42 = f42.findAt((({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"] / 2}, {params["cabin"]["height"]["axis_dis"]/2}, {params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]}), ))
faces_equip_w = faces41 + faces42
"""

    # 再者是设备间长度方向
    s += f"""
# 导入两个设备间长度板
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_equip_l']
a1.Instance(name='plate_equip_l-1', part=p, dependent=ON)
a1 = mdb.models['Model-1'].rootAssembly
a1.rotate(instanceList=('plate_equip_l-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('plate_equip_l-1', ), vector=({params["cabin"]["length"]["axis_dis"]}, 0.0, {params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]}))
a1.LinearInstancePattern(instanceList=('plate_equip_l-1', ), direction1=(-1.0, 
    0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, 
    spacing1={params["equip"]["width"]["axis_dis"]}, spacing2=1.0)
f41 = a.instances['plate_equip_l-1'].faces
faces41 = f41.findAt((({params["cabin"]["length"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"] / 2}, {params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]/2}), ))
f42 = a.instances['plate_equip_l-1-lin-2-1'].faces
faces42 = f42.findAt((({params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"] / 2}, {params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]/2}), ))
faces_equip_l = faces41 + faces42
"""

    # 再者是门周围的
    s += f"""
# 门钢板
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_door']
a1.Instance(name='plate_door-1', part=p, dependent=ON)
a1.rotate(instanceList=('plate_door-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('plate_door-1', ), vector=({params["cabin"]["length"]["axis_dis"]}, {params["door"]["ground_clear"]["axis_dis"]}, 0.0))

# 门左侧钢板
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_door_left']
a1.Instance(name='plate_door_left-1', part=p, dependent=ON)
a1.rotate(instanceList=('plate_door_left-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('plate_door_left-1', ), vector=({params["cabin"]["length"]["axis_dis"]}, 0.0, {params["door"]["width"]["axis_dis"]}))

# 门上方钢板
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_door_up']
a1.Instance(name='plate_door_up-1', part=p, dependent=ON)
a1.rotate(instanceList=('plate_door_up-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('plate_door_up-1', ), vector=({params["cabin"]["length"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]-params["door"]["top_clear"]["axis_dis"]}, 0.0))

# 门下方钢板
a1 = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['plate_door_down']
a1.Instance(name='plate_door_down-1', part=p, dependent=ON)
a1.rotate(instanceList=('plate_door_down-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
a1.translate(instanceList=('plate_door_down-1', ), vector=({params["cabin"]["length"]["axis_dis"]}, 0.0, 0.0))
"""

    # 将所有的面合并成一个部件，并把原本的框架导入进来
    s += f"""
a1 = mdb.models['Model-1'].rootAssembly
# 收集所有实例
all_instances = tuple(a1.instances.values())
# 一次性合并
a1.InstanceFromBooleanMerge(
    name='cabin_plates', 
    instances=all_instances, 
    keepIntersections=ON, 
    originalInstances=DELETE, 
    mergeNodes=NONE, 
    domain=BOTH)
# 划分网格
# 舱体网格
p = mdb.models['Model-1'].parts['cabin_plates']
p.seedPart(size=50.0, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
# 导入框架
p = mdb.models['Model-1'].parts['cabin_frame']
a1.Instance(name='cabin_frame-1', part=p, dependent=ON)
"""


    return s

# 创建框架与蒙皮的绑定关系
def gen_tie():
    # 首先创建舱体杆件的集合，包括线以及顶点
    s= f"""
# 获取所有的点线的数量
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['cabin_frame-1'].edges
v1 = a.instances['cabin_frame-1'].vertices
e1_num = len(e1)
v1_num = len(v1)
edges1 = e1[0:e1_num]
verts1 = v1[0:v1_num]
a.Set(edges=edges1, vertices=verts1, name='set_cabin_frame')
"""
    s += f"""
# 首先要获取所有点线面的个数
a = mdb.models['Model-1'].rootAssembly
f1 = a.instances['cabin_plates-1'].faces
v1 = a.instances['cabin_plates-1'].vertices
e1 = a.instances['cabin_plates-1'].edges
num_f1 = len(f1)
num_v1 = len(v1)
num_e1 = len(e1)
faces1 = f1[0:num_f1]
verts1 = v1[0:num_v1]
edges1 = e1[0:num_e1]
a.Set(faces=faces1, vertices=verts1, edges=edges1, name='set_plates')
"""
    # 最后生成绑定关系
    s += f"""
a = mdb.models['Model-1'].rootAssembly
region1=a.sets['set_cabin_frame']
a = mdb.models['Model-1'].rootAssembly
region2=a.sets['set_plates']
mdb.models['Model-1'].Tie(name='tie', master=region2, slave=region1, 
    positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, thickness=ON)
"""
    return s