import gradio as gr
import os
import json
import copy
import requests
from openai import OpenAI
import tkinter as tk
from tkinter import filedialog
import threading
import queue
import time

import cabin_processor.iterator as i
import cabin_processor.submitter as s
from cabin_result.summary import process_all_folders
import sys
import io
from docx import Document
from PIL import Image


content_str_default = "生成一个舱体长度为12m,窗户宽度为1.2m，舱体右侧开窗户位置分别为2，4，5，舱体左侧开窗户位置为2，4，3，5，6，的3D结构模型。"
base_params = {
    "舱体长度": 12000.0,
    "窗户信息": {
        "宽": 1200.0,
        "舱体右侧窗户": {
            "位置": [2,4,5]
        },
        "舱体左侧窗户": {
            "位置": [2,4,3,5,6]
        },
        "偏置": {
            "大小": 2
        }
    }
}

window_widths = [500.0, 700.0, 800.0, 1000.0, 1200.0]

openai_api_key = "NONE" 
openai_api_base = "http://10.11.205.10:8000/v1"  # 替换为你的vllm部署的DeepSeek API地址

client = OpenAI(api_key=openai_api_key, base_url=openai_api_base)

models = client.models.list()
model_id = models.data[0].id if models.data else None

log_path =  "cabin.log"
last_position = 0

def get_log_content():
    try:
        if not os.path.exists(log_path):
            return ""
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return "".join(lines)
    except Exception as e:
        return f"读取日志失败: {e}"

def read_docx_with_images(folderpath):
    print("Reading docx file:", folderpath)
    if not folderpath or not os.path.exists(folderpath):
        return "", None
    docx_files = os.path.join(folderpath, "方案比选报告.docx")
    doc = Document(docx_files)

    elements = []
    for block in doc.element.body:
        if block.tag.endswith('}p'):
            para = block
            text = "".join([node.text or "" for node in para.iter() if node.tag.endswith('}t')])
            elements.append(text)
        elif block.tag.endswith('}tbl'):
            table = block
            table_data = []
            for row in table.iterfind('.//w:tr', namespaces=doc.element.nsmap):
                row_data = []
                for cell in row.iterfind('.//w:tc', namespaces=doc.element.nsmap):
                    cell_text = "".join([node.text or "" for node in cell.iter() if node.tag.endswith('}t')])
                    row_data.append(cell_text)
                table_data.append(row_data)
            elements.append(table_data)


    # 整理文本和表格内容
    text = ""
    tables_content = []
    for elem in elements:
        if isinstance(elem, str):
            text += elem + "\n"
        elif isinstance(elem, list):
            # 格式化表格内容为文本
            table_str = "\n".join(["\t".join(row) for row in elem])
            tables_content.append(table_str)
            text += table_str + "\n"

    # 提取图片并转换为RGB图像
    images = []
    rels = doc.part.rels
    for rel in rels:
        rel = rels[rel]
        if "image" in rel.target_ref:
            image_data = rel.target_part.blob
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            images.append(image)

    return text, images[0:4]  

def convert_keys(data):
    if isinstance(data, dict):
        new_data = {}
        for k, v in data.items():
            if k == "舱体长度":
                new_data["cabin_length"] = convert_keys(v)
            elif k == "窗户信息":
                new_data["window"] = convert_keys(v)
            elif k == "宽":
                new_data["width"] = convert_keys(v)
            elif k == "舱体右侧窗户":
                new_data["right"] = convert_keys(v)
            elif k == "舱体左侧窗户":
                new_data["left"] = convert_keys(v)
            elif k == "个数":
                new_data["num"] = convert_keys(v)
            elif k == "位置":
                new_data["locate"] = convert_keys(v)
            elif k == "偏置":
                new_data["offside"] = convert_keys(v)
            elif k == "大小":
                new_data["num"] = convert_keys(v)
            else:
                new_data[k] = convert_keys(v)
        return new_data
    elif isinstance(data, list):
        return [convert_keys(item) for item in data]
    else:
        return data
    
# 假设的大模型对话函数
def llm_chat(user_input, history):
    
    template = (
        "请将下面的内容转换为JSON格式，字段包括舱体长度和窗户信息（包含窗户宽、舱体右侧窗户、舱体左侧窗户、偏置等子字段），"
        "确保输出的JSON结构与示例一致，只输出JSON，键名必须使用双引号，不要添加其他内容。\n"
        "示例：\n"
        f"{base_params}\n"
        "内容：\n"
        f"{content_str_default}\n"
        "请输出对应的JSON："
    )
    messages = [
        {"role": "user", "content": template}
    ]
    response = client.chat.completions.create(
        model=model_id, messages=messages, temperature=0.7)
    
    content = response.choices[0].message.content if response.choices else "No response"
    print("Model response:", content)
    # response_new = f"你说：{content}"
    # history = history + [(user_input, content)]
    history = [(user_input, content)]
    return content, history

