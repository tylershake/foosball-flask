"""Foosball TrueSkill Server

This server ranks foosball players and teams using the TrueSkill ranking
algorithm.

"""

import flask
import logging
import logging.config
from pprint import pprint
import traceback
import sys
import time
import plotly
import plotly.graph_objs

import utils.data_manager as data_manager
import utils.data_manager_exceptions as data_manager_exceptions
import utils.foosball_exceptions as foosball_exceptions

try:
    logging.config.fileConfig("./foosball-flask/utils/logging.conf",
        disable_existing_loggers=False)
except IOError:
    traceback.print_exc()
    sys.exit("Aborting. Unable to find foosball log config")
else:
    pass

FOOSBALL_APP = flask.Flask(__name__, static_folder='./utils/static',
    template_folder='./utils/templates')


#FOOSBALL_APP.config['DEBUG'] = True

MYSQL_STARTUP = 10
time.sleep(MYSQL_STARTUP)

FOOSBALL_DATA = data_manager.DataManager(db_user='foosball',
    db_pass='foosball', db_host='db_1', db_name='foosball')

@FOOSBALL_APP.route('/')
def index_redirect():
    """Main entry point to webpage

    Args:
        None

    Returns:
        display dashboard

    """

    player_count = FOOSBALL_DATA.get_total_players()
    team_count = FOOSBALL_DATA.get_total_teams()
    result_count = FOOSBALL_DATA.get_total_results()
    individual_ranks = FOOSBALL_DATA.get_individual_rankings()
    individual_ranks = sorted(individual_ranks, key=lambda tup: tup[4],
        reverse=True)
    team_ranks = FOOSBALL_DATA.get_team_rankings()
    team_ranks = sorted(team_ranks, key=lambda tup: tup[1],
        reverse=True)

    return flask.render_template('dashboard.html', player_count=player_count,
        team_count=team_count, result_count=result_count,
        individual_ranks=individual_ranks, team_ranks=team_ranks)

@FOOSBALL_APP.route('/index')
def index():
    """Dashboard webpage

    Args:
        None

    Returns:
        display dashboard

    """

    player_count = FOOSBALL_DATA.get_total_players()
    team_count = FOOSBALL_DATA.get_total_teams()
    result_count = FOOSBALL_DATA.get_total_results()
    individual_ranks = FOOSBALL_DATA.get_individual_rankings()
    individual_ranks = sorted(individual_ranks, key=lambda tup: tup[4],
        reverse=True)
    team_ranks = FOOSBALL_DATA.get_team_rankings()
    team_ranks = sorted(team_ranks, key=lambda tup: tup[1],
        reverse=True)

    return flask.render_template('dashboard.html', player_count=player_count,
        team_count=team_count, result_count=result_count,
        individual_ranks=individual_ranks, team_ranks=team_ranks)

@FOOSBALL_APP.route('/result')
def result():
    """Results webpage

    Args:
        None

    Returns:
        display results

    """

    results = FOOSBALL_DATA.get_all_results(100)

    return flask.render_template('result.html', results=results)

@FOOSBALL_APP.route('/player')
def player():
    """Players webpage

    Args:
        None

    Returns:
        display players

    """

    players = FOOSBALL_DATA.get_all_players()

    return flask.render_template('player.html', players=players)

@FOOSBALL_APP.route('/team')
def team():
    """Team webpage

    Args:
        None

    Returns:
        display teams

    """

    teams = FOOSBALL_DATA.get_all_teams()

    return flask.render_template('team.html', teams=teams)

