'''仿照 article 自己写 locus 恩恩'''
# locus list
@app.route('/locus')
def show_locus_list():
    return 'locus list'


# locus by id
@app.route('/locus/<int:l_id>')
def show_locus(l_id):
    return 'locus %d' % l_id