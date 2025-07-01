import os
import pandas as pd
import numpy as np
from typing import Optional, Dict

# 在开始计算前清空文件夹里的多余内容
def delete_file(params):
    folder_path = f'{params["output"]["dir"]}'

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # 如果是文件，且不是以 .py 结尾的，就删除
        if os.path.isfile(file_path) and not filename.lower().endswith('.py'):
            os.remove(file_path)

# 将位移与节点信息进行合并
def merge_nodes_displacements(params: Dict, nodes_filename: str, disp_filename: str, output_filename: Optional[str]) -> None:
    """
    合并节点坐标和位移数据表，并将结果保存到目录中，无返回值。
    在合并前将节点坐标表中 'Label' 列改为 'NodeLabel'，合并后仅保留一个 'NodeLabel' 列。
    合并结果按 'Magnitude' 列降序排列。

    参数：
    - params: 包含输出目录信息的字典，需包含 params['output']['dir']。
    - nodes_filename: 节点坐标文件名，默认为 'CABIN_FRAME_nodes.csv'。
    - disp_filename: 位移数据文件名，默认为 'U_CABIN_FRAME.csv'。
    - output_filename: 可选，合并后保存的文件名。如果未提供，则使用默认名称 '<nodes_filename>_merged.csv'。
    """
    # 从 params 中获取目录
    try:
        directory = params['output']['dir']
    except KeyError:
        raise KeyError("params 中缺少 'output' 或 'dir' 键: 请确保 params['output']['dir'] 存在")

    # 检查类型
    if not isinstance(directory, str):
        raise TypeError(f"输出目录应为字符串路径，但得到: {type(directory)}")

    # 构造文件路径
    nodes_path = os.path.join(directory, nodes_filename)
    disp_path = os.path.join(directory, disp_filename)

    # 检查文件是否存在
    if not os.path.isfile(nodes_path):
        raise FileNotFoundError(f"节点文件未找到: {nodes_path}")
    if not os.path.isfile(disp_path):
        raise FileNotFoundError(f"位移文件未找到: {disp_path}")

    # 读取 CSV
    try:
        nodes_df = pd.read_csv(nodes_path)
    except Exception as e:
        raise IOError(f"读取节点文件失败: {e}")
    try:
        disp_df = pd.read_csv(disp_path)
    except Exception as e:
        raise IOError(f"读取位移文件失败: {e}")

    # 检查并重命名第一列 Label -> NodeLabel
    if 'Label' not in nodes_df.columns:
        raise KeyError("节点坐标表中缺少 'Label' 列，无法重命名为 'NodeLabel'")
    # 如果已有 NodeLabel 列，先删除以避免冲突
    if 'NodeLabel' in nodes_df.columns:
        nodes_df = nodes_df.drop(columns=['NodeLabel'])
    nodes_df.rename(columns={'Label': 'NodeLabel'}, inplace=True)

    # 检查位移表中 'NodeLabel'
    if 'NodeLabel' not in disp_df.columns:
        raise KeyError("位移表中缺少 'NodeLabel' 列，无法按 NodeLabel 合并")

    # 合并数据：以 NodeLabel 为键
    merged_df = pd.merge(nodes_df, disp_df, on='NodeLabel', how='inner')

    # 检查 'Magnitude' 列是否存在以便排序
    if 'Magnitude' not in merged_df.columns:
        raise KeyError("合并后结果中缺少 'Magnitude' 列，无法按其排序")

    # 按 Magnitude 降序排列
    merged_df.sort_values(by='Magnitude', ascending=False, inplace=True)

    # 确定保存文件名
    if output_filename:
        save_name = output_filename
    else:
        stem = os.path.splitext(nodes_filename)[0]
        save_name = f"{stem}_merged.csv"
    output_path = os.path.join(directory, save_name)

    # 保存结果
    try:
        merged_df.to_csv(output_path, index=False)
    except Exception as e:
        raise IOError(f"保存合并文件失败: {e}")

    # 删除原始文件
    for path, desc in [(nodes_path, "节点文件"), (disp_path, "位移文件")]:
        try:
            os.remove(path)
        except Exception as e:
            raise IOError(f"删除原始文件失败 ({desc}: {path}): {e}")

