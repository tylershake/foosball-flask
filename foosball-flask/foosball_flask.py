"""Foosball TrueSkill Server

This server ranks foosball players and teams using the TrueSkill ranking
algorithm.

"""

import flask
import logging
import logging.config
import traceback
import sys
#import flask_mysql

import utils.data_manager as data_manager
import utils.data_manager_exceptions as data_manager_exceptions
import utils.foosball_exceptions as foosball_exceptions

try:
    logging.config.fileConfig("./utils/logging.conf",
        disable_existing_loggers=False)
    LOGGER = logging.getLogger("foosball")
except IOError:
    traceback.print_exc()
    sys.exit("Aborting. Unable to find foosball log config")
else:
    pass

FOOSBALL_APP = flask.Flask(__name__, static_folder='./utils/static',
    template_folder='./utils/templates')
#FOOSBALL_MYSQL = flask_mysql.MySQL(FOOSBALL_APP)

FOOSBALL_APP.config['DEBUG'] = True
#FOOSBALL_APP.config.update(dict(
#    SECRET_KEY='development key',
#    USERNAME='admin',
#    PASSWORD='default'
#))

FOOSBALL_DATA = data_manager.DataManager(db_user='foosball',
    db_pass='foosball', db_host='127.0.0.1', db_name='foosball')

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

@FOOSBALL_APP.route('/player.html')
def player():
    """docstring"""

    return flask.render_template('player.html')

@FOOSBALL_APP.route('/team.html')
def team():
    """docstring"""

    return flask.render_template('team.html')

@FOOSBALL_APP.route('/addteam.html')
def add_team():
    """docstring"""

    return flask.render_template('addteam.html')

@FOOSBALL_APP.route('/addplayer', methods=['GET', 'POST'])
def add_player():
    """docstring"""

    if flask.request.method == 'POST':
        first_name = flask.request.form['first_name']
        last_name = flask.request.form['last_name']
        nickname = flask.request.form['nickname']

        try:
            FOOSBALL_DATA.add_player(first_name=first_name,
                last_name=last_name, nickname=nickname)
        except data_manager_exceptions.DBValueError as error:
            LOGGER.error(error.msg)
            #TODO display warning
        except data_manager_exceptions.DBSyntaxError as error:
            LOGGER.error(error.msg)
            #TODO display warning
        except data_manager_exceptions.DBConnectionError as error:
            LOGGER.error(error.msg)
            #TODO display warning
        except data_manager_exceptions.DBExistError as error:
            LOGGER.error(error.msg)
            #TODO display warning
        else:
            pass

        #TODO display success
        return flask.render_template('player.html')
    elif flask.request.method == 'GET':
        return flask.render_template('addplayer.html')
    else:
        raise foosball_exceptions.HTTPError("Received unrecognized HTTP method")

@FOOSBALL_APP.route('/addresult.html')
def add_result():
    """docstring"""

    return flask.render_template('addresult.html')

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

    FOOSBALL_APP.run(port=11111, host='0.0.0.0')

if __name__ == '__main__':
    main()
