
def gen_head(params):
    return f"""# -*- coding: UTF-8 -*-
import os
from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
Mdb()
os.chdir(r"{params["output"]["dir"]}")
"""