# vLLM部署的DeepSeek服务请求函数示例
def request_deepseek_vllm(prompt, history=None, api_url="http://10.11.205.10:8000/generate"):
    """
    向vLLM部署的DeepSeek服务发送请求，获取模型回复
    :param prompt: 用户输入
    :param history: 对话历史（可选）
    :param api_url: DeepSeek服务API地址
    :return: 模型回复文本
    """
    payload = {
        "prompt": prompt,
        "history": history or []
    }
    try:
        response = requests.post(api_url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        # 假设返回格式为 {"response": "..."}
        return data.get("response", "")
    except Exception as e:
        return f"请求DeepSeek服务失败: {e}"


with gr.Blocks() as demo:
    # gr.Markdown("# 增压仓体设计助手")
    with gr.Row():
        gr.Markdown(
            "# 增压仓体设计助手",
            elem_id="centered-title"
        )

    with gr.Row():
        # 左侧：对话框
        with gr.Column():
            chatbot = gr.Chatbot(label="需求理解")
            msg = gr.Textbox(label="描述你需要生成的舱体尺寸和窗户信息", value=content_str_default)
            state = gr.State([])
            require_resp = gr.Textbox(visible=False, value=base_params)  # 隐藏的响应框，用于存储模型回复

            # 将msg的内容作为llm_chat的输入，在点击send_btn后发送接口请求
            def user_chat(user_message, chat_history):
                response, chat_history = llm_chat(user_message, chat_history)
                return chat_history, chat_history, response

            send_btn = gr.Button("解析需求")
            send_btn.click(
                user_chat,
                inputs=[msg, state],
                outputs=[chatbot, state, require_resp],
            )

        with gr.Column():
            gr.Markdown("## 舱体设计参数")
            # 左侧参数解析按钮
            with gr.Row():
                parse_btn_left = gr.Button("左侧参数同步", elem_id="parse-btn-left", interactive=False)

                def response_not_empty(response_val):
                    return gr.update(interactive=bool(response_val and response_val.strip()))
                require_resp.change(
                    response_not_empty,
                    inputs=[require_resp],
                    outputs=[parse_btn_left]
                )

            # 舱体参数输入区
            with gr.Row():
                cabin_length_input = gr.Textbox(label="舱体长度 (mm)", value=None, placeholder="12000", interactive=True)
            # 窗户参数输入区
            gr.Markdown("### 窗户参数") # 添加标题  
            # 窗户宽度单独一行
            with gr.Row():
                window_width_input = gr.Textbox(label="窗户宽度 (mm)", value=None, placeholder="1250", interactive=True)
            # 左侧窗户参数一行两列
            with gr.Row():
                with gr.Column():
                    left_window_locate = gr.Textbox(label="舱体左侧窗户位置", value=None, placeholder="多个位置用逗号分隔", interactive=True)
            # 右侧窗户参数一行两列
            with gr.Row():
                with gr.Column():
                    right_window_locate = gr.Textbox(label="舱体右侧窗户位置", value=None, placeholder="多个位置用逗号分隔", interactive=True)
            # 偏置大小单独一行
            with gr.Row():
                offside_num = gr.Textbox(label="偏置大小（mm）", value=None, placeholder="2", interactive=True) 

            def fill_value_from_content(content):
                try:
                    print("Received content:", content)
                    # 如果content以```json开头，则去除前缀和后缀
                    if content.strip().startswith("```json"):
                        content = content.strip()
                        # 去除头部的```json和尾部的```
                        content = content[7:]  # 去除```json
                        if content.endswith("```"):
                            content = content[:-3]
                        content = content.strip()
                    print("content first char:", content[0] if content else "EMPTY")
                    print("content first line:", content.splitlines()[0] if content else "EMPTY")
                    # 如果第一行内容不存在（为空），则去除第一行
                    lines = content.splitlines()
                    if lines and not lines[0].strip():
                        content = "\n".join(lines[1:])
                        print("Updated content after removing first line:", content)
                    content_data = json.loads(content)
                    print("Parsed content data:", content_data)
                    # 支持两种key风格
                    if "cabin_length" in content_data:
                        cabin_length = content_data.get("cabin_length")
                        window_width = content_data.get("window").get("width")
                        right_loc = content_data.get("window").get("right").get("locate")
                        left_loc = content_data.get("window").get("left").get("locate")
                        offside_num_val = content_data.get("window").get("offside").get("num")
                    else:
                        # 中文key
                        cabin_length = content_data.get("舱体长度")
                        print("cabin_length:", cabin_length)
                        window_width = content_data.get("窗户信息").get("宽")
                        print("window_width:", window_width)
                        right_loc = content_data.get("窗户信息").get("舱体右侧窗户").get("位置")
                        print("right_loc:", right_loc)
                        left_loc = content_data.get("窗户信息").get("舱体左侧窗户").get("位置")
                        print("left_loc:", left_loc)
                        offside_num_val = content_data.get("窗户信息").get("偏置").get("大小")
                        print("offside_num_val:", offside_num_val)

                    return (
                        cabin_length, window_width,
                        right_loc, left_loc,
                        offside_num_val
                    )
                except Exception as e:
                    gr.Warning(f"数据异常: {e}")
                    return (None, None, None, None, None)
                    
                
            parse_btn_left.click(
                fill_value_from_content,
                inputs=[require_resp],
                outputs=[cabin_length_input, window_width_input,
                    right_window_locate, left_window_locate,
                    offside_num]
            )    

            gr.Markdown("### 存储路径") # 添加标题  
            with gr.Row():
                # work_path_output = gr.Textbox(label="存储路径", value="F:\\CAE\\cube")
                work_path_output = gr.Textbox(label="路径地址", value=None, interactive=True, placeholder="请先选择存储路径", elem_id="work-path-input")
                
                # 将work_path设计为Button，选定文件夹后将路径赋值给work_path_output
                work_save_path = gr.Button("选择文件夹")
                def select_folder():
                    root = tk.Tk()
                    root.withdraw()
                    folder_path = filedialog.askdirectory()
                    root.destroy()
                    return folder_path

                work_save_path.click(
                    lambda: select_folder(),
                    inputs=[],
                    outputs=[work_path_output]
                )


    with gr.Row():
        generate_scheme_btn = gr.Button("生成设计方案", elem_id="generate-scheme-btn", scale=1, interactive=False)
        # 控制“生成设计方案”按钮的可用性
        def check_inputs(
            cabin_length, window_width,
            right_loc, left_loc,
            offside, work_path
        ):
            # 检查所有输入是否都有值且非空
            all_filled = all([
            cabin_length not in (None, "", []),
            window_width not in (None, "", []),
            right_loc not in (None, "", []),
            left_loc not in (None, "", []),
            offside not in (None, "", []),
            work_path not in (None, "", [])
            ])
            return gr.update(interactive=all_filled)

        cabin_length_input.change(
            check_inputs,
            inputs=[
            cabin_length_input, window_width_input,
            right_window_locate, left_window_locate,
            offside_num, work_path_output
            ],
            outputs=[generate_scheme_btn]
        )
        window_width_input.change(
            check_inputs,
            inputs=[
            cabin_length_input, window_width_input,
            right_window_locate, left_window_locate,
            offside_num, work_path_output
            ],
            outputs=[generate_scheme_btn]
        )
        right_window_locate.change(
            check_inputs,
            inputs=[
            cabin_length_input, window_width_input,
            right_window_locate, left_window_locate,
            offside_num, work_path_output
            ],
            outputs=[generate_scheme_btn]
        )
        left_window_locate.change(
            check_inputs,
            inputs=[
            cabin_length_input, window_width_input,
            right_window_locate, left_window_locate,
            offside_num, work_path_output
            ],
            outputs=[generate_scheme_btn]
        )
        offside_num.change(
            check_inputs,
            inputs=[
            cabin_length_input, window_width_input,
            right_window_locate, left_window_locate,
            offside_num, work_path_output
            ],
            outputs=[generate_scheme_btn]
        )
        work_path_output.change(
            check_inputs,
            inputs=[
            cabin_length_input, window_width_input,
            right_window_locate, left_window_locate,
            offside_num, work_path_output
            ],
            outputs=[generate_scheme_btn]
        )
    with gr.Row():
        with gr.Column():
            
            gr.Markdown("### 生成过程日志")
            log_refresh_btn = gr.Button("刷新日志", interactive=False)
            process_log = gr.Textbox(label="生成进度信息", lines=10, interactive=False)
            
            def check_logfile_exists():
                if not os.path.exists(log_path):
                    return gr.update(interactive=False), ""
                else:
                    return gr.update(interactive=True)
                
            work_path_output.change(
                check_logfile_exists,
                inputs=[],
                outputs=[log_refresh_btn]
            )
            log_refresh_btn.click(
                get_log_content,
                inputs=[],
                outputs=[process_log]
            )

        with gr.Column():
            gr.Markdown("### 生成模型结果")
            model_refresh_btn = gr.Button("刷新模型信息", interactive=False)
            modelfile = gr.Textbox(visible=False, value=None)  # 隐藏的响应框，用于存储模型回复
            result_output = gr.Textbox(label="模型信息", lines=10, interactive=False)
            images_output = gr.Gallery(label="图片", show_label=True)
            
            def on_generate_scheme_click(content, 
                                        cabin_length_input, window_width_input,
                                        right_window_locate, left_window_locate,
                                        offside_num, work_path_output):

                print("Received content:", content)
                # 如果content以```json开头，则去除前缀和后缀
                if content.strip().startswith("```json"):
                    content = content.strip()
                    # 去除头部的```json和尾部的```
                    content = content[7:]  # 去除```json
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()
                print("content first char:", content[0] if content else "EMPTY")
                print("content first line:", content.splitlines()[0] if content else "EMPTY")
                # 如果第一行内容不存在（为空），则去除第一行
                lines = content.splitlines()
                if lines and not lines[0].strip():
                    content = "\n".join(lines[1:])
                    print("Updated content after removing first line:", content)
                content_data = json.loads(content)
                print("Parsed content data:", content_data)

                content_data = convert_keys(content_data)
                print("Converted content data:", content_data)
                print("Work path:", work_path_output)
                # 用输入框的值覆盖content_data内对应key
                content_data["cabin_length"] = float(cabin_length_input) if cabin_length_input else content_data.get("cabin_length")
                if "window" not in content_data:
                    content_data["window"] = {}
                content_data["window"]["width"] = float(window_width_input) if window_width_input else content_data["window"].get("width")
                if "right" not in content_data["window"]:
                    content_data["window"]["right"] = {}
                if right_window_locate:
                    if right_window_locate.startswith("[") and right_window_locate.endswith("]"):
                        right_window_locate = right_window_locate[1:-1]  # 去除首尾[]
                    if ',' in right_window_locate:
                        content_data["window"]["right"]["locate"] = [int(x.strip()) for x in str(right_window_locate).split(',') if x.strip()]
                    else:
                        content_data["window"]["right"]["locate"] = int(right_window_locate)
                else:
                    content_data["window"]["right"]["locate"] = content_data["window"]["right"].get("locate")
                if "left" not in content_data["window"]:
                    content_data["window"]["left"] = {}
                if left_window_locate:
                    if left_window_locate.startswith("[") and left_window_locate.endswith("]"):
                        left_window_locate = left_window_locate[1:-1]  # 去除首尾[]
                    if ',' in str(left_window_locate):
                        content_data["window"]["left"]["locate"] = [int(x.strip()) for x in str(left_window_locate).split(',') if x.strip()]
                    else:
                        content_data["window"]["left"]["locate"] = int(left_window_locate)
                else:
                    content_data["window"]["left"]["locate"] = content_data["window"]["left"].get("locate")
                if "offside" not in content_data["window"]:
                    content_data["window"]["offside"] = {}
                content_data["window"]["offside"]["num"] = int(offside_num) if offside_num else content_data["window"]["offside"].get("num")

                for k in range(len(window_widths)):
                    params = copy.deepcopy(content_data)
                    params["window"]["width"] = window_widths[k]
                    # globals()[f'params{k + 1}'] = params
                    
                    a = i.PartsIterator(params, work_path_output)
                    a.run()

                docx_filepath = process_all_folders(work_path_output)
                return docx_filepath

            generate_scheme_btn.click(
                on_generate_scheme_click,
                inputs=[require_resp, 
                        cabin_length_input, window_width_input,
                        right_window_locate, left_window_locate,
                        offside_num, work_path_output],
                outputs=[modelfile]
            )

            def check_modelfile_exists(work_path):
                if not work_path or not os.path.exists(work_path):
                    print("工作路径不存在或未设置:", work_path)
                    return gr.update(interactive=False), ""
                # 判断路径中是否包含“方案比选报告.docx”
                if "方案比选报告.docx" in os.path.basename(work_path):
                    docx_files = work_path
                else:
                    docx_files = os.path.join(work_path, "方案比选报告.docx")
                print("Checking for docx file:", docx_files)
                if os.path.exists(docx_files):
                    # 存在docx文件，按钮可点击
                    return gr.update(interactive=True)
                else:
                    # 不存在docx文件，按钮不可点击
                    print("方案比选报告.docx not found in", work_path)
                    return gr.update(interactive=False)
                
            modelfile.change(
                check_modelfile_exists,
                inputs=[modelfile],
                outputs=[model_refresh_btn]
            )

            model_refresh_btn.click(
                read_docx_with_images,
                inputs=[work_path_output],
                outputs=[result_output, images_output]
            )
            
# demo.launch()
demo.launch(server_name='0.0.0.0', server_port=7860, share=True)

