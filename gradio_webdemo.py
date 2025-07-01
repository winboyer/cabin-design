import gradio as gr
import os
import json
import requests
from openai import OpenAI
import tkinter as tk
from tkinter import filedialog
import threading
import queue
import time

import cabin_processor.iterator as i
import cabin_processor.submitter as s


content_str_default = "生成一个舱体长度为12m,窗户宽度为1.25m，舱体右侧开1扇窗户，位置为2，舱体是左侧开1扇窗户，位置为2，的3D结构模型。"
params = {
    "舱体长度": 12000.0,
    "窗户信息": {
        "宽": 1250.0,
        "舱体右侧窗户": {
            "个数": 1,
            "位置": 2
        },
        "舱体左侧窗户": {
            "个数": 1,
            "位置": 2
        },
        "偏置": {
            "大小": 2
        }
    }
}

openai_api_key = "NONE" 
openai_api_base = "http://10.11.205.10:8000/v1"  # 替换为你的vllm部署的DeepSeek API地址

client = OpenAI(api_key=openai_api_key, base_url=openai_api_base)

models = client.models.list()
model_id = models.data[0].id if models.data else None

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
        f"{params}\n"
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
            require_resp = gr.Textbox(visible=False)  # 隐藏的响应框，用于存储模型回复

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
                    left_window_num = gr.Textbox(label="舱体左侧窗户个数", value=None, placeholder="1", interactive=True)
                with gr.Column():
                    left_window_locate = gr.Textbox(label="舱体左侧窗户位置", value=None, placeholder="多个位置用逗号分隔", interactive=True)
            # 右侧窗户参数一行两列
            with gr.Row():
                with gr.Column():
                    right_window_num = gr.Textbox(label="舱体右侧窗户个数", value=None, placeholder="1", interactive=True)
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
                        right_num, right_loc = content_data.get("window").get("right").get("num"), content_data.get("window").get("right").get("locate")
                        left_num, left_loc = content_data.get("window").get("left").get("num"), content_data.get("window").get("left").get("locate")
                        offside_num_val = content_data.get("window").get("offside").get("num")
                    else:
                        # 中文key
                        cabin_length = content_data.get("舱体长度")
                        print("cabin_length:", cabin_length)
                        window_width = content_data.get("窗户信息").get("宽")
                        print("window_width:", window_width)
                        right_num, right_loc = content_data.get("窗户信息").get("舱体右侧窗户").get("个数"), content_data.get("窗户信息").get("舱体右侧窗户").get("位置")
                        print("right_num:", right_num, "right_loc:", right_loc)
                        left_num, left_loc = content_data.get("窗户信息").get("舱体左侧窗户").get("个数"), content_data.get("窗户信息").get("舱体左侧窗户").get("位置")
                        print("left_num:", left_num, "left_loc:", left_loc)
                        offside_num_val = content_data.get("窗户信息").get("偏置").get("大小")
                        print("offside_num_val:", offside_num_val)

                    return (
                        cabin_length, window_width,
                        right_num, right_loc,
                        left_num, left_loc,
                        offside_num_val
                    )
                except Exception as e:
                    gr.Warning(f"数据异常: {e}")
                    return (None, None, None, None, None, None, None)
                    
                
            parse_btn_left.click(
                fill_value_from_content,
                inputs=[require_resp],
                outputs=[cabin_length_input, window_width_input,
                    right_window_num, right_window_locate,
                    left_window_num, left_window_locate,
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
            right_num, right_loc,
            left_num, left_loc,
            offside, work_path
        ):
            # 检查所有输入是否都有值且非空
            all_filled = all([
            cabin_length not in (None, "", []),
            window_width not in (None, "", []),
            right_num not in (None, "", []),
            right_loc not in (None, "", []),
            left_num not in (None, "", []),
            left_loc not in (None, "", []),
            offside not in (None, "", []),
            work_path not in (None, "", [])
            ])
            return gr.update(interactive=all_filled)

        cabin_length_input.change(
            check_inputs,
            inputs=[
            cabin_length_input, window_width_input,
            right_window_num, right_window_locate,
            left_window_num, left_window_locate,
            offside_num, work_path_output
            ],
            outputs=[generate_scheme_btn]
        )
        window_width_input.change(
            check_inputs,
            inputs=[
            cabin_length_input, window_width_input,
            right_window_num, right_window_locate,
            left_window_num, left_window_locate,
            offside_num, work_path_output
            ],
            outputs=[generate_scheme_btn]
        )
        right_window_num.change(
            check_inputs,
            inputs=[
            cabin_length_input, window_width_input,
            right_window_num, right_window_locate,
            left_window_num, left_window_locate,
            offside_num, work_path_output
            ],
            outputs=[generate_scheme_btn]
        )
        right_window_locate.change(
            check_inputs,
            inputs=[
            cabin_length_input, window_width_input,
            right_window_num, right_window_locate,
            left_window_num, left_window_locate,
            offside_num, work_path_output
            ],
            outputs=[generate_scheme_btn]
        )
        left_window_num.change(
            check_inputs,
            inputs=[
            cabin_length_input, window_width_input,
            right_window_num, right_window_locate,
            left_window_num, left_window_locate,
            offside_num, work_path_output
            ],
            outputs=[generate_scheme_btn]
        )
        left_window_locate.change(
            check_inputs,
            inputs=[
            cabin_length_input, window_width_input,
            right_window_num, right_window_locate,
            left_window_num, left_window_locate,
            offside_num, work_path_output
            ],
            outputs=[generate_scheme_btn]
        )
        offside_num.change(
            check_inputs,
            inputs=[
            cabin_length_input, window_width_input,
            right_window_num, right_window_locate,
            left_window_num, left_window_locate,
            offside_num, work_path_output
            ],
            outputs=[generate_scheme_btn]
        )
        work_path_output.change(
            check_inputs,
            inputs=[
            cabin_length_input, window_width_input,
            right_window_num, right_window_locate,
            left_window_num, left_window_locate,
            offside_num, work_path_output
            ],
            outputs=[generate_scheme_btn]
        )
    with gr.Row():
        with gr.Column():
            
            gr.Markdown("### 生成过程日志")
            process_output = gr.Textbox(label="生成进度信息", lines=5, interactive=False, elem_id="process-output")

        with gr.Column():
            gr.Markdown("### 生成模型结果")
            result_output = gr.Textbox(label="生成模型信息", lines=10, interactive=False, elem_id="result-output")

            def on_generate_scheme_click(content, 
                                        cabin_length_input, window_width_input,
                                        right_window_num, right_window_locate,
                                        left_window_num, left_window_locate,
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
                content_data["window"]["right"]["num"] = int(right_window_num) if right_window_num else content_data["window"]["right"].get("num")
                if right_window_locate:
                    if ',' in str(right_window_locate):
                        content_data["window"]["right"]["locate"] = [int(x.strip()) for x in str(right_window_locate).split(',') if x.strip()]
                    else:
                        content_data["window"]["right"]["locate"] = int(right_window_locate)
                else:
                    content_data["window"]["right"]["locate"] = content_data["window"]["right"].get("locate")
                if "left" not in content_data["window"]:
                    content_data["window"]["left"] = {}
                content_data["window"]["left"]["num"] = int(left_window_num) if left_window_num else content_data["window"]["left"].get("num")
                if left_window_locate:
                    if ',' in str(left_window_locate):
                        content_data["window"]["left"]["locate"] = [int(x.strip()) for x in str(left_window_locate).split(',') if x.strip()]
                    else:
                        content_data["window"]["left"]["locate"] = int(left_window_locate)
                else:
                    content_data["window"]["left"]["locate"] = content_data["window"]["left"].get("locate")
                if "offside" not in content_data["window"]:
                    content_data["window"]["offside"] = {}
                content_data["window"]["offside"]["num"] = int(offside_num) if offside_num else content_data["window"]["offside"].get("num")

                a = i.PartsIterator(content_data, work_path_output)
                final_df = a.run()
                print(final_df)
                print(a.over_limit_df)

                # 合并final_df和a.over_limit_df为一个内容字符串
                result = ""
                if final_df is not None:
                    result += "【设计结果】\n"
                    result += str(final_df) + "\n"
                if a.over_limit_df is not None and not (isinstance(a.over_limit_df, str) and not a.over_limit_df.strip()):
                    result += "【超限信息】\n"
                    result += str(a.over_limit_df)
                return result
                # return final_df, a.over_limit_df
                # yield final_df, a.over_limit_df

            generate_scheme_btn.click(
                on_generate_scheme_click,
                inputs=[require_resp, 
                        cabin_length_input, window_width_input,
                        right_window_num, right_window_locate,
                        left_window_num, left_window_locate,
                        offside_num, work_path_output],
                outputs=[result_output]
            )

# demo.launch()
demo.launch(server_name='0.0.0.0', server_port=7860, share=True)