@FOOSBALL_APP.route('/addteam', methods=['GET', 'POST'])
def add_team():
    """Add Team webpage

    Args:
        team_name (str):    team name
        member_one (tup):   first team member
        member_two (tup):   second team member

    Returns:
        display add team
        display team

    Raises:
        foosball_exceptions.HTTPError

    """

    players = FOOSBALL_DATA.get_all_players()

    if flask.request.method == 'POST':
        team_name = flask.request.form['team_name'].encode('utf-8')
        member_one = flask.request.form['member_one'].encode('utf-8')
        member_two = flask.request.form['member_two'].encode('utf-8')

        first_quote = member_one.find('"')
        second_quote = member_one.find('"', first_quote + 1)
        final_member_one = (member_one[:first_quote - 1],
            member_one[second_quote + 2:],
            member_one[first_quote + 1:second_quote])

        first_quote = member_two.find('"')
        second_quote = member_two.find('"', first_quote + 1)
        final_member_two = (member_two[:first_quote - 1],
            member_two[second_quote + 2:],
            member_two[first_quote + 1:second_quote])

        try:
            FOOSBALL_DATA.add_team(team_name=team_name,
                member_one=final_member_one, member_two=final_member_two)
            FOOSBALL_DATA.commit_data()
        except data_manager_exceptions.DBValueError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('addteam.html', error=error,
                players=players)
        except data_manager_exceptions.DBSyntaxError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('addteam.html', error=error,
                players=players)
        except data_manager_exceptions.DBConnectionError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('addteam.html', error=error,
                players=players)
        except data_manager_exceptions.DBExistError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('addteam.html', error=error,
                players=players)
        else:
            pass

        message = 'Team successfully added'
        teams = FOOSBALL_DATA.get_all_teams()
        return flask.render_template('team.html', message=message,
            teams=teams)
    elif flask.request.method == 'GET':
        return flask.render_template('addteam.html', players=players)
    else:
        raise foosball_exceptions.HTTPError("Received unrecognized HTTP method")

@FOOSBALL_APP.route('/addplayer', methods=['GET', 'POST'])
def add_player():
    """Add Player webpage

    Args:
        first_name (str):   player first name
        last_name (str):    player last name
        nickname (str):     player nickname

    Returns:
        display add player
        display player

    Raises:
        foosball_exceptions.HTTPError

    """

    if flask.request.method == 'POST':
        first_name = flask.request.form['first_name'].encode('utf-8')
        last_name = flask.request.form['last_name'].encode('utf-8')
        nickname = flask.request.form['nickname'].encode('utf-8')

        try:
            FOOSBALL_DATA.add_player(first_name=first_name,
                last_name=last_name, nickname=nickname)
            FOOSBALL_DATA.commit_data()
        except data_manager_exceptions.DBValueError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('addplayer.html', error=error)
        except data_manager_exceptions.DBSyntaxError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('addplayer.html', error=error)
        except data_manager_exceptions.DBConnectionError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('addplayer.html', error=error)
        except data_manager_exceptions.DBExistError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('addplayer.html', error=error)
        else:
            pass

        message = 'Player successfully added'
        players = FOOSBALL_DATA.get_all_players()
        return flask.render_template('player.html', message=message,
            players=players)
    elif flask.request.method == 'GET':
        return flask.render_template('addplayer.html')
    else:
        raise foosball_exceptions.HTTPError("Received unrecognized HTTP method")


@FOOSBALL_APP.route('/editplayer', methods=['GET', 'POST'])
def edit_player():
    """Edit an existing player name"""
    players = FOOSBALL_DATA.get_all_players()
    data_manager.LOGGER.info(flask.request.method)
    if flask.request.method == 'POST':
        data_manager.LOGGER.info(flask.request.form)
        previous_player = flask.request.form['previous_player'].encode('utf-8')

        first_quote = previous_player.find('"')
        second_quote = previous_player.find('"', first_quote + 1)
        previous_player = (previous_player[:first_quote - 1],
            previous_player[second_quote + 2:],
            previous_player[first_quote + 1:second_quote])

        # first_name = flask.request.form['first_name'].encode('utf-8')
        # last_name = flask.request.form['last_name'].encode('utf-8')
        # nickname = flask.request.form['nickname'].encode('utf-8')
        previous_player = {'previous_first_name': previous_player[0],
                           'previous_last_name': previous_player[1],
                           'previous_nickname': previous_player[2]}
        new = {'first_name': flask.request.form['first_name'].encode('utf-8'),
               'last_name': flask.request.form['last_name'].encode('utf-8'),
               'nickname': flask.request.form['nickname'].encode('utf-8')}
        #new = (first_name, last_name, nickname)
        data_manager.LOGGER.info(previous_player)
        data_manager.LOGGER.info(new)
        try:
            FOOSBALL_DATA.edit_player(previous_player, new)

            FOOSBALL_DATA.commit_data()
        except data_manager_exceptions.DBValueError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('editplayer.html', error=error)
        except data_manager_exceptions.DBSyntaxError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('editplayer.html', error=error)
        except data_manager_exceptions.DBConnectionError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('editplayer.html', error=error)
        except data_manager_exceptions.DBExistError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('editplayer.html', error=error)
        else:
            pass

        message = 'Player successfully edited'
        players = FOOSBALL_DATA.get_all_players()
        return flask.render_template('editplayer.html', message=message,
            players=players)
    elif flask.request.method == 'GET':
        return flask.render_template('editplayer.html', players=players)
    else:
        raise foosball_exceptions.HTTPError("Received unrecognized HTTP method")



