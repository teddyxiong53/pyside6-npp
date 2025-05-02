# Python示例文件
"""
多行注释
演示语法高亮
"""

from typing import List, Optional
import datetime

# 装饰器示例
def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"调用函数: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

# 类定义
class Animal:
    def __init__(self, name: str):
        self.name = name
    
    def make_sound(self) -> str:
        pass

class Dog(Animal):
    def __init__(self, name: str, age: int):
        super().__init__(name)
        self.age = age
    
    @log_call
    def make_sound(self) -> str:
        return "汪汪!"

# TODO: 添加更多动物类

# 列表推导式
numbers = [1, 2, 3, 4, 5]
squares = [x**2 for x in numbers if x % 2 == 0]

# 字符串格式化
name = "小明"
age = 10
message = f"{name}今年{age}岁"

# 异常处理
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"错误: {e}")
finally:
    print("处理完成")

# 主函数
if __name__ == "__main__":
    dog = Dog("旺财", 3)
    print(dog.make_sound())