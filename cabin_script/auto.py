import os
import subprocess

def put_job(params):

    # 构造命令行字符串
    script_path = params["output"]["dir"]+"\\cube.py"
    work_dir = os.path.dirname(script_path)
    # shell解析 .bat
    cmd_str = (
        f'abaqus cae noGUI={script_path}'
    )
    process = subprocess.run(
        cmd_str,
        cwd=work_dir,
        shell=True,
        capture_output=True,
        text=True
    )
    if process.returncode != 0:
        print("Abaqus 计算出错，返回码:", process.returncode)
        print("stderr:", process.stderr)
    return
