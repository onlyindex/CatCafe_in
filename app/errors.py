# 错误程序处理

from flask import render_template, app


# 全局错误使用@app_error()
# app_errorhandler vs errorhandler

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.errorhandler(403)
def internal_server_error(e):
    return render_template('403.html'), 403


@app.errorhandler(400)
def bad_request(e):
    return '400 请求无效', 400


@app.errorhandler(302)
def redirect():
    return redirect('https://www.catcafe.in'), 302