@FOOSBALL_APP.route('/delplayer', methods=['GET'])
def del_player():
    """Delete player webpage

    Args:
        first_name (str):   player first name
        last_name (str):    player last name
        nickname (str):     player nickname

    Returns:
        display player

    Raises:
        foosball_exceptions.HTTPError

    """

    if flask.request.method == 'GET':
        first_name = flask.request.args.get('first_name').encode('utf-8')
        last_name = flask.request.args.get('last_name').encode('utf-8')
        nickname = flask.request.args.get('nickname').encode('utf-8')

        try:
            FOOSBALL_DATA.delete_player(first_name=first_name,
                last_name=last_name, nickname=nickname)
            FOOSBALL_DATA.commit_data()
        except data_manager_exceptions.DBValueError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('player.html', error=error)
        except data_manager_exceptions.DBSyntaxError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('player.html', error=error)
        except data_manager_exceptions.DBConnectionError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('player.html', error=error)
        except data_manager_exceptions.DBExistError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('player.html', error=error)
        else:
            pass

        message = 'Player successfully deleted'
        players = FOOSBALL_DATA.get_all_players()
        return flask.render_template('player.html', message=message,
            players=players)

    else:
        raise foosball_exceptions.HTTPError("Received unrecognized HTTP method")

@FOOSBALL_APP.route('/addresult', methods=['GET', 'POST'])
def add_result():
    """Add Result webpage

    Args:
        offense_winner(tup):    offense_winner
        defense_winner (tup):   defense_winner
        offense_loser (tup):    offense_loser
        defense_loser (tup):    defense_loser

    Returns:
        display add result
        display result

    Raises:
        foosball_exceptions.HTTPError

    """

    players = FOOSBALL_DATA.get_all_players()

    if flask.request.method == 'POST':
        offense_winner = flask.request.form['offense_winner'].encode('utf-8')
        offense_loser = flask.request.form['offense_loser'].encode('utf-8')
        defense_winner = flask.request.form['defense_winner'].encode('utf-8')
        defense_loser = flask.request.form['defense_loser'].encode('utf-8')

        first_quote = offense_winner.find('"')
        second_quote = offense_winner.find('"', first_quote + 1)
        final_offense_winner = (offense_winner[:first_quote - 1],
            offense_winner[second_quote + 2:],
            offense_winner[first_quote + 1:second_quote])

        first_quote = offense_loser.find('"')
        second_quote = offense_loser.find('"', first_quote + 1)
        final_offense_loser = (offense_loser[:first_quote - 1],
            offense_loser[second_quote + 2:],
            offense_loser[first_quote + 1:second_quote])

        first_quote = defense_winner.find('"')
        second_quote = defense_winner.find('"', first_quote + 1)
        final_defense_winner = (defense_winner[:first_quote - 1],
            defense_winner[second_quote + 2:],
            defense_winner[first_quote + 1:second_quote])

        first_quote = defense_loser.find('"')
        second_quote = defense_loser.find('"', first_quote + 1)
        final_defense_loser = (defense_loser[:first_quote - 1],
            defense_loser[second_quote + 2:],
            defense_loser[first_quote + 1:second_quote])

        try:
            FOOSBALL_DATA.add_result(offense_winner=final_offense_winner,
                defense_winner=final_defense_winner,
                offense_loser=final_offense_loser,
                defense_loser=final_defense_loser)
            FOOSBALL_DATA.commit_data()
        except data_manager_exceptions.DBValueError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('addresult.html', error=error,
                players=players)
        except data_manager_exceptions.DBSyntaxError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('addresult.html', error=error,
                players=players)
        except data_manager_exceptions.DBConnectionError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('addresult.html', error=error,
                players=players)
        except data_manager_exceptions.DBExistError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('addresult.html', error=error,
                players=players)
        else:
            pass

        message = 'Result successfully added'
        results = FOOSBALL_DATA.get_all_results(100)
        return flask.render_template('result.html', message=message,
            results=results)
    elif flask.request.method == 'GET':
        return flask.render_template('addresult.html', players=players)
    else:
        raise foosball_exceptions.HTTPError("Received unrecognized HTTP method")