# 生成两个csv，用于存放部件的节点坐标
def get_part_node_coord_csv(params):
    s = f"""
# -*- coding: utf-8 -*-
from odbAccess import openOdb
odb_path = "{params["output"]["dir"]}" + r"\Job-Mises.odb"
odb = openOdb(odb_path)

instance_name = 'CABIN_PLATES-1'
a = odb.rootAssembly
instance = a.instances[instance_name]
output_path = "{params["output"]["dir"]}" + r'\CABIN_PLATES_nodes.csv'

f = open(output_path, 'w')
f.write('Label,X,Y,Z\\n')
for node in instance.nodes:
    # node.label 为节点编号（整数）
    # node.coordinates 为三元组 (x, y, z)
    x, y, z = node.coordinates
    # 写入 csv 格式
    f.write('%d,%g,%g,%g\\n' % (node.label, x, y, z))

f.close()

instance_name = 'CABIN_FRAME-1'
a = odb.rootAssembly
instance = a.instances[instance_name]
output_path = "{params["output"]["dir"]}" + r'\CABIN_FRAME_nodes.csv'

f = open(output_path, 'w')
f.write('Label,X,Y,Z\\n')
for node in instance.nodes:
    # node.label 为节点编号（整数）
    # node.coordinates 为三元组 (x, y, z)
    x, y, z = node.coordinates
    # 写入 csv 格式
    f.write('%d,%g,%g,%g\\n' % (node.label, x, y, z))

f.close()
"""
    return s

# 生成位移结果文件
def get_result_u(params):
    s = f"""
from textRepr import *

# 获取 odb 对象
odb_path = "{params["output"]["dir"]}" + r"\\Job-Deflection.odb"
odb = openOdb(odb_path)
# 指定分析步
step = odb.steps["Step-2"]
# 选取最后一帧
frame = step.frames[-1]
# 获取全局位移场变量
dis_field = frame.fieldOutputs["U"]
# 获取舱体框架的节点集合
cabin_frame_node_set = odb.rootAssembly.instances["CABIN_FRAME-1"].nodeSets["NODE_SET_CABIN_FRAME"]
# 提取部件上的位移
local_dis_value = dis_field.getSubset(region=cabin_frame_node_set)

# 创建 CSV 并保存：写入 NodeLabel, Ux, Uy, Uz, Magnitude，按 magnitude 降序排列
output_csv = "{params["output"]["dir"]}" + r"\\U_CABIN_FRAME.csv"
with open(output_csv, 'w') as f:
    f.write("NodeLabel,Ux,Uy,Uz,Magnitude\\n")
    # 对 values 按 magnitude 降序排序
    for node_value in sorted(local_dis_value.values, key=lambda v: v.magnitude, reverse=True):
        ux, uy, uz = node_value.data
        mag = node_value.magnitude
        f.write("%d,%g,%g,%g,%g\\n" % (node_value.nodeLabel, ux, uy, uz, mag))

# 获取舱体钢板的节点集合
cabin_plate_node_set = odb.rootAssembly.instances["CABIN_PLATES-1"].nodeSets["NODE_SET_CABIN_PLATES"]
# 提取部件上的位移
local_dis_value = dis_field.getSubset(region=cabin_plate_node_set)
# 创建 CSV 并保存：写入 NodeLabel, Ux, Uy, Uz, Magnitude，同样按 magnitude 降序排列
output_csv = "{params["output"]["dir"]}" + r"\\U_CABIN_PLATES.csv"
with open(output_csv, 'w') as f:
    f.write("NodeLabel,Ux,Uy,Uz,Magnitude\\n")
    for node_value in sorted(local_dis_value.values, key=lambda v: v.magnitude, reverse=True):
        ux, uy, uz = node_value.data
        mag = node_value.magnitude
        f.write("%d,%g,%g,%g,%g\\n" % (node_value.nodeLabel, ux, uy, uz, mag))

# 尝试打印图片
o1 = session.openOdb(
    name=odb_path)
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=31.0, 
    height=185.266662597656)
    
session.viewports['Viewport: 1'].maximize() # 视窗最大化

# 设置对象
session.viewports['Viewport: 1'].setValues(displayedObject=o1) 

# 隐藏网格
session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
    visibleEdges=FEATURE)

# 设置放缩
session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
    deformationScaling=UNIFORM, uniformScaleFactor=1)

# 设置背景   
session.graphicsOptions.setValues(backgroundStyle=SOLID, 
    backgroundColor='#FFFFFF')
    
# 设置显示内容
session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(
    legend=OFF, title=OFF, state=OFF, annotations=OFF, compass=OFF)
    
# 渲染构件钢板
session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(
    renderBeamProfiles=ON, renderShellThickness=ON)
    
# 切换为显示位移
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    CONTOURS_ON_DEF, ))
session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
    variableLabel='U', outputPosition=NODAL, refinement=(INVARIANT, 
    'Magnitude'), )

# 缩放改为1
session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
    deformationScaling=UNIFORM, uniformScaleFactor=1)
    
# 去除钢板打印
leaf = dgo.LeafFromPartInstance(partInstanceName=("CABIN_PLATES-1", ))
session.viewports['Viewport: 1'].odbDisplay.displayGroup.remove(leaf=leaf)
session.View(name='Iso', nearPlane=14193, farPlane=42578, width=5996.6, 
    height=4767.1, projection=PERSPECTIVE, cameraPosition=(22831, 17555, 
    18004), cameraUpVector=(-0.57735, 0.57735, -0.57735), cameraTarget=(6442.5, 
    1167.1, 1615.5), viewOffsetX=0, viewOffsetY=0, autoFit=ON)
session.printOptions.setValues(reduceColors=False)
session.printToFile(fileName='frame_deflection', format=PNG, canvasObjects=(
    session.viewports['Viewport: 1'], ))

# 关闭 ODB
odb.close()
"""
    return s

