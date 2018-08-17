from flask import Flask, url_for, request, render_template, make_response
from datetime import datetime

from app.main import RegistrationForm

app = Flask(__name__)


# index
@app.route('/')
def index():
    # 创建响应对象设置 cookie
    # 加入 datetime 变量
    response = make_response('this decumnet carries a cookies')
    response.setcookie('answer', '42')
    return render_template('index.html',current_time=datetime.utcnow()), response


# locus list
@app.route('/locus')
def show_locus_list():
    return 'locus list'


# locus by id
@app.route('/locus/<int:l_id>')
def show_locus(l_id):
    return 'locus %d' % l_id


# message
@app.route('/message')
def message():
    return 'message list'


# friend list
@app.route('/friend')
def show_friend_list():
    return 'friend list'


# tag  list
@app.route('/tag/<tag_name>')
def show_tag_list(tag_name):
    return '%s' % tag_name


# support catcafe in
@app.route('/koorukooru')
def koorukooru():
    return 'koorukooru 花点钱要办茶会买猫买猫粮'


# resume
@app.route('/resume')
def resume():
    return 'resume'


# about me
@app.route('/ore')
def oreore():
    return 'ore ha cat~~o( =∩ω∩= )m'


# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return 'do_the_login()'
    else:
        return 'show_the_login_form()'


# sign up
@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.email.data,
                    form.password.data)
        db_session.add(user)
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

# user
@app.route('/user/<username>')
def profile(username):
    return render_template('user.html', name=username)
# '{}\'s profile'.format(username)


with app.test_request_context():
    print(url_for('index'))
    print(url_for('login'))
    print(url_for('login', next='/'))
    print(url_for('profile', username='John Doe'))

