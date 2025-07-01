# 用于生成舱体的各个表面与荷载

def gen_surf(params):
    s = f"""
# 首先是舱体上表面
a = mdb.models['Model-1'].rootAssembly
s1 = a.instances['cabin_plates-1'].faces
side1Faces1 = s1.findAt(({(params["cabin"]["length"]["axis_dis"] / 2, params["cabin"]["height"]["axis_dis"],
                               params["cabin"]["width"]["axis_dis"] / 2)}, ))
a.Surface(side1Faces=side1Faces1, name='surf_cabin_top')
# 舱体下表面
a = mdb.models['Model-1'].rootAssembly
s1 = a.instances['cabin_plates-1'].faces
side2Faces1 = s1.findAt(({(params["cabin"]["length"]["axis_dis"] / 2, 0.0,
                               params["cabin"]["width"]["axis_dis"] / 2)}, ))
a.Surface(side2Faces=side2Faces1, name='surf_cabin_btm')
# 设备间长度方向面
a = mdb.models['Model-1'].rootAssembly
s1 = a.instances['cabin_plates-1'].faces
side1Faces1 = s1.findAt(({(params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"],
                               params["cabin"]["height"]["axis_dis"] / 2,
                               params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"] / 2)}, ))
a.Surface(side1Faces=side1Faces1, name='surf_equip_l')
# 设备间宽度方向面
a = mdb.models['Model-1'].rootAssembly
s1 = a.instances['cabin_plates-1'].faces
side2Faces1 = s1.findAt(({(params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"] / 2,
                               params["cabin"]["height"]["axis_dis"] / 2,
                               params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"])}, ))
a.Surface(side2Faces=side2Faces1, name='surf_equip_w')
# 门顶面
a = mdb.models['Model-1'].rootAssembly
s1 = a.instances['cabin_plates-1'].faces
side1Faces1 = s1.findAt(({(params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"] / 2,
                               params["cabin"]["height"]["axis_dis"],
                               (params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]) / 2)}, ))
a.Surface(side1Faces=side1Faces1, name='surf_door_top')
# 门底面
a = mdb.models['Model-1'].rootAssembly
s1 = a.instances['cabin_plates-1'].faces
side2Faces1 = s1.findAt(({(params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"] / 2, 0.0,
                               (params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"]) / 2)}, ))
a.Surface(side2Faces=side2Faces1, name='surf_door_btm')
# 门上下左
a = mdb.models['Model-1'].rootAssembly
s1 = a.instances['cabin_plates-1'].faces
side1Faces1 = s1.findAt(({(params["cabin"]["length"]["axis_dis"], params["door"]["ground_clear"]["axis_dis"] / 2,
                               params["door"]["width"]["axis_dis"] / 2)}, ), ({(params["cabin"]["length"]["axis_dis"],
                               params["cabin"]["height"]["axis_dis"] - params["door"]["top_clear"]["axis_dis"] / 2,
                               params["door"]["width"]["axis_dis"] / 2)}, ), ({(params["cabin"]["length"]["axis_dis"], params["cabin"]["height"]["axis_dis"] / 2, (
                params["cabin"]["width"]["axis_dis"] - params["equip"]["length"]["axis_dis"] - params["door"]["width"][
            "axis_dis"]) / 2 + params["door"]["width"]["axis_dis"])}, ))
a.Surface(side1Faces=side1Faces1, name='surf_door_round')
"""

    # 接下来根据舱体是否带有窗户生成三个侧面
    if params["window"]["right"]["num"] ==0:
        s += f"""
a = mdb.models['Model-1'].rootAssembly
s1 = a.instances['cabin_plates-1'].faces
side1Faces1 = s1.findAt(({(params["cabin"]["length"]["axis_dis"] / 2, params["cabin"]["height"]["axis_dis"] / 2, 0.0)}, ))
a.Surface(side1Faces=side1Faces1, name='surf_cabin_right')
"""
    else:
        s += f"""
a = mdb.models['Model-1'].rootAssembly
s1 = a.instances['cabin_plates-1'].faces
side1Faces1 = s1.findAt(({((params["window"]["right"]["locate"] - 1) * params["window"]["width"]["axis_dis"]+ params["window"]["width"]["axis_dis"]/2,
                                   params["window"]["ground_clear"]["axis_dis"] + params["window"]["height"][
                                       "axis_dis"] + params["window"]["top_clear"]["axis_dis"]/2, 0.0)}, ), ({((params["window"]["right"]["locate"] - 1) * params["window"]["width"]["axis_dis"] + params["window"]["ground_clear"]["axis_dis"]/2, params["window"]["ground_clear"]["axis_dis"]/2, 0.0)}, 
    ), ({(params["window"]["width"]["axis_dis"]*(params["window"]["right"]["locate"]-1)/2, params["cabin"]["height"]["axis_dis"]/2, 0.0)}, ), ({(params["window"]["right"]["locate"] * params["window"]["width"]["axis_dis"] + (params["cabin"]["length"]["axis_dis"]-params["window"]["width"]["axis_dis"]*params["window"]["right"]["locate"])/2, params["cabin"]["height"]["axis_dis"]/2, 0.0)},))
a.Surface(side1Faces=side1Faces1, name='surf_cabin_right')
"""

    if params["window"]["left"]["num"] == 0:
        s += f"""
a = mdb.models['Model-1'].rootAssembly
s1 = a.instances['cabin_plates-1'].faces
side2Faces1 = s1.findAt(({((params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"]) / 2,
                                   params["cabin"]["height"]["axis_dis"] / 2, params["cabin"]["width"]["axis_dis"])}, ))
a.Surface(side2Faces=side2Faces1, name='surf_cabin_left')
"""
    else:
        s += f"""
a = mdb.models['Model-1'].rootAssembly
s1 = a.instances['cabin_plates-1'].faces
side2Faces1 = s1.findAt(({((params["window"]["left"]["locate"] - 1) * params["window"]["width"]["axis_dis"] +
                                   params["window"]["width"]["axis_dis"] / 2,
                                   params["window"]["ground_clear"]["axis_dis"] + params["window"]["height"][
                                       "axis_dis"] + params["window"]["top_clear"]["axis_dis"] / 2, params["cabin"]["width"]["axis_dis"])}, ), ({((params["window"]["left"]["locate"] - 1) * params["window"]["width"]["axis_dis"] +
             params["window"]["ground_clear"]["axis_dis"] / 2, params["window"]["ground_clear"]["axis_dis"] / 2, params["cabin"]["width"]["axis_dis"])}, ), ({(
                                  params["window"]["width"]["axis_dis"] * (params["window"]["left"]["locate"] - 1) / 2,
                                  params["cabin"]["height"]["axis_dis"] / 2, params["cabin"]["width"]["axis_dis"])}, ), ({(params["window"]["left"]["locate"] * params["window"]["width"]["axis_dis"] + (
                        params["cabin"]["length"]["axis_dis"] - params["equip"]["width"]["axis_dis"] - params["window"]["width"]["axis_dis"] *
                        params["window"]["left"]["locate"]) / 2, params["cabin"]["height"]["axis_dis"] / 2, params["cabin"]["width"]["axis_dis"])}, ))
a.Surface(side2Faces=side2Faces1, name='surf_cabin_left')
"""

    if params["window"]["offside"]["num"] == 0:
        s += f"""
a = mdb.models['Model-1'].rootAssembly
s1 = a.instances['cabin_plates-1'].faces
side2Faces1 = s1.findAt(({(0.0, params["cabin"]["height"]["axis_dis"] / 2, params["cabin"]["width"]["axis_dis"] / 2)}, ))
a.Surface(side2Faces=side2Faces1, name='surf_cabin_offside')
"""
    else:
        # 此时创建一个列表去存储窗户上下的位置坐标
        coord_list = []
        for i in range(params["window"]["offside"]["num"]):
            coord_list.append(
                (
                    0.0,
                    params["window"]["ground_clear"]["axis_dis"] / 2,
                    (params["cabin"]["width"]["axis_dis"] - params["window"]["offside"]["num"] *
                     params["window"]["width"]["axis_dis"]) / 2 + (i + 0.5) * params["window"]["width"]["axis_dis"]
                )
            )
            coord_list.append(
                (
                    0.0,
                    params["cabin"]["height"]["axis_dis"] - params["window"]["top_clear"]["axis_dis"] / 2,
                    (params["cabin"]["width"]["axis_dis"] - params["window"]["offside"]["num"] *
                     params["window"]["width"]["axis_dis"]) / 2 + (i + 0.5) * params["window"]["width"]["axis_dis"]
                )
            )
        # 最后再加上窗户两侧的部分
        coord_list.append(
            (
                0.0,
                params["cabin"]["height"]["axis_dis"] / 2,
                (params["cabin"]["width"]["axis_dis"] - params["window"]["offside"]["num"] *
                 params["window"]["width"]["axis_dis"]) / 4
            )
        )
        coord_list.append(
            (
                0.0,
                params["cabin"]["height"]["axis_dis"] / 2,
                params["cabin"]["width"]["axis_dis"] - (
                            params["cabin"]["width"]["axis_dis"] - params["window"]["offside"]["num"] *
                            params["window"]["width"]["axis_dis"]) / 4
            )
        )
        s += f"""
a = mdb.models['Model-1'].rootAssembly
s1 = a.instances['cabin_plates-1'].faces
face_coord_list = {coord_list}
side2Faces1 = s1.findAt(*tuple((coord,) for coord in face_coord_list))
a.Surface(side2Faces=side2Faces1, name='surf_cabin_offside')
"""
    return s

