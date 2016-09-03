"""Foosball TrueSkill Server

This server ranks foosball players and teams using the TrueSkill ranking
algorithm.

"""

import flask
import flask_mysql

FOOSBALL_APP = flask.Flask(__name__)
FOOSBALL_MYSQL = flask_mysql.MySQL(FOOSBALL_APP)

FOOSBALL_APP.config.update(dict(
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

@FOOSBALL_APP.route('/')
def show_entries():
    """docstring"""

    cursor = FOOSBALL_MYSQL.connection.cursor()
    cursor.execute('''SELECT title, text FROM entries ORDER BY id DESC''')
    entries = cursor.fetchall()
    return flask.render_template('show_entries.html', entries=entries)
