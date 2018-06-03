from flask import Flask, request


# 初始化一个flask对象(程序实例),传递一个参数__name__
app = Flask(__name__)

# # 方便flask框架寻找资源'/'
# # 方便flask初见比如flask-Sql alchemy出现错误好定位问题
# # 装饰器url与视图的映射(路由):192.168.1.5000/,请求index函数,结果返回浏览器
# # index view function 视图函数:字符串 or 复杂表单
# # Python嵌入字符串导致代码难以维护?
# # 修饰器修改函数行为把函数注册为事件处理程序


@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    return '<h1>Hello!<h1><br><p>Your browser is %s</p>' % user_agent


# 动态路由_(:з」∠)_
@app.route('/user/<name>')
def show_myself(name):
    return '<h2>Hello,my name is , %s!<h2>' % name


# %s 占位符动态输入内容


@app.route('/user/<user_id>')
def show_user_id(user_id):
    return '<h3>Hello,your id is %s!<he3>' % user_id


# 路由只匹配动态片段id为整数的URL

@app.route("/wb/<uuid>")
def show_twitter(uuid):
    return "twitter context from %s" % uuid


@app.route('/article/<article_id>')
def article(article_id):
    return '你传递的参数是%s' % article_id


# "wb context from" + uuid

# 如当前文件为入口程序运行,那就执行app.run
# 启动web应用服务器,接受用户请求
if __name__ == '__main__':
    app.run()
# flask提供的web服务器不适合生产环境

# while True listen()
# debug=True 调试模式激活调试器
# 程序出现错误,可以在页面看到错误信息和出错位置
# 只需要修改了项目中的Python文件,程序会自动加载,不需要重新启动服务器
