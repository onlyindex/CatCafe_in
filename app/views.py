from flask import session, redirect, url_for, request
from sqlalchemy.sql.functions import current_user


#index・_・? 这个页面全是一些不明觉厉的东西根本不懂

# before_app_request 处理程序在每次请求前运行
# before_request 钩子
# before_app_request 修饰器 在蓝本中使用针对程序全局请求的钩子

# 过滤未确认的账户
@app.before_app_request
def before_request():
    if current_user.is_authenticated()
        and not current_user.confirmed
        and request.endpoint[:5] != 'auth.':
        # 请求的端点(request.endpoint 获取)不在认证蓝本中。
        # 访问认证路由要获取权限，路由的作用是让用户确认账户或执行其他账户管理操作。
        and request.endpoint != 'static':
    return redirect(url_for('auth.unconfirmed'))


# 更新已登录用户的访问时间
@app.before_app_request
def before_request():
    if current_user.is_authenticated():
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))


# 查询session.get('user_id')   g.user=get_db().excute(...,'user_id').fetchone
@app.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
        the database into ``g.user``."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


# 如果 before_request 或 before_app_request 的回调返回响应或重定向，
# Flask 会直接将其发送至客户端，而不会调用请求的视图函数。
# 因此，这些回调可 在必要时拦截请求。

import Permission as Permission
# 把 Permission 类加入模板上下文
# 为了避免每次调用 render_template() 时都多添加一个模板参数，可以使用上下文处理器
# 上下文处理器能让变量在所有模板中全局可访问
@app.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
