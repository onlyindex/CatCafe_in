# friend list
from app import app

'''点击朋友列表的头像链接到个人资料页'''
@app.route('/friend')
def show_friend_list():
    return 'friend list'