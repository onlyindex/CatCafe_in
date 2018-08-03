# 创建蓝本
from flask import Blueprint


main = Blueprint('main', __name__)

from . import views, errors
# 模块在末尾导入为了避免循环依赖??不懂