# 获取单元应力值
def get_result_s(params):
    s = f"""
# -*- coding: utf-8 -*-
from odbAccess import openOdb
from textRepr import *
import os

# 打开 ODB
odb_path = "{params["output"]["dir"]}" + r"\\Job-Mises.odb"
odb = openOdb(odb_path)

# 获取指定步的最后一帧和应力场
step = odb.steps["Step-2"]
frame = step.frames[-1]
field = frame.fieldOutputs["S"]

def export_element_set_stress_csv(instance_name, element_set_name, output_csv_path):

    # 获取元素集
    elem_set = odb.rootAssembly.instances[instance_name].elementSets[element_set_name]
    # 一次性获取该集合所有单元的应力值
    subset = field.getSubset(region=elem_set)
    # 建立元素号到最大（或首个）Mises 的映射
    stress_map = {{}}  # elementLabel -> float
    # 这里示例取最大值；若只需第一个积分点，可先判断 elabel 不在 map 时直接赋值
    for val in subset.values:
        elabel = val.elementLabel
        m = val.mises
        # 取最大
        if elabel not in stress_map or m > stress_map[elabel]:
            stress_map[elabel] = m

    # 建立元素号到连通性的映射
    connectivity_map = {{}}
    for element in elem_set.elements:
        # element.label 是元素号，element.connectivity 是节点号列表
        connectivity_map[element.label] = element.connectivity

    # 写 CSV
    # CSV 列：ElementLabel, Connectivity, Mises
    # Connectivity 字段可将节点号列表 join 为字符串，比如空格分隔
    # 注意如果想更标准 CSV，可在 Connectivity 外加引号，这里简单处理：
    # "节点号1 节点号2 节点号3 ..." 作为一个字段
    # Python 2.7 下用 % 格式化
    # 确保输出目录存在
    out_dir = os.path.dirname(output_csv_path)
    if out_dir and not os.path.exists(out_dir):
        try:
            os.makedirs(out_dir)
        except:
            pass  # 简单处理，不做过多错误检查

    with open(output_csv_path, 'w') as f:
        f.write("ElementLabel,Connectivity,Mises\\n")
        # 按 Mises 降序排列后写入
        for elabel, mises in sorted(stress_map.iteritems(), key=lambda x: x[1], reverse=True):
            conn = connectivity_map.get(elabel, ())
            # 将节点号列表转换为字符串
            conn_str = " ".join(map(str, conn))
            # 如果字符串中含逗号，CSV 可能需要引号包裹；这里假设节点号用空格连接，无逗号
            line = "%d,%s,%g\\n" % (elabel, conn_str, mises)
            f.write(line)

# 调用示例：根据自己需求修改输出路径
output_plate_csv = "{params["output"]["dir"]}" + r"\\S_CABIN_PLATES.csv"
export_element_set_stress_csv("CABIN_PLATES-1", "ELEMENT_SET_CABIN_PLATES", output_plate_csv)

output_frame_csv = "{params["output"]["dir"]}" + r"\\S_CABIN_FRAME.csv"
export_element_set_stress_csv("CABIN_FRAME-1", "ELEMENT_SET_CABIN_FRAME", output_frame_csv)

# 尝试打印图片
o1 = session.openOdb(
    name=odb_path)
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=31.0, 
    height=185.266662597656)
    
session.viewports['Viewport: 1'].maximize() # 视窗最大化

# 设置对象
session.viewports['Viewport: 1'].setValues(displayedObject=o1) 

# 隐藏网格
session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
    visibleEdges=FEATURE)

# 设置放缩
session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
    deformationScaling=UNIFORM, uniformScaleFactor=1)

# 设置背景   
session.graphicsOptions.setValues(backgroundStyle=SOLID, 
    backgroundColor='#FFFFFF')
    
# 设置显示内容
session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(
    legend=OFF, title=OFF, state=OFF, annotations=OFF, compass=OFF)
    
# 渲染构件钢板
session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(
    renderBeamProfiles=ON, renderShellThickness=ON)

# 构件跟钢板使用两种颜色
session.viewports['Viewport: 1'].enableMultipleColors()
session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')
cmap=session.viewports['Viewport: 1'].colorMappings['Part instance']
session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
session.viewports['Viewport: 1'].disableMultipleColors()

# 总体视角未变形视图保存
session.View(name='Iso', nearPlane=14193, farPlane=42578, width=5996.6, 
    height=4767.1, projection=PERSPECTIVE, cameraPosition=(22831, 17555, 
    18004), cameraUpVector=(-0.57735, 0.57735, -0.57735), cameraTarget=(6442.5, 
    1167.1, 1615.5), viewOffsetX=0, viewOffsetY=0, autoFit=OFF)
    
# 打印
session.printOptions.setValues(reduceColors=False)
session.pngOptions.setValues(imageSize=(1080, 839)) # 图片大小
session.printToFile(fileName='origin_cabin', format=PNG, canvasObjects=(
    session.viewports['Viewport: 1'], ))
    
# 变形后的应力
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    CONTOURS_ON_DEF, ))

# 缩放改为1
session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(
    deformationScaling=UNIFORM, uniformScaleFactor=1)
session.View(name='Iso', nearPlane=14193, farPlane=42578, width=5996.6, 
    height=4767.1, projection=PERSPECTIVE, cameraPosition=(22831, 17555, 
    18004), cameraUpVector=(-0.57735, 0.57735, -0.57735), cameraTarget=(6442.5, 
    1167.1, 1615.5), viewOffsetX=0, viewOffsetY=0, autoFit=ON)
session.printOptions.setValues(reduceColors=False)
session.printToFile(fileName='all_mises', format=PNG, canvasObjects=(
    session.viewports['Viewport: 1'], ))
    
# 去除钢板再打印一次
leaf = dgo.LeafFromPartInstance(partInstanceName=("CABIN_PLATES-1", ))
session.viewports['Viewport: 1'].odbDisplay.displayGroup.remove(leaf=leaf)
session.View(name='Iso', nearPlane=14193, farPlane=42578, width=5996.6, 
    height=4767.1, projection=PERSPECTIVE, cameraPosition=(22831, 17555, 
    18004), cameraUpVector=(-0.57735, 0.57735, -0.57735), cameraTarget=(6442.5, 
    1167.1, 1615.5), viewOffsetX=0, viewOffsetY=0, autoFit=ON)
session.printOptions.setValues(reduceColors=False)
session.printToFile(fileName='frame_mises', format=PNG, canvasObjects=(
    session.viewports['Viewport: 1'], ))
    
# 关闭 ODB
odb.close()

"""
    return s

