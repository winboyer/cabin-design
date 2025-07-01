import gradio as gr
from docx import Document
from PIL import Image
import io


def read_docx_with_images(file):
    if file is None:
        return ""
    doc = Document(file.name)

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

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=2):
            file_input = gr.File(label="上传docx文件", file_types=[".docx"])
            docx_content = gr.Textbox(label="内容", lines=20, interactive=False)
            images_output = gr.Gallery(label="图片", show_label=True, elem_id="docx-images")

            file_input.change(read_docx_with_images, inputs=file_input, outputs=[docx_content, images_output])

if __name__ == "__main__":
    # demo.launch()
    demo.launch(server_name='0.0.0.0', server_port=7860, share=True)