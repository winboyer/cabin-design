import gradio as gr

with gr.Blocks() as demo:
    with gr.Row():
        # 左侧列：对话框
        with gr.Column(scale=1):
            chatbot = gr.Chatbot(label="对话框", height=600)
            msg = gr.Textbox(label="输入消息")
            send_btn = gr.Button("发送")

            def respond(message, history):
                history = history or []
                history.append((message, "收到: " + message))
                return "", history

            send_btn.click(respond, [msg, chatbot], [msg, chatbot])

        # 右侧列：3行，第二行再分2列
        with gr.Column(scale=1):
            with gr.Row():
                window_width_input = gr.Number(label="窗户宽度 (mm)", value=None)
            with gr.Row():
                with gr.Column():
                    left_window_num = gr.Number(label="舱体左侧窗户个数", value=None)
                with gr.Column():
                    left_window_locate = gr.Textbox(label="舱体左侧窗户位置", value=None)
            with gr.Row():
                with gr.Column():
                    right_window_num = gr.Number(label="舱体右侧窗户个数", value=None)
                with gr.Column():
                    right_window_locate = gr.Textbox(label="舱体右侧窗户位置", value=None)

            with gr.Row():
                query_btn = gr.Button("查询")
                def print_window_locations(left_locate, right_locate):
                    print("左侧窗户位置:", left_locate)
                    print("右侧窗户位置:", right_locate)

                query_btn.click(
                    print_window_locations,
                    [left_window_locate, right_window_locate],
                    []
                )
if __name__ == "__main__":
    # demo.launch()
    demo.launch(server_name='0.0.0.0', server_port=7860, share=True)