# tag  list
from app import app


@app.route('/tag/<tag_name>')
def show_tag_list(tag_name):
    return '%s' % tag_name