def gen_load_g(params):
    gravity_s = f"""
mdb.models['Model-1'].Gravity(name='Load-G', createStepName='Step-2', 
    comp2=-9800.0, distributionType=UNIFORM, field='')
"""
    s = gravity_s
    return s

def gen_pressure(params):
    # 为每一个面施加相应的内压
    s = f"""
a = mdb.models['Model-1'].rootAssembly
region = a.surfaces['surf_cabin_btm']
mdb.models['Model-1'].Pressure(name='Load-Pressure-cabin_btm', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]*params["load"]["ratio"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_cabin_top']
mdb.models['Model-1'].Pressure(name='Load-Pressure-cabin_top', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]*params["load"]["ratio"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_cabin_left']
mdb.models['Model-1'].Pressure(name='Load-Pressure-cabin_left', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]*params["load"]["ratio"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_cabin_right']
mdb.models['Model-1'].Pressure(name='Load-Pressure-cabin_right', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]*params["load"]["ratio"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_cabin_offside']
mdb.models['Model-1'].Pressure(name='Load-Pressure-cabin_offside', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]*params["load"]["ratio"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_door_top']
mdb.models['Model-1'].Pressure(name='Load-Pressure-door_top', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]*params["load"]["ratio"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_door_btm']
mdb.models['Model-1'].Pressure(name='Load-Pressure-door_btm', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]*params["load"]["ratio"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_door_round']
mdb.models['Model-1'].Pressure(name='Load-Pressure-door_round', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]*params["load"]["ratio"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_equip_l']
mdb.models['Model-1'].Pressure(name='Load-Pressure-equip_l', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]*params["load"]["ratio"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_equip_w']
mdb.models['Model-1'].Pressure(name='Load-Pressure-equip_w', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]*params["load"]["ratio"]["pres"]}, 
    amplitude=UNSET)
"""
    return s

