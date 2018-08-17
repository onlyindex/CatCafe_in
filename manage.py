# 启动程序脚本
# !/user/bin/env python
import  os
from app import create_app,db
from app.models import User,Role
from flask_script import Manger, Shell
from flask_migrate import Migrate, MigrateCommand

# 创建程序,定义环境变量FLASK_CONFIG读取配置名否则使用默认配置
app=create_app(os.getenv('FLASK_CONFIG')or 'default')

# 初始化 flask-script flask-migrate
manager = Manger(app)
migrate= Migrate(app.db)

# 为 python shell 定义上下文
# make_shell_context() 函数注册了程序、数据库实例以及模型
def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role)
manager.add_command('shell',Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)

if __name__='__main__'
    manager.run()


