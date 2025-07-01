import os
# 获取逻辑处理器数量
logical_cores = os.cpu_count()
print(f"逻辑处理器数量: {logical_cores}")  # 例如：8（超线程下可能是物理核心的2倍）