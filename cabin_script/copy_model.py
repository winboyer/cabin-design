# 复制一个模型，计算挠度结果
def copy_model(params, cpu_num):
    s = f"""
mdb.Model(name='Model-2', objectToCopy=mdb.models['Model-1'])

# 删除掉原有荷载（保留重力）
del mdb.models['Model-2'].loads['Load-Pressure-cabin_btm']
del mdb.models['Model-2'].loads['Load-Pressure-cabin_left']
del mdb.models['Model-2'].loads['Load-Pressure-cabin_offside']
del mdb.models['Model-2'].loads['Load-Pressure-cabin_right']
del mdb.models['Model-2'].loads['Load-Pressure-cabin_top']
del mdb.models['Model-2'].loads['Load-Pressure-door_btm']
del mdb.models['Model-2'].loads['Load-Pressure-door_round']
del mdb.models['Model-2'].loads['Load-Pressure-door_top']
del mdb.models['Model-2'].loads['Load-Pressure-equip_l']
del mdb.models['Model-2'].loads['Load-Pressure-equip_w']
del mdb.models['Model-2'].loads['Load-dead_cabin_btm']
del mdb.models['Model-2'].loads['Load-dead_door_btm']
del mdb.models['Model-2'].loads['Load-live_cabin_btm']
del mdb.models['Model-2'].loads['Load-live_door_btm']

# 重新施加没有系数的荷载
a = mdb.models['Model-2'].rootAssembly
region = a.surfaces['surf_cabin_btm']
mdb.models['Model-2'].Pressure(name='Load-Pressure-cabin_btm', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_cabin_top']
mdb.models['Model-2'].Pressure(name='Load-Pressure-cabin_top', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_cabin_left']
mdb.models['Model-2'].Pressure(name='Load-Pressure-cabin_left', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_cabin_right']
mdb.models['Model-2'].Pressure(name='Load-Pressure-cabin_right', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_cabin_offside']
mdb.models['Model-2'].Pressure(name='Load-Pressure-cabin_offside', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_door_top']
mdb.models['Model-2'].Pressure(name='Load-Pressure-door_top', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_door_btm']
mdb.models['Model-2'].Pressure(name='Load-Pressure-door_btm', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_door_round']
mdb.models['Model-2'].Pressure(name='Load-Pressure-door_round', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_equip_l']
mdb.models['Model-2'].Pressure(name='Load-Pressure-equip_l', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]}, 
    amplitude=UNSET)
region = a.surfaces['surf_equip_w']
mdb.models['Model-2'].Pressure(name='Load-Pressure-equip_w', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["pres"]}, 
    amplitude=UNSET)
    
# 施加底面恒荷载 
a = mdb.models['Model-2'].rootAssembly
region = a.surfaces['surf_cabin_btm']
mdb.models['Model-2'].Pressure(name='Load-dead_cabin_btm', 
    createStepName='Step-2', region=region, distributionType=UNIFORM, field='', 
    magnitude={params["load"]["basic"]["dead"]}, amplitude=UNSET)

a = mdb.models['Model-2'].rootAssembly
region = a.surfaces['surf_door_btm']
mdb.models['Model-2'].Pressure(name='Load-dead_door_btm', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["dead"]}, 
    amplitude=UNSET)

# 施加底面活荷载
a = mdb.models['Model-2'].rootAssembly
region = a.surfaces['surf_cabin_btm']
mdb.models['Model-2'].Pressure(name='Load-live_cabin_btm', 
    createStepName='Step-2', region=region, distributionType=UNIFORM, field='', 
    magnitude={params["load"]["basic"]["live"]}, amplitude=UNSET)

a = mdb.models['Model-2'].rootAssembly
region = a.surfaces['surf_door_btm']
mdb.models['Model-2'].Pressure(name='Load-live_door_btm', createStepName='Step-2', 
    region=region, distributionType=UNIFORM, field='', magnitude={params["load"]["basic"]["live"]}, 
    amplitude=UNSET)

# 重新创建作业
mdb.Job(name='Job-Deflection', model='Model-2', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus={cpu_num}, 
    numDomains={cpu_num}, numGPUs=0)
    
# 尝试更改场输出请求
mdb.models['Model-2'].FieldOutputRequest(name='F-Output-1', 
    createStepName='Step-2', variables=('S', 'U'), frequency=LAST_INCREMENT, region=MODEL, exteriorOnly=OFF)
"""
    return s