@FOOSBALL_APP.route('/teamstat')
def team_stat():
    """Team Stat webpage

    Args:
        None

    Returns:
        display dashboard

    """

    player_count = FOOSBALL_DATA.get_total_players()
    team_count = FOOSBALL_DATA.get_total_teams()
    result_count = FOOSBALL_DATA.get_total_results()
    individual_ranks = FOOSBALL_DATA.get_individual_rankings()
    individual_ranks = sorted(individual_ranks, key=lambda tup: tup[4],
        reverse=True)
    team_ranks = FOOSBALL_DATA.get_team_rankings()
    team_ranks = sorted(team_ranks, key=lambda tup: tup[1],
        reverse=True)

    return flask.render_template('dashboard.html', player_count=player_count,
        team_count=team_count, result_count=result_count,
        individual_ranks=individual_ranks, team_ranks=team_ranks)

@FOOSBALL_APP.route('/playerstat', methods=['GET', 'POST'])
def player_stat():
    """Player Stat webpage

    Args:
        None

    Returns:
        display dashboard

    """

    players = FOOSBALL_DATA.get_all_players()
    results = FOOSBALL_DATA.get_all_results(100)

    if flask.request.method == 'POST':
        selected_player = flask.request.form['player'].encode('utf-8')
        selected_position = flask.request.form['position'].encode('utf-8')

        first_quote = selected_player.find('"')
        second_quote = selected_player.find('"', first_quote + 1)
        final_player = (selected_player[:first_quote - 1],
            selected_player[second_quote + 2:],
            selected_player[first_quote + 1:second_quote])

        try:
            individual_results = FOOSBALL_DATA.get_individual_results(
                player=final_player, position=selected_position)
            rank_history = FOOSBALL_DATA.get_player_rankings_hist(
                player=final_player, position=selected_position)
        except data_manager_exceptions.DBValueError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('playerstat.html', error=error,
                players=players, results=results)
        except data_manager_exceptions.DBSyntaxError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('playerstat.html', error=error,
                players=players, results=results)
        except data_manager_exceptions.DBConnectionError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('playerstat.html', error=error,
                players=players, results=results)
        except data_manager_exceptions.DBExistError as error:
            data_manager.LOGGER.error(error.msg)
            return flask.render_template('playerstat.html', error=error,
                players=players, results=results)
        else:
            pass

        # generate plotly temp graph to pass to template

        time_data = []
        rank_data = []
        for rating, date in rank_history:
            time_data.append(date)
            rank_data.append(rating * 100)

        trace_one = plotly.graph_objs.Scatter(
            x=time_data,
            y=rank_data,
            mode='lines',
            name='Rating')
        #trace_two = plotly.graph_objs.Scatter(
        #    x=self.analytic_obj.get_concatenated_time_data(),
        #    y=self.analytic_obj.get_concatenated_imag_data(),
        #    mode='lines',
        #    name='Q')
        data = [trace_one]
        layout = {
            'title': "RatingvsTime",
            'xaxis': {
                'title': "Time",
            },
            'yaxis': {
                'title': "Rating",
            },
        }
        figure = {
            'data': data,
            'layout': layout,
        }
        plotly.offline.plot(figure, filename="./temp.html",
                auto_open=False)
        with open('./temp.html', 'r') as myfile:
            data = myfile.read().replace('\n', '')

        first_body = data.find("<body>")
        first_body = first_body + 6
        data = data[first_body:]
        last_body = data.find("</body>")
        data = data[:last_body]

        return flask.render_template('playerstat.html',
            results=individual_results,
            players=players,
            rank_history=data)
    elif flask.request.method == 'GET':
        return flask.render_template('playerstat.html', results=results,
            players=players, rank_history=None)
    else:
        raise foosball_exceptions.HTTPError("Received unrecognized HTTP method")

def main():
    """Main entry point

    Args:
        None

    Returns:
        None

    """

    FOOSBALL_APP.run(port=11111, host='0.0.0.0')

if __name__ == '__main__':
    main()
