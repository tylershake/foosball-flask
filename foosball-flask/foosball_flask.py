"""Foosball TrueSkill Server

This server ranks foosball players and teams using the TrueSkill ranking
algorithm.

"""

import flask
#import flask_mysql

FOOSBALL_APP = flask.Flask(__name__, static_folder='./utils/static',
    template_folder='./utils/templates')
#FOOSBALL_MYSQL = flask_mysql.MySQL(FOOSBALL_APP)

#FOOSBALL_APP.config.update(dict(
#    SECRET_KEY='development key',
#    USERNAME='admin',
#    PASSWORD='default'
#))

@FOOSBALL_APP.route('/')
def index_redirect():
    """docstring"""

    return flask.render_template('dashboard.html')

@FOOSBALL_APP.route('/index.html')
def index():
    """docstring"""

    return flask.render_template('dashboard.html')

@FOOSBALL_APP.route('/result.html')
def result():
    """docstring"""

    return flask.render_template('result.html')

#@FOOSBALL_APP.route('/login', methods=['GET', 'POST'])
#def login():
#    """docstring"""
#    error = None
#    if flask.request.method == 'POST':
#        if flask.request.form['username'] != FOOSBALL_APP.config['USERNAME']:
#            error = 'Invalid username'
#        elif flask.request.form['password'] != FOOSBALL_APP.config['PASSWORD']:
#            error = 'Invalid password'
#        else:
#            flask.session['logged_in'] = True
#            flask.flash('You were logged in')
#            return flask.redirect(flask.url_for('show_entries'))
#    return flask.render_template('login.html', error=error)

#@FOOSBALL_APP.route('/logout')
#def logout():
#    """docstring"""
#    flask.session.pop('logged_in', None)
#    flask.flash('You were logged out')
#    return flask.redirect(flask.url_for('show_entries'))

def main():
    """docstring"""

    FOOSBALL_APP.run(port=11111)

if __name__ == '__main__':
    main()
