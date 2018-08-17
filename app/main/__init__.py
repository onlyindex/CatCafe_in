# 创建蓝本
from flask import Blueprint

main = Blueprint('main', __name__)

from . import errors, views


# 模块在末尾导入为了避免循环依赖??不懂

# 把 Permission 类加入模板上下文
# 为了避免每次调用 render_template() 时都多添加一个模板参数，可以使用上下文处理器
# 上下文处理器能让变量在所有模板中全局可访问
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
