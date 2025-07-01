# 用于生成边界条件、创建分析步等

def gen_bc(params):
    s = f"""
a = mdb.models['Model-1'].rootAssembly
v1 = a.instances['cabin_frame-1'].vertices
verts1 = v1.findAt((({params["cabin"]["length"]["axis_dis"]}, 0.0, 0.0), ), (({params["cabin"]["length"]["axis_dis"]}, 0.0, {params["cabin"]["width"]["axis_dis"]}), ), ((0.0, 
    0.0, {params["cabin"]["width"]["axis_dis"]}), ), ((0.0, 0.0, 0.0), ))
region = a.Set(vertices=verts1, name='set_bc')
mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Initial', 
    region=region, u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET, 
    amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
"""
    return s

def gen_step():
    s = f"""
mdb.models['Model-1'].StaticStep(name='Step-2', previous='Initial', 
    maxNumInc=10000, initialInc=0.001, maxInc=0.5)
"""
    return s

def gen_mesh(mesh_size):
    s = f"""
# 注意这个地方没有划分合并后的钢板网格，是在合并的部分划分的
# 舱体网格
p = mdb.models['Model-1'].parts['cabin_frame']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()

# 顶板网格
p = mdb.models['Model-1'].parts['plate_top_cabin']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
p = mdb.models['Model-1'].parts['plate_top_equip']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
p = mdb.models['Model-1'].parts['plate_top_door']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()

# 舱体右侧网格
p = mdb.models['Model-1'].parts['plate_r_whole']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
p = mdb.models['Model-1'].parts['plate_r_wl']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
p = mdb.models['Model-1'].parts['plate_r_wr']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()

# 舱体左侧网格
p = mdb.models['Model-1'].parts['plate_l_whole']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
p = mdb.models['Model-1'].parts['plate_l_wl']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
p = mdb.models['Model-1'].parts['plate_l_wr']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()

# 舱体对侧网格
p = mdb.models['Model-1'].parts['plate_off_whole']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
p = mdb.models['Model-1'].parts['plate_off_w']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()

# 设备间网格
p = mdb.models['Model-1'].parts['plate_equip_w']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
p = mdb.models['Model-1'].parts['plate_equip_l']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()

# 舱体门附近网格
p = mdb.models['Model-1'].parts['plate_door']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
p = mdb.models['Model-1'].parts['plate_door_up']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
p = mdb.models['Model-1'].parts['plate_door_down']
p.seedPart(size=10.0, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
p = mdb.models['Model-1'].parts['plate_door_left']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()

# 窗户位置的网格
p = mdb.models['Model-1'].parts['plate_window_up']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
p = mdb.models['Model-1'].parts['plate_window_down']
p.seedPart(size=10.0, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
p = mdb.models['Model-1'].parts['plate_window']
p.seedPart(size={mesh_size}, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
"""
    return s

def gen_job(cpu_num: int):
    s = f"""
# 创建作业
mdb.Job(name='Job-Mises', model='Model-1', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus={cpu_num}, 
    numDomains={cpu_num}, numGPUs=0)
# 尝试更改场输出请求
mdb.models['Model-1'].FieldOutputRequest(name='F-Output-1', 
    createStepName='Step-2', variables=('S', 'U'), frequency=LAST_INCREMENT, region=MODEL, exteriorOnly=OFF)
"""
    return s

# 为部件创建节点集合，方便后处理
def gen_node_element_set():
    s = f"""
p = mdb.models['Model-1'].parts['cabin_frame']
n = p.nodes
n_num = len(n)
nodes = n[0:n_num]
p.Set(nodes=nodes, name='node_set_cabin_frame')
e = p.elements
e_num = len(e)
elements = e[0:e_num]
p.Set(elements=elements, name='element_set_cabin_frame')

p = mdb.models['Model-1'].parts['cabin_plates']
n = p.nodes
n_num = len(n)
nodes = n[0:n_num]
p.Set(nodes=nodes, name='node_set_cabin_plates')
e = p.elements
e_num = len(e)
elements = e[0:e_num]
p.Set(elements=elements, name='element_set_cabin_plates')
"""
    return s