# 错误程序处理
# 导入蓝本 main

from flask import render_template
from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

@main.app_errorhandler(403)
def internal_server_error(e):
    return render_template('403.html'),403

# 全局错误使用@ app_error()


# bad request 400 请求无效
# 302 重定向 redirect('https://www.catcafe.in')