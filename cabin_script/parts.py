## 所有旋转的部件都是以Y轴正方向旋转-90°

# 材料
def gen_material():
    s = f"""
# 创建钢材材料
mdb.models['Model-1'].Material(name='Q355C')
mdb.models['Model-1'].materials['Q355C'].Density(table=((7.85e-09, ), ))
mdb.models['Model-1'].materials['Q355C'].Elastic(table=((206000.0, 0.28), ))
# 考虑使用双折线模型，数据来源于
# 赵鑫,李洁,桑秀兴,等.Q355C钢宽间隙焊接试验研究[J].焊接技术,2021,50(08):48-52.
mdb.models['Model-1'].materials['Q355C'].Plastic(table=((422.0, 0.0), 
    (558.0, 0.005796)))
"""
    return s

# 剖面
def gen_profile(params):
    s = f"""
# 生成框架梁剖面
mdb.models['Model-1'].BoxProfile(name='{params["parts"]["main_beam_column"]["type"]}', b={params["parts"]["main_beam_column"]["a"]}, a={params["parts"]["main_beam_column"]["b"]},
    uniformThickness=ON, t1={params["parts"]["main_beam_column"]["c"]})
# 生成环向主梁剖面
mdb.models['Model-1'].IProfile(name='{params["parts"]["cir_main_beam"]["type"]}', l={params["parts"]["cir_main_beam"]["a"]}, h={params["parts"]["cir_main_beam"]["b"]}, b1={params["parts"]["cir_main_beam"]["c"]}, 
    b2={params["parts"]["cir_main_beam"]["d"]}, t1={params["parts"]["cir_main_beam"]["e"]}, t2={params["parts"]["cir_main_beam"]["f"]}, t3={params["parts"]["cir_main_beam"]["g"]})
# 生成环向次梁剖面（加入偏移，生成的是朝Z方向的以及朝向-X方向的）
mdb.models['Model-1'].IProfile(name='{params["parts"]["cir_secd_beam"]["type"]}', l={params["parts"]["cir_secd_beam"]["a"]-params["parts"]["cir_secd_beam"]["move"]}, h={params["parts"]["cir_secd_beam"]["b"]}, b1={params["parts"]["cir_secd_beam"]["c"]}, 
    b2={params["parts"]["cir_secd_beam"]["d"]}, t1={params["parts"]["cir_secd_beam"]["e"]}, t2={params["parts"]["cir_secd_beam"]["f"]}, t3={params["parts"]["cir_secd_beam"]["g"]})
# 生成环向支撑梁剖面（加入偏移，生成的是朝Z方向的以及朝向-X方向的）
mdb.models['Model-1'].ArbitraryProfile(name='{params["parts"]["cir_sup_beam"]["type"]}', table=(({params["parts"]["cir_sup_beam"]["a"]}, {params["parts"]["cir_sup_beam"]["b"]+params["parts"]["cir_sup_beam"]["move"]}), (
    {params["parts"]["cir_sup_beam"]["c"]}, {params["parts"]["cir_sup_beam"]["d"]+params["parts"]["cir_sup_beam"]["move"]}, {params["parts"]["cir_sup_beam"]["i"]}), ({params["parts"]["cir_sup_beam"]["e"]}, {params["parts"]["cir_sup_beam"]["f"]+params["parts"]["cir_sup_beam"]["move"]}, {params["parts"]["cir_sup_beam"]["i"]}), ({params["parts"]["cir_sup_beam"]["g"]}, {params["parts"]["cir_sup_beam"]["h"]+params["parts"]["cir_sup_beam"]["move"]}, {params["parts"]["cir_sup_beam"]["i"]})))
# 生成顶部环向次梁剖面
mdb.models['Model-1'].IProfile(name='{params["parts"]["cir_secd_beam"]["type"]}_top', l={params["parts"]["cir_secd_beam"]["a"]-params["parts"]["cir_secd_beam"]["move"]}, h={params["parts"]["cir_secd_beam"]["b"]}, b1={params["parts"]["cir_secd_beam"]["c"]}, 
    b2={params["parts"]["cir_secd_beam"]["d"]}, t1={params["parts"]["cir_secd_beam"]["e"]}, t2={params["parts"]["cir_secd_beam"]["f"]}, t3={params["parts"]["cir_secd_beam"]["g"]})
# 生成底部环向次梁剖面
mdb.models['Model-1'].IProfile(name='{params["parts"]["cir_secd_beam"]["type"]}_btm', l={params["parts"]["cir_secd_beam"]["a"]+params["parts"]["cir_secd_beam"]["move"]}, h={params["parts"]["cir_secd_beam"]["b"]}, b1={params["parts"]["cir_secd_beam"]["c"]}, 
     b2={params["parts"]["cir_secd_beam"]["d"]}, t1={params["parts"]["cir_secd_beam"]["e"]}, t2={params["parts"]["cir_secd_beam"]["f"]}, t3={params["parts"]["cir_secd_beam"]["g"]})
# 生成底部环向支撑梁剖面
mdb.models['Model-1'].ArbitraryProfile(name='{params["parts"]["cir_sup_beam"]["type"]}_btm', table=(({params["parts"]["cir_sup_beam"]["a"]}, {params["parts"]["cir_sup_beam"]["b"]-params["parts"]["cir_sup_beam"]["move"]}), (
    {params["parts"]["cir_sup_beam"]["c"]}, {params["parts"]["cir_sup_beam"]["d"]-params["parts"]["cir_sup_beam"]["move"]}, {params["parts"]["cir_sup_beam"]["i"]}), ({params["parts"]["cir_sup_beam"]["e"]}, {params["parts"]["cir_sup_beam"]["f"]-params["parts"]["cir_sup_beam"]["move"]}, {params["parts"]["cir_sup_beam"]["i"]}), ({params["parts"]["cir_sup_beam"]["g"]}, {params["parts"]["cir_sup_beam"]["h"]-params["parts"]["cir_sup_beam"]["move"]}, {params["parts"]["cir_sup_beam"]["i"]})))
# 生成顶部环向支撑梁剖面
mdb.models['Model-1'].ArbitraryProfile(name='{params["parts"]["cir_sup_beam"]["type"]}_top', table=(({params["parts"]["cir_sup_beam"]["a"]}, {params["parts"]["cir_sup_beam"]["b"]+params["parts"]["cir_sup_beam"]["move"]}), (
    {params["parts"]["cir_sup_beam"]["c"]}, {params["parts"]["cir_sup_beam"]["d"]+params["parts"]["cir_sup_beam"]["move"]}, {params["parts"]["cir_sup_beam"]["i"]}), ({params["parts"]["cir_sup_beam"]["e"]}, {params["parts"]["cir_sup_beam"]["f"]+params["parts"]["cir_sup_beam"]["move"]}, {params["parts"]["cir_sup_beam"]["i"]}), ({params["parts"]["cir_sup_beam"]["g"]}, {params["parts"]["cir_sup_beam"]["h"]+params["parts"]["cir_sup_beam"]["move"]}, {params["parts"]["cir_sup_beam"]["i"]})))
"""
    return s

