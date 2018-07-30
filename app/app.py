from flask import Flask, url_for, request

app = Flask(__name__)


# index
@app.route('/')
def index():
    return 'index page'


# article list
@app.route('/article')
def show_article_list():
    return 'article list '


# article by id
@app.route('/article/<int:a_id>')
def show_article(a_id):
    return 'artilce %d' % a_id


# locus list
@app.route('/locus')
def show_locus_list():
    return 'locus list'


# locus by id
@app.route('/locus/<int:l_id>')
def show_locus(l_id):
    return 'locus %d' % l_id


# friend list
@app.route('/friend')
def show_friend_list():
    return 'friend list'


# tag  list
@app.route('/tag/<tag_name>')
def show_tag_list(tag_name):
    return '%s' % tag_name


# support catcafe in
@app.route('/kooru')
def koorukooru():
    return 'kooru 花点钱要办茶会买猫买猫粮'


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
@app.route('/signup')
def sign_up():
    return 'sign up '


@app.route('/user/<username>')
def profile(username):
    return '{}\'s profile'.format(username)


with app.test_request_context():
    print(url_for('index'))
    print(url_for('login'))
    print(url_for('login', next='/'))
    print(url_for('profile', username='John Doe'))
