# 异常检测
class ParamValidationError(Exception):
    def __init__(self, errors):
        super().__init__("参数校验失败")
        self.errors = errors

    def __str__(self):
        return f"{super().__str__()}，详细错误如下：\n" + "\n".join(self.errors)