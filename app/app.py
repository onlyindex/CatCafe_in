from flask import  make_response
from datetime import datetime
from flask import Flask, url_for,  render_template



app = Flask(__name__)


# index
@app.route('/')
def index():
    # 创建响应对象设置 cookie
    # 加入 datetime 变量
    response = make_response('this decumnet carries a cookies')
    response.setcookie('answer', '42')
    return render_template('index.html',current_time=datetime.utcnow()), response


# support catcafe in
@app.route('/koorukooru')
def koorukooru():
    return 'koorukooru 花点钱要办茶会买猫买猫粮'



with app.test_request_context():
    print(url_for('index'))
    print(url_for('login'))
    print(url_for('login', next='/'))
    print(url_for('profile', username='John Doe'))

