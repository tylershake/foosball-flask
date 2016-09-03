"""Foosball TrueSkill Server

This server ranks foosball players and teams using the TrueSkill ranking
algorithm.

"""

import flask
#import flask_mysql

FOOSBALL_APP = flask.Flask(__name__)
#FOOSBALL_MYSQL = flask_mysql.MySQL(FOOSBALL_APP)

#FOOSBALL_APP.config.update(dict(
#    SECRET_KEY='development key',
#    USERNAME='admin',
#    PASSWORD='default'
#))

@FOOSBALL_APP.route('/')
def show_entries():
    """docstring"""

#    cursor = FOOSBALL_MYSQL.connection.cursor()
#    cursor.execute('''SELECT title, text FROM entries ORDER BY id DESC''')
#    entries = cursor.fetchall()
#    entries = 'Test Entry'
    return flask.render_template('dashboard.html')

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