# 判断一个单元（由 coord1, coord2 端点坐标给出）是否属于某零件（part）
def element_belongs_to_part(coord1: np.ndarray, coord2: np.ndarray,
                            part_center: np.ndarray, part_dir: np.ndarray,
                            part_length: float,
                            tol_factor: float = 0.6) -> bool:
    """
    判断一个单元（由 coord1, coord2 端点坐标给出）是否属于某零件（part）。
    逻辑同前：通过单元中点到构件中心线的投影和垂直距离来判断，tol_factor 可调整。
    """
    vec_e = coord2 - coord1
    l_e = np.linalg.norm(vec_e)
    if l_e == 0:
        return False
    midpoint = (coord1 + coord2) / 2.0
    v_mid = midpoint - part_center
    t_mid = np.dot(v_mid, part_dir)
    half_part = part_length / 2.0
    # 允许单元长度一半的余量
    if t_mid < -half_part - l_e/2.0 - 1e-8 or t_mid > half_part + l_e/2.0 + 1e-8:
        return False
    orth = v_mid - t_mid * part_dir
    d = np.linalg.norm(orth)
    if d > tol_factor * (l_e/2.0):
        return False
    # 如需可加方向平行检查，这里省略
    return True

# 计算某单元在构件上的位置
def compute_locate_for_element(coord1: np.ndarray, coord2: np.ndarray,
                               part_center: np.ndarray, part_dir: np.ndarray,
                               part_length: float) -> str:
    """
    计算某单元在构件上的位置：通过中点在轴线上的投影 t_mid 判断是否在端部或中部。
    - 端部范围：距离端点不超过长度的 10%；
    - 若在正方向端部，返回 '"+axis"' 或 '-axis'，根据 part_dir 的方向符号判断；
      若在负方向端部，返回相反符号；
    - 否则返回 '"mid"'。
    返回值带双引号，如 "+y"、"-x"、"mid"。
    """
    midpoint = (coord1 + coord2) / 2.0
    v_mid = midpoint - part_center
    t_mid = np.dot(v_mid, part_dir)
    half_part = part_length / 2.0
    thresh = 0.1 * part_length  # 10% 长度范围
    # 先确定轴名称和 dir_unit 符号
    # part_dir 应为单位向量，这里取绝对值最大的分量对应轴
    abs_dir = np.abs(part_dir)
    axis_idx = int(np.argmax(abs_dir))  # 0->x,1->y,2->z
    axis_name = ['x','y','z'][axis_idx]
    dir_sign = '+' if part_dir[axis_idx] >= 0 else '-'
    # 判断位置
    if t_mid >= half_part - thresh:
        # 靠近正方向端部
        # 正方向端部：如果 part_dir 指向该轴正方向，则 "+axis"；如果 part_dir 指向负方向，则 "-axis"
        return f'"{dir_sign}{axis_name}"'
    elif t_mid <= -half_part + thresh:
        # 靠近负方向端部：符号与正方向端部相反
        opposite_sign = '-' if dir_sign == '+' else '+'
        return f'"{opposite_sign}{axis_name}"'
    else:
        return '"mid"'

