from flask import Blueprint


admin_bp = Blueprint('admin', __name__, url_prefix='admin')
# 项目超级大多人协作不同模块每个模块下都包含/static/ 比如/admin/static_admin/
# static_folder='static_admin'  访问static_admin目录下的静态文件
# static_url_path='/lib'  将为 static_admin 文件夹的路由设置为 /lib
# template_folder='templates' 每个模块下都包含/templates/


@admin_bp.route('/admin')
def admin():
    return 'admin'
