# 使用自定义的修饰器,让视图函数只对具有特定权限的用户开放
from functools import wraps
# 这两个修饰器都使用了 Python 标准库中的 functools 包
# 如果用户不具有指定权限，则返 回 403 错误码/页面，即 HTTP“禁止”错误
from flask import abort
from flask.ext.login import current_user
# 检查用户常规权限的自定义修饰器
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorato

# 检查管理员权限。
def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)