# 处理最终的框架应力结果
def process_frame_parts_by_element_with_locate(parts_info: dict, params: dict):
    # 1. 读取节点和位移
    u_csv = os.path.join(params["output"]["dir"], "U_CABIN_FRAME_PROCESSED.csv")
    df_nodes = pd.read_csv(u_csv)
    for col in ['NodeLabel', 'X', 'Y', 'Z', 'Ux', 'Uy', 'Uz', 'Magnitude']:
        if col not in df_nodes.columns:
            raise ValueError(f"U_CSV 缺少列 {col}")
    try:
        df_nodes['NodeLabel'] = df_nodes['NodeLabel'].astype(int)
    except (ValueError, TypeError):
        pass
    node_coord_map = {}
    node_disp_map = {}
    for _, row in df_nodes.iterrows():
        nl = row['NodeLabel']
        node_coord_map[nl] = np.array([row['X'], row['Y'], row['Z']], dtype=float)
        node_disp_map[nl] = {'Ux': row['Ux'], 'Uy': row['Uy'], 'Uz': row['Uz'], 'Magnitude': row['Magnitude']}
    # 2. 读取单元应力表
    s_csv = os.path.join(params["output"]["dir"], "S_CABIN_FRAME.csv")
    df_elems = pd.read_csv(s_csv)
    for col in ['ElementLabel', 'Connectivity', 'Mises']:
        if col not in df_elems.columns:
            raise ValueError(f"S_CSV 缺少列 {col}")
    def parse_conn(s):
        parts = str(s).split()
        if len(parts) != 2:
            raise ValueError(f"Connectivity 格式异常: {s}")
        try:
            return int(parts[0]), int(parts[1])
        except (ValueError, TypeError):
            return parts[0], parts[1]
    conn = df_elems['Connectivity'].apply(parse_conn)
    df_elems['node1'] = conn.apply(lambda x: x[0])
    df_elems['node2'] = conn.apply(lambda x: x[1])
    try:
        df_elems['ElementLabel'] = df_elems['ElementLabel'].astype(int)
    except (ValueError, TypeError):
        pass
    df_elems['Mises'] = pd.to_numeric(df_elems['Mises'], errors='coerce')
    # 3. 预处理 parts_info：提取 center, dir_unit, length
    parts_processed = {}
    for pid, info in parts_info.items():
        if 'center_coord' not in info or 'dir' not in info or 'length' not in info:
            raise ValueError(f"parts_info 中 {pid} 缺少字段")
        c = info['center_coord']
        center = np.array([c['x'], c['y'], c['z']], dtype=float)
        d = info['dir']
        dir_arr = np.array([d.get('x',0), d.get('y',0), d.get('z',0)], dtype=float)
        norm = np.linalg.norm(dir_arr)
        if norm == 0:
            raise ValueError(f"part {pid} dir 向量为零")
        dir_unit = dir_arr / norm
        length = float(info['length'])
        parts_processed[pid] = {'center': center, 'dir': dir_unit, 'length': length}
    # 4. 建立 parts_elements_map：对每个单元判断归属
    parts_elements_map = {pid: [] for pid in parts_info.keys()}
    for _, row in df_elems.iterrows():
        e_label = row['ElementLabel']
        n1 = row['node1']; n2 = row['node2']
        if n1 not in node_coord_map or n2 not in node_coord_map:
            continue
        coord1 = node_coord_map[n1]; coord2 = node_coord_map[n2]
        assigned = False
        for pid, pinfo in parts_processed.items():
            if element_belongs_to_part(coord1, coord2,
                                      pinfo['center'], pinfo['dir'], pinfo['length'],
                                      tol_factor=0.6):
                parts_elements_map[pid].append(e_label)
                assigned = True
                break
        if not assigned:
            print(f"警告: 元素 {e_label} 未匹配到任何 part")
    # 5. 收集每个 part 的节点集合（由其元素端点继承）
    parts_nodes_map = {}
    for pid, elems in parts_elements_map.items():
        node_set = set()
        for el in elems:
            dfrow = df_elems[df_elems['ElementLabel'] == el]
            if dfrow.empty: continue
            r = dfrow.iloc[0]
            node_set.add(r['node1'])
            node_set.add(r['node2'])
        parts_nodes_map[pid] = node_set
    # 6. 汇总每个 part：最大应力元素、最大位移节点，以及定位 locate；并添加 type 字段
    results = []
    for pid, elems in parts_elements_map.items():
        if not elems:
            print(f"提示: part {pid} 无任何元素，跳过")
            continue
        df_part = df_elems[df_elems['ElementLabel'].isin(elems)].dropna(subset=['Mises'])
        if df_part.empty:
            print(f"提示: part {pid} 元素 Mises 全空，跳过")
            continue
        # 6.1. 最大应力单元
        idx_max = df_part['Mises'].idxmax()
        row_max = df_part.loc[idx_max]
        max_mises = float(row_max['Mises'])
        elem_label = row_max['ElementLabel']
        node1 = row_max['node1']; node2 = row_max['node2']
        # 计算该单元定位 locate
        coord1 = node_coord_map.get(node1)
        coord2 = node_coord_map.get(node2)
        p_center = parts_processed[pid]['center']
        p_dir = parts_processed[pid]['dir']
        p_len = parts_processed[pid]['length']
        if coord1 is None or coord2 is None or p_len == 0:
            locate = '"mid"'
        else:
            locate = compute_locate_for_element(coord1, coord2, p_center, p_dir, p_len)
        # 6.2. 最大位移节点
        max_disp = None; max_disp_node = None
        for nl in parts_nodes_map[pid]:
            disp = node_disp_map.get(nl)
            if disp is None: continue
            mag = disp['Magnitude']
            if pd.isna(mag): continue
            if (max_disp is None) or (abs(mag) > abs(max_disp)):
                max_disp = mag; max_disp_node = nl
        if max_disp_node is None:
            print(f"提示: part {pid} 无有效节点位移，跳过")
            continue
        d0 = node_disp_map[max_disp_node]
        comp = {'x': d0['Ux'], 'y': d0['Uy'], 'z': d0['Uz']}
        axis = max(comp.keys(), key=lambda k: abs(comp[k]))
        val = comp[axis]
        sign = '+' if val >= 0 else '-'
        direction = f'"{sign}{axis}"'
        if p_len == 0:
            print(f"警告: part {pid} 长度为0，跳过")
            continue
        max_deflection = abs(val) / p_len

        # 获取 type 值，并用双引号包裹；若 parts_info 中无 'type'，可选用空字符串或其他默认
        part_type = parts_info.get(pid, {}).get('type', '')
        type_str = f"\"{part_type}\""

        # 汇总
        results.append({
            'part_id': pid,
            'type': type_str,
            'max_mises': max_mises,
            'element_label': elem_label,
            'locate': locate,
            'node1': node1,
            'node2': node2,
            'max_deflection': max_deflection,
            'node': max_disp_node,
            'direction': direction
        })
    if not results:
        print("未生成任何结果")
        return
    # 7. 结果 DataFrame，与之前相比多了 type 列，并把它放到 part_id 之后
    df_res = pd.DataFrame(results)
    # 调整列顺序：确保 type 列紧跟在 part_id 之后
    cols = list(df_res.columns)
    if 'type' in cols:
        cols.remove('type')
        # 找到 part_id 索引
        try:
            idx = cols.index('part_id')
        except ValueError:
            idx = -1
        # 插入到 part_id 之后，如果没找到，则放在最前或末尾
        if idx >= 0:
            cols.insert(idx+1, 'type')
        else:
            cols.insert(0, 'type')
    df_res = df_res[cols]
    # 排序
    df_res = df_res.sort_values(by='max_mises', ascending=False)
    out_csv = os.path.join(params["output"]["dir"], "FRAME_SUM.csv")
    df_res.to_csv(out_csv, index=False)