# 截面
def gen_section(params):
    s = f"""
# 框架梁柱截面
mdb.models['Model-1'].BeamSection(name='{params["parts"]["main_beam_column"]["type"]}', 
    integration=DURING_ANALYSIS, poissonRatio=0.0, profile='{params["parts"]["main_beam_column"]["type"]}', 
    material='Q355C', temperatureVar=LINEAR, consistentMassMatrix=False)
# 环向主梁截面
mdb.models['Model-1'].BeamSection(name='{params["parts"]["cir_main_beam"]["type"]}', 
    integration=DURING_ANALYSIS, poissonRatio=0.0, profile='{params["parts"]["cir_main_beam"]["type"]}', 
    material='Q355C', temperatureVar=LINEAR, consistentMassMatrix=False)
# 环向次梁截面
mdb.models['Model-1'].BeamSection(name='{params["parts"]["cir_secd_beam"]["type"]}', 
    integration=DURING_ANALYSIS, poissonRatio=0.0, profile='{params["parts"]["cir_secd_beam"]["type"]}', 
    material='Q355C', temperatureVar=LINEAR, consistentMassMatrix=False)
# 环向支撑梁截面
mdb.models['Model-1'].BeamSection(name='{params["parts"]["cir_sup_beam"]["type"]}', 
    integration=DURING_ANALYSIS, poissonRatio=0.0, profile='{params["parts"]["cir_sup_beam"]["type"]}', 
    material='Q355C', temperatureVar=LINEAR, consistentMassMatrix=False)
# 顶部环向次梁截面
mdb.models['Model-1'].BeamSection(name='{params["parts"]["cir_secd_beam"]["type"]}_top', 
    integration=DURING_ANALYSIS, poissonRatio=0.0, profile='{params["parts"]["cir_secd_beam"]["type"]}_top', 
    material='Q355C', temperatureVar=LINEAR, consistentMassMatrix=False)
# 底部环向次梁截面
mdb.models['Model-1'].BeamSection(name='{params["parts"]["cir_secd_beam"]["type"]}_btm', 
    integration=DURING_ANALYSIS, poissonRatio=0.0, profile='{params["parts"]["cir_secd_beam"]["type"]}_btm', 
    material='Q355C', temperatureVar=LINEAR, consistentMassMatrix=False)
# 顶部环向支撑梁截面
mdb.models['Model-1'].BeamSection(name='{params["parts"]["cir_sup_beam"]["type"]}_top', 
    integration=DURING_ANALYSIS, poissonRatio=0.0, profile='{params["parts"]["cir_sup_beam"]["type"]}_top', 
    material='Q355C', temperatureVar=LINEAR, consistentMassMatrix=False)
# 底部环向支撑梁截面
mdb.models['Model-1'].BeamSection(name='{params["parts"]["cir_sup_beam"]["type"]}_btm', 
    integration=DURING_ANALYSIS, poissonRatio=0.0, profile='{params["parts"]["cir_sup_beam"]["type"]}_btm', 
    material='Q355C', temperatureVar=LINEAR, consistentMassMatrix=False)
# 蒙皮钢板截面
mdb.models['Model-1'].HomogeneousShellSection(name='plate', preIntegrate=OFF, 
    material='Q355C', thicknessType=UNIFORM, thickness=5.0, thicknessField='', 
    nodalThicknessField='', idealization=NO_IDEALIZATION, 
    poissonDefinition=DEFAULT, thicknessModulus=None, temperature=GRADIENT, 
    useDensity=OFF, integrationRule=SIMPSON, numIntPts=5)
"""
    return s