def gen_dead_live_load(params):
    s = ""
    s += f"""
# 施加底面恒荷载 
a = mdb.models['Model-1'].rootAssembly
region = a.surfaces['surf_cabin_btm']
mdb.models['Model-1'].Pressure(name='Load-dead_cabin_btm', 
    createStepName='Step-2', region=region, distributionType=UNIFORM, field='', 
    magnitude={params["load"]["basic"]["dead"]*params["load"]["ratio"]["dead"]}, amplitude=UNSET)

a = mdb.models['Model-1'].rootAssembly
region = a.surfaces['surf_door_btm']
mdb.models['Model-1'].Pressure(name='Load-dead_door_btm', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["dead"]*params["load"]["ratio"]["dead"]}, 
    amplitude=UNSET)

# 施加底面活荷载
a = mdb.models['Model-1'].rootAssembly
region = a.surfaces['surf_cabin_btm']
mdb.models['Model-1'].Pressure(name='Load-live_cabin_btm', 
    createStepName='Step-2', region=region, distributionType=UNIFORM, field='', 
    magnitude={params["load"]["basic"]["live"]*params["load"]["ratio"]["live"]}, amplitude=UNSET)

a = mdb.models['Model-1'].rootAssembly
region = a.surfaces['surf_door_btm']
mdb.models['Model-1'].Pressure(name='Load-live_door_btm', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["live"]*params["load"]["ratio"]["live"]}, 
    amplitude=UNSET)
"""
    return s