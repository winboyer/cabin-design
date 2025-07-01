import requests
from openai import OpenAI
import json

openai_api_key = "NONE" 
openai_api_base = "http://10.11.205.10:8000/v1"  # 替换为你的vllm部署的DeepSeek API地址

client = OpenAI(api_key=openai_api_key, base_url=openai_api_base)

models = client.models.list()
model_id = models.data[0].id if models.data else None

content_str = "你好，请你生成一个舱体长度为12m,窗户宽度为1.25m，舱体右侧开2扇窗户，位置为2，3，舱体是左侧开2扇窗户，位置为1，2，的3D结构模型。"

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
# 构造一个template，指导模型将content_str转换为params格式的JSON
template = (
    "请将下面的内容转换为JSON格式，字段包括舱体长度和窗户信息（包含窗户宽、舱体右侧窗户、舱体左侧窗户、偏置等子字段），"
    "确保输出的JSON结构与示例一致，只输出JSON，不要添加其他内容。\n"
    "示例：\n"
    f"{params}\n"
    "内容：\n"
    f"{content_str}\n"
    "请输出对应的JSON："
)
print("Prompt template:\n", template)

messages = [
    {"role": "user", "content": template}
]
# response = client.chat.completions.create(
#     model=model_id, messages=messages, max_tokens=128, temperature=0.7)
response = client.chat.completions.create(
    model=model_id, messages=messages, temperature=0.7)

content = response.choices[0].message.content if response.choices else "No response"
print("Model response:", content)

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

try:
    json_data = json.loads(content)
    converted = convert_keys(json_data)
    print("Converted params:", converted)
except Exception as e:
    print("Failed to parse or convert content:", e)


# params = {
#     "cabin_length": 12000.0,
#     "window": {
#         "width": 1250.0,
#         "right": {
#             "num": 1,
#             "locate": 2
#         },
#         "left": {
#             "num": 1,
#             "locate": 2
#         },
#         "offside": {
#             "num": 2
#         }
#     }
# }