# 构件
def gen_parts(params):
    main_frame_s = f"""
# 创建框架梁
# 横梁
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["cabin"]["width"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='frame_beam_width', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['frame_beam_width']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['frame_beam_width']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['frame_beam_width']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['frame_beam_width']
p.SectionAssignment(region=region, sectionName='{params["parts"]["main_beam_column"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 纵梁
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["cabin"]["length"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='frame_beam_length', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['frame_beam_length']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['frame_beam_length']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['frame_beam_length']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['frame_beam_length']
p.SectionAssignment(region=region, sectionName='{params["parts"]["main_beam_column"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
    
# 设备间短横梁
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["equip"]["width"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g.findAt(({params["equip"]["width"]["axis_dis"] / 2.0}, 0.0)), addUndoState=False)
p = mdb.models['Model-1'].Part(name='frame_beam_short', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['frame_beam_short']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['frame_beam_short']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['frame_beam_short']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['frame_beam_short']
p.SectionAssignment(region=region, sectionName='{params["parts"]["main_beam_column"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 柱
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=(0.0, {params["cabin"]["height"]["axis_dis"]}))
s1.VerticalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='frame_column', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['frame_column']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['frame_column']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['frame_column']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['frame_column']
p.SectionAssignment(region=region, sectionName='{params["parts"]["main_beam_column"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
"""
    door_beam_s = f"""
# 门上下环向次梁
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Line(point1=(0.0, 0.0), point2=({params["door"]["width"]["axis_dis"]}, 0.0))
s.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='door_beam', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['door_beam']
p.BaseWire(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['door_beam']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['door_beam']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['door_beam']
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_secd_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 门左侧环向次梁
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]-params["door"]["width"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='door_left_beam', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['door_left_beam']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['door_left_beam']
del mdb.models['Model-1'].sketches['__profile__']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['door_left_beam']
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_secd_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
    
# 门上方支撑梁
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Line(point1=(0.0, 0.0), point2=({params["door"]["width"]["axis_dis"]}, 0.0))
s.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_d', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_d']
p.BaseWire(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_d']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['sup_beam_d']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['sup_beam_d']
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
"""
    window_beam_s = f"""
# 侧面窗户次梁

s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["cabin"]["length"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='window_beam_side', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['window_beam_side']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['window_beam_side']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['window_beam_side']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['window_beam_side']
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_secd_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
# 对侧窗户次梁

s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["cabin"]["width"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='window_beam_offside', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['window_beam_offside']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['window_beam_offside']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['window_beam_offside']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['window_beam_offside']
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_secd_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
"""
    secd_beam_s = f"""
# 创建环向次梁（舱体顶面与底面）
# 首先创建顶面
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Line(point1=(0.0, 0.0), point2=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, 0.0))
s.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='cir_secd_beam_top', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['cir_secd_beam_top']
p.BaseWire(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['cir_secd_beam_top']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['cir_secd_beam_top']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['cir_secd_beam_top']
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_secd_beam"]["type"]}_top', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
# 其次创建底面
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Line(point1=(0.0, 0.0), point2=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, 0.0))
s.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='cir_secd_beam_btm', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['cir_secd_beam_btm']
p.BaseWire(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['cir_secd_beam_btm']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['cir_secd_beam_btm']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['cir_secd_beam_btm']
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_secd_beam"]["type"]}_btm', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
"""
    cir_main_s = f"""
# 创建环向主梁（柱子）
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Line(point1=(0.0, 0.0), point2=(0.0, {params["cabin"]["height"]["axis_dis"]}))
s.VerticalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='cir_column', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['cir_column']
p.BaseWire(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['cir_column']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['cir_column']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_main_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
# 创建环向主梁（舱体上下两个面）
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["cabin"]["width"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='cir_beam', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['cir_beam']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['cir_beam']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['cir_beam']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_main_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
"""
    window_plate_s = f"""
# 创建窗户间隙之间的钢板    
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["window"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_window_gap', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_window_gap']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_window_gap']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_window_gap']
f = p.faces
faces = f.findAt((({params["window"]["width"]["axis_dis"]/2}, {params["cabin"]["height"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_window_gap']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
# 创建窗户位置的钢板
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["window"]["width"]["axis_dis"]}, {params["window"]["height"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_window', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_window']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_window']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_window']
f = p.faces
faces = f.findAt((({params["window"]["width"]["axis_dis"]/2}, {params["window"]["height"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_window']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
# 其次是窗户下侧
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["window"]["width"]["axis_dis"]}, {params["window"]["ground_clear"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_window_down', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_window_down']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_window_down']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_window_down']
f = p.faces
faces = f.findAt((({params["window"]["width"]["axis_dis"]/2}, {params["window"]["ground_clear"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_window_down']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
# 其次是窗户上侧
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["window"]["width"]["axis_dis"]}, {params["window"]["top_clear"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_window_up', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_window_up']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_window_up']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_window_up']
f = p.faces
faces = f.findAt((({params["window"]["width"]["axis_dis"]/2}, {params["window"]["top_clear"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_window_up']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
"""
    equip_beam_s = f"""
# 创建设备间环向次梁
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Line(point1=(0.0, 0.0), point2=({params["equip"]["length"]["axis_dis"]}, 0.0))
s.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='equip_beam_length', 
    dimensionality=THREE_D, type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['equip_beam_length']
p.BaseWire(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['equip_beam_length']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['equip_beam_length']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['equip_beam_length']
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_secd_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
    
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Line(point1=(0.0, 0.0), point2=({params["equip"]["width"]["axis_dis"]}, 0.0))
s.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='equip_beam_width', 
    dimensionality=THREE_D, type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['equip_beam_width']
p.BaseWire(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['equip_beam_width']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['equip_beam_width']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['equip_beam_width']
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_secd_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 接下来生成设备间顶部的环向次梁
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Line(point1=(0.0, 0.0), point2=({params["equip"]["width"]["axis_dis"]}, 0.0))
s.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='equip_beam_w_top', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['equip_beam_w_top']
p.BaseWire(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['equip_beam_w_top']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['equip_beam_w_top']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['equip_beam_w_top']
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_secd_beam"]["type"]}_top', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 还有设备间底部的环向次梁
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Line(point1=(0.0, 0.0), point2=({params["equip"]["width"]["axis_dis"]}, 0.0))
s.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='equip_beam_w_btm', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['equip_beam_w_btm']
p.BaseWire(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['equip_beam_w_btm']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['equip_beam_w_btm']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['equip_beam_w_btm']
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_secd_beam"]["type"]}_btm', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
"""
    sup_beam_s = f"""
# 窗户宽度范围内单位长度的环向支撑梁
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["window"]["width"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_wg', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_wg']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_wg']
del mdb.models['Model-1'].sketches['__profile__']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
# 设备间长度方向的环向支撑梁
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["equip"]["length"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_el', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_el']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_el']
del mdb.models['Model-1'].sketches['__profile__']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 设备间宽度方向的环向支撑梁
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["equip"]["width"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_ew', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_ew']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_ew']
del mdb.models['Model-1'].sketches['__profile__']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 门左侧的环向支撑梁
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]-params["door"]["width"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_dl', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_dl']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_dl']
del mdb.models['Model-1'].sketches['__profile__']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 舱体左侧的环向支撑梁（长度为舱体长度减去设备间宽度）
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_left', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_left']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_left']
del mdb.models['Model-1'].sketches['__profile__']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 舱体左侧窗户左侧的环向支撑梁（远离舱门一侧）
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({(min(params["window"]["left"]["locate"])-1)*params["window"]["width"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_left_wl', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_left_wl']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_left_wl']
del mdb.models['Model-1'].sketches['__profile__']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 舱体左侧窗户右侧的环向支撑梁（靠近舱门一侧）
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]-max(params["window"]["left"]["locate"])*params["window"]["width"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_left_wr', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_left_wr']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_left_wr']
del mdb.models['Model-1'].sketches['__profile__']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 舱体对侧的环向支撑梁（长度与舱体宽度相同）
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["cabin"]["width"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_offside', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_offside']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_offside']
del mdb.models['Model-1'].sketches['__profile__']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 舱体对侧窗户一侧的环向支撑梁
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({(params["cabin"]["width"]["axis_dis"]-params["window"]["offside"]["num"]*params["window"]["width"]["axis_dis"])/2}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_offside_w', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_offside_w']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_offside_w']
del mdb.models['Model-1'].sketches['__profile__']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 舱体上下两个面上的环向支撑梁
# 首先创建舱体顶部
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_top', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_top']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_top']
del mdb.models['Model-1'].sketches['__profile__']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}_top', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
# 其次创建舱体底部
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_btm', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_btm']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_btm']
del mdb.models['Model-1'].sketches['__profile__']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}_btm', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 舱体右侧的环向支撑梁（长度与舱体长度相同）
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["cabin"]["length"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_right', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_right']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_right']
del mdb.models['Model-1'].sketches['__profile__']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 舱体右侧窗户左侧的环向支撑梁
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({params["cabin"]["length"]["axis_dis"]-max(params["window"]["right"]["locate"])*params["window"]["width"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_right_wl', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_right_wl']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_right_wl']
del mdb.models['Model-1'].sketches['__profile__']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 舱体右侧窗户右侧的环向支撑梁
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(0.0, 0.0), point2=({(min(params["window"]["right"]["locate"])-1)*params["window"]["width"]["axis_dis"]}, 0.0))
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_right_wr', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_right_wr']
p.BaseWire(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_right_wr']
del mdb.models['Model-1'].sketches['__profile__']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 门上方那一小块区域的环向支撑梁
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Line(point1=(0.0, 0.0), point2=({params["equip"]["width"]["axis_dis"]}, 0.0))
s.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_ew_top', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_ew_top']
p.BaseWire(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_ew_top']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['sup_beam_ew_top']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['sup_beam_ew_top']
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}_top', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
    
# 随后是门下方
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Line(point1=(0.0, 0.0), point2=({params["equip"]["width"]["axis_dis"]}, 0.0))
s.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='sup_beam_ew_btm', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['sup_beam_ew_btm']
p.BaseWire(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['sup_beam_ew_btm']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['sup_beam_ew_btm']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['sup_beam_ew_btm']
p.SectionAssignment(region=region, sectionName='{params["parts"]["cir_sup_beam"]["type"]}_btm', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
"""
    equip_plate_s = f"""
# 设备间两侧蒙皮钢板
# 长度方向的
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["equip"]["length"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_equip_l', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_equip_l']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_equip_l']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_equip_l']
f = p.faces
faces = f.findAt((({params["equip"]["length"]["axis_dis"]/2}, {params["cabin"]["height"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_equip_l']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
# 宽度方向的
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_equip_w', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_equip_w']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_equip_w']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_equip_w']
f = p.faces
faces = f.findAt((({params["equip"]["width"]["axis_dis"]/2}, {params["cabin"]["height"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_equip_w']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
"""
    left_plate_s = f"""
# 舱体左侧蒙皮钢板
# 首先创建一个通长但不含设备间的
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_l_whole', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_l_whole']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_l_whole']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_l_whole']
f = p.faces
faces = f.findAt((({(params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"])/2}, {params["cabin"]["height"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_l_whole']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
# 随后创建左侧窗户的左侧
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["window"]["width"]["axis_dis"]*(min(params["window"]["left"]["locate"])-1)}, {params["cabin"]["height"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_l_wl', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_l_wl']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_l_wl']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_l_wl']
f = p.faces
faces = f.findAt((({(params["window"]["width"]["axis_dis"]*(min(params["window"]["left"]["locate"])-1))/2}, {params["cabin"]["height"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_l_wl']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
# 随后是左侧窗户的右侧
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["cabin"]["length"]["axis_dis"]-params["window"]["width"]["axis_dis"]*max(params["window"]["left"]["locate"])-params["equip"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_l_wr', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_l_wr']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_l_wr']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_l_wr']
f = p.faces
faces = f.findAt((({(params["cabin"]["length"]["axis_dis"]-params["window"]["width"]["axis_dis"]*max(params["window"]["left"]["locate"])-params["equip"]["width"]["axis_dis"])/2}, {params["cabin"]["height"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_l_wr']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
"""
    right_plate_s = f"""
# 舱体右侧蒙皮钢板
# 首先创建一个通长的
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["cabin"]["length"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_r_whole', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_r_whole']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_r_whole']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_r_whole']
f = p.faces
faces = f.findAt((({params["cabin"]["length"]["axis_dis"]/2}, {params["cabin"]["height"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_r_whole']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
# 如果有窗户的话则需要建立窗户的左右上下四部分
# 首先是左边
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["cabin"]["length"]["axis_dis"]-params["window"]["width"]["axis_dis"]*max(params["window"]["right"]["locate"])}, {params["cabin"]["height"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_r_wl', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_r_wl']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_r_wl']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_r_wl']
f = p.faces
faces = f.findAt((({(params["cabin"]["length"]["axis_dis"]-params["window"]["width"]["axis_dis"]*max(params["window"]["right"]["locate"]))/2}, {params["cabin"]["height"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_r_wl']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
# 其次是窗户右侧
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["window"]["width"]["axis_dis"]*(min(params["window"]["right"]["locate"])-1)}, {params["cabin"]["height"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_r_wr', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_r_wr']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_r_wr']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_r_wr']
f = p.faces
faces = f.findAt((({(params["window"]["width"]["axis_dis"]*(min(params["window"]["right"]["locate"])-1))/2}, {params["cabin"]["height"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_r_wr']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
"""
    offside_plate_s= f"""
# 舱体对侧蒙皮钢板
# 首先创建一个通长的
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["cabin"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_off_whole', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_off_whole']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_off_whole']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_off_whole']
f = p.faces
faces = f.findAt((({params["cabin"]["width"]["axis_dis"]/2}, {params["cabin"]["height"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_off_whole']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
# 如果有窗户的话还是要建立一侧
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({(params["cabin"]["width"]["axis_dis"]-params["window"]["offside"]["num"]*params["window"]["width"]["axis_dis"])/2}, {params["cabin"]["height"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_off_w', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_off_w']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_off_w']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_off_w']
f = p.faces
faces = f.findAt((({(params["cabin"]["width"]["axis_dis"]-params["window"]["offside"]["num"]*params["window"]["width"]["axis_dis"])/4}, {params["cabin"]["height"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_off_w']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
"""
    top_plate_s = f"""
# 舱体顶部蒙皮钢板
# 首先创建设备间上方的
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["equip"]["width"]["axis_dis"]}, {params["equip"]["length"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_top_equip', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_top_equip']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_top_equip']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_top_equip']
f = p.faces
faces = f.findAt((({params["equip"]["width"]["axis_dis"]/2}, {params["equip"]["length"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_top_equip']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 再创建门上方的
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["equip"]["width"]["axis_dis"]}, {params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_top_door', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_top_door']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_top_door']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_top_door']
f = p.faces
faces = f.findAt((({params["equip"]["width"]["axis_dis"]/2}, {(params["cabin"]["width"]["axis_dis"]-params["equip"]["length"]["axis_dis"])/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_top_door']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
    
# 再创建剩余长度
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"]}, {params["cabin"]["width"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_top_cabin', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_top_cabin']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_top_cabin']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_top_cabin']
f = p.faces
faces = f.findAt((({(params["cabin"]["length"]["axis_dis"]-params["equip"]["width"]["axis_dis"])/2}, {params["cabin"]["width"]["axis_dis"]}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_top_cabin']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
"""
    door_plate_s = f"""
# 首先是门位置的板
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["door"]["width"]["axis_dis"]}, {params["door"]["height"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_door', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_door']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_door']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_door']
f = p.faces
faces = f.findAt((({params["door"]["width"]["axis_dis"]/2}, {params["door"]["height"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_door']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 其次是门上方
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["door"]["width"]["axis_dis"]}, {params["door"]["top_clear"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_door_up', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_door_up']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_door_up']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_door_up']
f = p.faces
faces = f.findAt((({params["door"]["width"]["axis_dis"]/2}, {params["door"]["top_clear"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_door_up']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)

# 其次是门下方
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["door"]["width"]["axis_dis"]}, {params["door"]["ground_clear"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_door_down', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_door_down']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_door_down']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_door_down']
f = p.faces
faces = f.findAt((({params["door"]["width"]["axis_dis"]/2}, {params["door"]["ground_clear"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_door_down']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
    
# 最后是门左侧
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=10000.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=({params["cabin"]["width"]["axis_dis"]-params["door"]["width"]["axis_dis"]}, {params["cabin"]["height"]["axis_dis"]}))
p = mdb.models['Model-1'].Part(name='plate_door_left', dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['plate_door_left']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['plate_door_left']
del mdb.models['Model-1'].sketches['__profile__']
p = mdb.models['Model-1'].parts['plate_door_left']
f = p.faces
faces = f.findAt((({(params["cabin"]["width"]["axis_dis"]-params["door"]["width"]["axis_dis"])/2}, {params["cabin"]["height"]["axis_dis"]/2}, 0.0), ))
region = regionToolset.Region(faces=faces)
p = mdb.models['Model-1'].parts['plate_door_left']
p.SectionAssignment(region=region, sectionName='plate', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', 
    thicknessAssignment=FROM_SECTION)
"""
    s = (main_frame_s + door_beam_s + window_beam_s + secd_beam_s + cir_main_s + equip_beam_s +
         sup_beam_s + left_plate_s + right_plate_s + top_plate_s + equip_plate_s + offside_plate_s +
         door_plate_s + window_plate_s)
    return s