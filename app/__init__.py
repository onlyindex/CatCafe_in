import os

from flask import Flask


def create_app(test_config=None):
    # 创建 app
    app = Flask(__name__, instance_relative_config=True)
    # 配置 app
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite')

    )
    # 重新加载 app 配置
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(
            test_config
        )
    # 确保实例文件存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

