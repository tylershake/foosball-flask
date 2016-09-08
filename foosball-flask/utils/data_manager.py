"""Foosball Data Manager

This class handles all data interactions with the database.

"""

import MySQLdb
import logging
import logging.config
import os
import sys
import traceback
import trueskill

import data_manager_exceptions

try:
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
        'logging.conf')
    logging.config.fileConfig(LOG_FILE, disable_existing_loggers=False)
    LOGGER = logging.getLogger("foosball")
except IOError:
    traceback.print_exc()
    sys.exit("Aborting. Unable to find data manager logging config")
else:
    pass

class DataManager(object):
    """DataManager class used to interact with database

    Args:
        db_user (str):  MySQL username
        db_pass (str):  MySQL password
        db_host (str):  MySQL server host address
        db_name (str):  MySQL database name

    Attributes:
        db_conn (obj):  MySQL database connection object

    Raises:
        data_manager_exceptions.DBConnectionError
        data_manager_exceptions.DBSyntaxError

    """

    def __init__(self, db_user, db_pass, db_host, db_name):

        try:
            LOGGER.info("Connecting to MySQL database")
            LOGGER.debug("Connection parameters:\n\
username: {0}\n\
password: {1}\n\
hostname: {2}\n\
database: {3}".format(db_user, db_pass, db_host, db_name))
            self.db_conn = MySQLdb.connect(user=db_user, passwd=db_pass,
                host=db_host, db=db_name)

            cursor = self.db_conn.cursor()

            LOGGER.info("Creating MySQL tables")

            cursor.execute("CREATE TABLE IF NOT EXISTS rating (\
rating_id INT NOT NULL AUTO_INCREMENT,\
mu DECIMAL(6,4) NOT NULL,\
sigma DECIMAL(6,4) NOT NULL,\
time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
PRIMARY KEY (rating_id),\
UNIQUE INDEX rating_id_UNIQUE (rating_id ASC))")

            cursor.execute("CREATE TABLE IF NOT EXISTS player (\
player_id INT NOT NULL AUTO_INCREMENT,\
first_name VARCHAR(45) NOT NULL,\
last_name VARCHAR(45) NOT NULL,\
nickname VARCHAR(45) NULL,\
time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
offense_rating INT NOT NULL,\
defense_rating INT NOT NULL,\
PRIMARY KEY (player_id),\
UNIQUE INDEX player_id_UNIQUE (player_id ASC),\
INDEX offense_rating_idx (offense_rating ASC),\
INDEX defense_rating_idx (defense_rating ASC),\
CONSTRAINT offense_rating \
FOREIGN KEY (offense_rating) \
REFERENCES rating (rating_id) \
ON DELETE NO ACTION \
ON UPDATE NO ACTION,\
CONSTRAINT defense_rating \
FOREIGN KEY (defense_rating) \
REFERENCES rating (rating_id) \
ON DELETE NO ACTION \
ON UPDATE NO ACTION)")

            cursor.execute("CREATE TABLE IF NOT EXISTS team (\
team_id INT NOT NULL AUTO_INCREMENT,\
team_name VARCHAR(75) NOT NULL,\
time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
rating INT NOT NULL,\
PRIMARY KEY (team_id),\
UNIQUE INDEX team_id_UNIQUE (team_id ASC),\
UNIQUE INDEX team_name_UNIQUE (team_name ASC),\
INDEX rating_idx (rating ASC),\
CONSTRAINT rating_1 \
FOREIGN KEY (rating) \
REFERENCES rating (rating_id) \
ON DELETE NO ACTION \
ON UPDATE NO ACTION)")

            cursor.execute("CREATE TABLE IF NOT EXISTS player_team_xref (\
player INT NOT NULL,\
team INT NOT NULL,\
INDEX player_idx (player ASC),\
INDEX team_idx (team ASC),\
CONSTRAINT player \
FOREIGN KEY (player) \
REFERENCES player (player_id) \
ON DELETE NO ACTION \
ON UPDATE NO ACTION,\
CONSTRAINT team \
FOREIGN KEY (team) \
REFERENCES team (team_id) \
ON DELETE NO ACTION \
ON UPDATE NO ACTION)")

            cursor.execute("CREATE TABLE IF NOT EXISTS result (\
result_id INT NOT NULL AUTO_INCREMENT,\
offense_winner INT NOT NULL,\
defense_winner INT NOT NULL,\
offense_loser INT NOT NULL,\
defense_loser INT NOT NULL,\
time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
PRIMARY KEY (result_id),\
UNIQUE INDEX result_id_UNIQUE (result_id ASC),\
INDEX offense_winner_idx (offense_winner ASC),\
INDEX defense_winner_idx (defense_winner ASC),\
INDEX offense_loser_idx (offense_loser ASC),\
INDEX defense_loser_idx (defense_loser ASC),\
CONSTRAINT offense_winner \
FOREIGN KEY (offense_winner) \
REFERENCES player (player_id) \
ON DELETE NO ACTION \
ON UPDATE NO ACTION,\
CONSTRAINT defense_winner \
FOREIGN KEY (defense_winner) \
REFERENCES player (player_id) \
ON DELETE NO ACTION \
ON UPDATE NO ACTION,\
CONSTRAINT offense_loser \
FOREIGN KEY (offense_loser) \
REFERENCES player (player_id) \
ON DELETE NO ACTION \
ON UPDATE NO ACTION,\
CONSTRAINT defense_loser \
FOREIGN KEY (defense_loser) \
REFERENCES player (player_id) \
ON DELETE NO ACTION \
ON UPDATE NO ACTION)")

        except MySQLdb.OperationalError:
            LOGGER.error("MySQL operational error occured")
            traceback.print_exc()
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")

        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL programming error")
            traceback.print_exc()
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")

        else:
            pass

    def check_if_player_exists(self, first_name, last_name, nickname):
        """Method to check if player currently exists in database

        Args:
            first_name (str):   player first name
            last_name(str):     player last name
            nickname (str):     player nickname

        Returns:
            (bool):             True/False if player exists

        Raises:
            data_manager_exceptions.DBConnectionError
            data_manager_exceptions.DBSyntaxError

        """

        try:
            LOGGER.info("Checking if player already exists")
            LOGGER.debug("Player parameters:\n\
first name: {0}\n\
last name: {1}\n\
nickname: {2}".format(first_name, last_name, nickname))

            cursor = self.db_conn.cursor()
            cursor.execute("SELECT first_name, last_name, nickname FROM player")
            players = cursor.fetchall()

            for existing_first_name, existing_last_name, existing_nickname in \
                players:
            
                if (first_name == existing_first_name) and (last_name == 
                    existing_last_name) and (nickname == existing_nickname):
                    return False

        except MySQLdb.OperationalError:
            LOGGER.error("MySQL operational error occured")
            traceback.print_exc()
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")

        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL programming error")
            traceback.print_exc()
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")

        else:
            return True
    def check_if_team_exists(self, team_name):
        """Method to check if team currently exists in database

        Args:
            team_name (str):    team name

        Returns:
            (bool):             True/False if team exists

        Raises:
            data_manager_exceptions.DBConnectionError
            data_manager_exceptions.DBSyntaxError

        """

        try:
            LOGGER.info("Checking if team already exists")
            LOGGER.debug("Team parameters:\nTeam name: {0}".format(team_name))

            cursor = self.db_conn.cursor()
            cursor.execute("SELECT team_name FROM team")
            teams = cursor.fetchall()
            for team in teams:
                if team == team_name:
                    return False

        except MySQLdb.OperationalError:
            LOGGER.error("MySQL operational error occured")
            traceback.print_exc()
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")

        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL programming error")
            traceback.print_exc()
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")

        else:
            return True

    def add_rating(self):
        """Method to add a new rating to the database

        Args:
            None

        Return:
            rating_id (int):    rating_id for rating just created

        Raises:
            data_manager_exceptions.DBConnectionError
            data_manager_exceptions.DBSyntaxError

        """

        try:
            LOGGER.info("Creating new rating")
            new_rating = trueskill.Rating()
            cursor = self.db_conn.cursor()
            cursor.execute("INSERT INTO rating (mu, sigma) VALUES ({0}, {1}\
)".format(new_rating.mu, new_rating.sigma))
            rating_id = cursor.lastrowid

        except MySQLdb.OperationalError:
            LOGGER.error("MySQL operational error occured")
            traceback.print_exc()
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")

        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL programming error")
            traceback.print_exc()
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")

        else:
            return rating_id

    def add_player(self, first_name, last_name, nickname):
        """Method to add a player to the database

        Args:
            first_name (str):   player first name
            last_name(str):     player last name
            nickname (str):     player nickname

        Raises:
            data_manager_exceptions.DBValueError
            data_manager_exceptions.DBExistError
            data_manager_exceptions.DBConnectionError
            data_manager_exceptions.DBSyntaxError

        """

        if len(first_name) is 0:
            raise data_manager_exceptions.DBValueError("First name must be at \
least one character")

        if len(last_name) is 0:
            raise data_manager_exceptions.DBValueError("Last name must be at \
least one character")

        try:
            if not self.check_if_player_exists(first_name=first_name,
                last_name=last_name, nickname=nickname):
                raise data_manager_exceptions.DBExistError("Name already \
exists in database")

            offense_rating_id = self.add_rating()
            defense_rating_id = self.add_rating()

            cursor = self.db_conn.cursor()

            LOGGER.info("Adding player to database")
            cursor.execute("INSERT INTO player (first_name, last_name, \
nickname, offense_rating, defense_rating) VALUES ('{0}', '{1}', '{2}', \
{3}, {4})".format(first_name, last_name, nickname, offense_rating_id,
                defense_rating_id))

        except MySQLdb.OperationalError:
            LOGGER.error("MySQL operational error occured")
            traceback.print_exc()
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")

        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL programming error")
            traceback.print_exc()
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")

        else:
            pass

    def edit_player(self):
        """TODO"""

    def delete_player(self, first_name, last_name, nickname):
        """TODO"""
        """Method to delete a player from the database

        Args:
            first_name (str):   player first name
            last_name(str):     player last name
            nickname (str):     player nickname

        Raises:
            data_manager_exceptions.DBValueError
            data_manager_exceptions.DBExistError
            data_manager_exceptions.DBConnectionError
            data_manager_exceptions.DBSyntaxError

        """

        #TODO check if data exists and don't delete if it does
        #TODO deleting player should also delete a team

        if len(first_name) is 0:
            raise data_manager_exceptions.DBValueError("First name must be at \
least one character")

        if len(last_name) is 0:
            raise data_manager_exceptions.DBValueError("Last name must be at \
least one character")

        try:
            LOGGER.info("Checking that player already exists")
            LOGGER.debug("Player parameters:\n\
first name: {0}\n\
last name: {1}\n\
nickname: {2}".format(first_name, last_name, nickname))
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT player_id, first_name, last_name, \
nickname FROM player")
            players = cursor.fetchall()

            if len(players) is 0:
                raise data_manager_exceptions.DBExistError("No players \
in database to delete")

            for player in players:
                player_id, existing_first_name, existing_last_name, \
                    existing_nickname = player
            
                if (first_name == existing_first_name) and (last_name == 
                    existing_last_name) and (nickname == existing_nickname):
                    LOGGER.info("Deleting player from database")
                    cursor.execute("DELETE FROM player WHERE player_id \
= {0}".format(player_id))
                    return
                else:
                    continue

            raise data_manager_exceptions.DBExistError("Player \
doesn't exist")
        except MySQLdb.OperationalError:
            LOGGER.error("Cannot connect to MySQL server")
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")
        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL syntax error")
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")
        else:
            pass

    def get_all_players(self):
        """Method to get all players from database

        Args:
            None

        Returns:
            players (tup):  tuple of player tuples

        Raises:
            data_manager_exceptions.DBConnectionError
            data_manager_exceptions.DBSyntaxError

        """

        try:
            LOGGER.info("Getting player list")
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT first_name, last_name, nickname FROM player \
ORDER BY time DESC")
            players = cursor.fetchall()

        except MySQLdb.OperationalError:
            LOGGER.error("MySQL operational error occured")
            traceback.print_exc()
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")

        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL programming error")
            traceback.print_exc()
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")

        else:
            return players

    def get_total_players(self):
        """Method to get player count from database

        Args:
            None

        Returns:
            count (int):    count of players

        Raises:
            data_manager_exceptions.DBConnectionError
            data_manager_exceptions.DBSyntaxError

        """

        try:
            LOGGER.info("Getting total player count")
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT COUNT(player_id) FROM player")
            count = cursor.fetchone()[0]

        except MySQLdb.OperationalError:
            LOGGER.error("MySQL operational error occured")
            traceback.print_exc()
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")

        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL programming error")
            traceback.print_exc()
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")

        else:
            return count

    def get_total_teams(self):
        """Method to get team count from database

        Args:
            None

        Return:
            count (int):    total number of teams

        Raises:
            data_manager_exceptions.DBConnectionError
            data_manager_exceptions.DBSyntaxError

        """

        try:
            LOGGER.info("Getting total team count")
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT COUNT(team_id) FROM team")
            count = cursor.fetchone()[0]

        except MySQLdb.OperationalError:
            LOGGER.error("MySQL operational error occured")
            traceback.print_exc()
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")

        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL programming error")
            traceback.print_exc()
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")

        else:
            return count

    def get_all_teams(self):
        """Method to get all teams from database

        Args:
            None

        Returns:
            teams (tup):    tuple of team tuples

        Raises:
            data_manager_exceptions.DBConnectionError
            data_manager_exceptions.DBSyntaxError

        """

        all_teams = ()

        try:
            LOGGER.info("Getting team list")
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT team_id, team_name FROM team ORDER BY \
time DESC")
            teams = cursor.fetchall()

            for team_id, name in teams:
                intermediate_teams = ()
                intermediate_teams = intermediate_teams + (name,)
                cursor.execute("SELECT player FROM player_team_xref WHERE \
team = {0}".format(team_id))
                players = cursor.fetchall()
                if len(players) != 2:
                    raise data_manager_exceptions.DBValueError("Found more \
than two players per team")

                for player in players:
                    cursor.execute("SELECT first_name, last_name, nickname \
FROM player WHERE player_id = {0}".format(player[0]))
                    first_name, last_name, nickname = cursor.fetchall()[0]

                    intermediate_teams = intermediate_teams + (first_name,
                        last_name, nickname)

                all_teams = all_teams + (intermediate_teams,)
                del intermediate_teams

        except MySQLdb.OperationalError:
            LOGGER.error("MySQL operational error occured")
            traceback.print_exc()
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")

        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL programming error")
            traceback.print_exc()
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")

        else:
            return all_teams

    def add_team(self, team_name, member_one, member_two):
        """Method to add a team to database

        Args:
            team_name (str):    team name
            member_one (tup):   first member names
            member_two (tup):   second member names

        Raises:
            data_manager_exceptions.DBValueError
            data_manager_exceptions.DBExistError
            data_manager_exceptions.DBConnectionError
            data_manager_exceptions.DBSyntaxError

        """

        if len(team_name) is 0:
            raise data_manager_exceptions.DBValueError("Team name must be at \
least one character")

        if len(member_one) != 3:
            raise data_manager_exceptions.DBValueError("First team member must\
 be complete")

        if len(member_two) != 3:
            raise data_manager_exceptions.DBValueError("Second team member must\
 be complete")

        try:

            if not self.check_if_team_exists(team_name=team_name):
                raise data_manager_exceptions.DBExistError("Team already \
exists")

            #LOGGER.info("Checking if players are already on team together")
            #TODO

            LOGGER.info("Adding team to database")

            cursor = self.db_conn.cursor()
            cursor.execute("INSERT INTO team (team_name) VALUES \
('{0}')".format(team_name))

            team_id = cursor.lastrowid

            cursor.execute("INSERT INTO player_team_xref (player, team) \
VALUES ((SELECT player_id FROM player WHERE first_name = '{0}' AND last_name \
= '{1}' AND nickname = '{2}'), {3})".format(member_one[0], member_one[1],
                member_one[2], team_id))

            cursor.execute("INSERT INTO player_team_xref (player, team) \
VALUES ((SELECT player_id FROM player WHERE first_name = '{0}' AND last_name \
= '{1}' AND nickname = '{2}'), {3})".format(member_two[0], member_two[1],
                member_two[2], team_id))

        except MySQLdb.OperationalError:
            LOGGER.error("MySQL operational error occured")
            traceback.print_exc()
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")

        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL programming error")
            traceback.print_exc()
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")

        else:
            pass

    def add_result(self, offense_winner, defense_winner, offense_loser,
        defense_loser):
        """Method to add a result to database

        Args:
            offense_winner(tup):    offense_winner
            defense_winner (tup):   defense_winner
            offense_loser (tup):    offense_loser
            defense_loser (tup):    defense_loser

        Raises:
            data_manager_exceptions.DBValueError
            data_manager_exceptions.DBExistError
            data_manager_exceptions.DBConnectionError
            data_manager_exceptions.DBSyntaxError

        """

        if len(offense_winner) != 3:
            raise data_manager_exceptions.DBValueError("Offense winner must\
 be complete")

        if len(defense_winner) != 3:
            raise data_manager_exceptions.DBValueError("Defense winner must\
 be complete")

        if len(offense_loser) != 3:
            raise data_manager_exceptions.DBValueError("Offense loser must\
 be complete")

        if len(defense_loser) != 3:
            raise data_manager_exceptions.DBValueError("Defense loser must\
 be complete")

        try:
            LOGGER.info("Adding result to database")
            cursor = self.db_conn.cursor()
            cursor.execute("INSERT INTO result (offense_winner, \
defense_winner, offense_loser, defense_loser) VALUES ((SELECT \
player_id FROM player WHERE first_name = '{0}' AND last_name \
= '{1}' AND nickname = '{2}'), (SELECT player_id FROM player WHERE first_name \
= '{3}' AND last_name = '{4}' AND nickname = '{5}'), (SELECT player_id FROM \
player WHERE first_name = '{6}' AND last_name = '{7}' AND nickname = '{8}'), \
(SELECT player_id FROM player WHERE first_name = '{9}' AND last_name = '{10}' \
AND nickname = '{11}'))".format(offense_winner[0],
                offense_winner[1], offense_winner[2], defense_winner[0],
                defense_winner[1], defense_winner[2], offense_loser[0],
                offense_loser[1], offense_loser[2], defense_loser[0],
                defense_loser[1], defense_loser[2]))

            LOGGER.info("Updating individual ratings")
            cursor.execute("SELECT player_id, offense_rating FROM player \
WHERE first_name = '{0}' AND last_name = '{1}' AND nickname = '{2}'".format(
                offense_winner[0], offense_winner[1], offense_winner[2]))
            offense_winner_player_id, rating = cursor.fetchall()[0]

            cursor.execute("SELECT mu, sigma FROM rating WHERE rating_id \
= {0}".format(rating))
            mu, sigma = cursor.fetchall()[0]
            offense_winner_rating = trueskill.Rating(mu=float(mu),
                sigma=float(sigma))

            cursor.execute("SELECT player_id, defense_rating FROM player \
WHERE first_name = '{0}' AND last_name = '{1}' AND nickname = '{2}'".format(
                defense_winner[0], defense_winner[1], defense_winner[2]))
            defense_winner_player_id, rating = cursor.fetchall()[0]

            cursor.execute("SELECT mu, sigma FROM rating WHERE rating_id \
= {0}".format(rating))
            mu, sigma = cursor.fetchall()[0]
            defense_winner_rating = trueskill.Rating(mu=float(mu),
                sigma=float(sigma))

            cursor.execute("SELECT player_id, offense_rating FROM player \
WHERE first_name = '{0}' AND last_name = '{1}' AND nickname = '{2}'".format(
                offense_loser[0], offense_loser[1], offense_loser[2]))
            offense_loser_player_id, rating = cursor.fetchall()[0]

            cursor.execute("SELECT mu, sigma FROM rating WHERE rating_id \
= {0}".format(rating))
            mu, sigma = cursor.fetchall()[0]
            offense_loser_rating = trueskill.Rating(mu=float(mu),
                sigma=float(sigma))

            cursor.execute("SELECT player_id, defense_rating FROM player \
WHERE first_name = '{0}' AND last_name = '{1}' AND nickname = '{2}'".format(
                defense_loser[0], defense_loser[1], defense_loser[2]))
            defense_loser_player_id, rating = cursor.fetchall()[0]

            cursor.execute("SELECT mu, sigma FROM rating WHERE rating_id \
= {0}".format(rating))
            mu, sigma = cursor.fetchall()[0]
            defense_loser_rating = trueskill.Rating(mu=float(mu),
                sigma=float(sigma))

            (new_offense_winner_rating, new_defense_winner_rating), \
            (new_offense_loser_rating, new_defense_loser_rating) = \
            trueskill.rate([(offense_winner_rating, defense_winner_rating),
                (offense_loser_rating, defense_loser_rating)], ranks=[0, 1])

            cursor.execute("INSERT INTO rating (mu, sigma) VALUES ({0}, {1}\
)".format(new_offense_winner_rating.mu, new_offense_winner_rating.sigma))
            new_rating_id = cursor.lastrowid
            cursor.execute("UPDATE player set offense_rating = {0} where \
player_id = {1}".format(new_rating_id, offense_winner_player_id))

            cursor.execute("INSERT INTO rating (mu, sigma) VALUES ({0}, {1}\
)".format(new_defense_winner_rating.mu, new_defense_winner_rating.sigma))
            new_rating_id = cursor.lastrowid
            cursor.execute("UPDATE player set defense_rating = {0} where \
player_id = {1}".format(new_rating_id, defense_winner_player_id))

            cursor.execute("INSERT INTO rating (mu, sigma) VALUES ({0}, {1}\
)".format(new_offense_loser_rating.mu, new_offense_loser_rating.sigma))
            new_rating_id = cursor.lastrowid
            cursor.execute("UPDATE player set offense_rating = {0} where \
player_id = {1}".format(new_rating_id, offense_loser_player_id))

            cursor.execute("INSERT INTO rating (mu, sigma) VALUES ({0}, {1}\
)".format(new_defense_loser_rating.mu, new_defense_loser_rating.sigma))
            new_rating_id = cursor.lastrowid
            cursor.execute("UPDATE player set defense_rating = {0} where \
player_id = {1}".format(new_rating_id, defense_loser_player_id))

        except MySQLdb.OperationalError:
            LOGGER.error("MySQL operational error occured")
            traceback.print_exc()
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")

        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL programming error")
            traceback.print_exc()
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")

        else:
            pass

    def get_total_results(self):
        """Method to get result count from database

        Args:
            None

        Returns:
            count (int):    total number of results

        Raises:
            data_manager_exceptions.DBConnectionError
            data_manager_exceptions.DBSyntaxError

        """

        try:
            LOGGER.info("Getting total result count")
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT COUNT(result_id) FROM result")
            count = cursor.fetchone()[0]

        except MySQLdb.OperationalError:
            LOGGER.error("MySQL operational error occured")
            traceback.print_exc()
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")

        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL programming error")
            traceback.print_exc()
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")

        else:
            return count

    def get_all_results(self):
        """Method to get all results from database

        Args:
            None

        Raises:
            data_manager_exceptions.DBConnectionError
            data_manager_exceptions.DBSyntaxError

        """

        all_results = ()

        try:
            LOGGER.info("Getting result list")
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT offense_winner, defense_winner, \
offense_loser, defense_loser FROM result ORDER BY time DESC")
            results = cursor.fetchall()

            for offense_winner_id, defense_winner_id, offense_loser_id, \
                defense_loser_id in results:

                intermediate_results = ()
                cursor.execute("SELECT first_name, last_name, nickname FROM \
player WHERE player_id = {0}".format(offense_winner_id))
                offense_winner = cursor.fetchall()
                first_name_offense_winner, last_name_offense_winner, \
                    nickname_offense_winner = offense_winner[0]

                cursor.execute("SELECT first_name, last_name, nickname FROM \
player WHERE player_id = {0}".format(defense_winner_id))
                defense_winner = cursor.fetchall()
                first_name_defense_winner, last_name_defense_winner, \
                    nickname_defense_winner = defense_winner[0]

                cursor.execute("SELECT first_name, last_name, nickname FROM \
player WHERE player_id = {0}".format(offense_loser_id))
                offense_loser = cursor.fetchall()
                first_name_offense_loser, last_name_offense_loser, \
                    nickname_offense_loser = offense_loser[0]

                cursor.execute("SELECT first_name, last_name, nickname FROM \
player WHERE player_id = {0}".format(defense_loser_id))
                defense_loser = cursor.fetchall()
                first_name_defense_loser, last_name_defense_loser, \
                    nickname_defense_loser = defense_loser[0]

                intermediate_results = intermediate_results + \
                    (first_name_offense_winner, last_name_offense_winner,
                    nickname_offense_winner, first_name_defense_winner,
                    last_name_defense_winner, nickname_defense_winner,
                    first_name_offense_loser, last_name_offense_loser,
                    nickname_offense_loser, first_name_defense_loser,
                    last_name_defense_loser, nickname_defense_loser)

                all_results = all_results + (intermediate_results,)
                del intermediate_results

        except MySQLdb.OperationalError:
            LOGGER.error("MySQL operational error occured")
            traceback.print_exc()
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")

        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL programming error")
            traceback.print_exc()
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")

        else:
            return all_results

    def get_individual_rankings(self):
        """Method to get individual rankings from database

        Args:
            None

        Returns:
            ranks (list):   individual rank list

        Raises:
            data_manager_exceptions.DBConnectionError
            data_manager_exceptions.DBSyntaxError

        """

        ranks = []

        try:
            LOGGER.info("Getting individual rankings")
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT player_id, first_name, last_name, \
nickname FROM player")
            players = cursor.fetchall()

            for player_id, first_name, last_name, nickname in players:
                cursor.execute("SELECT offense_rating, defense_rating FROM \
player WHERE player_id = {0}".format(player_id))
                offense_rating, defense_rating = cursor.fetchall()[0]

                cursor.execute("SELECT mu, sigma FROM rating WHERE rating_id \
= {0}".format(offense_rating))
                offense_mu, offense_sigma = cursor.fetchall()[0]

                cursor.execute("SELECT mu, sigma FROM rating WHERE rating_id \
= {0}".format(defense_rating))
                defense_mu, defense_sigma = cursor.fetchall()[0]

                offense_rank = float(offense_mu) - (3 * float(offense_sigma))
                defense_rank = float(defense_mu) - (3 * float(defense_sigma))

                intermediate_rank = (first_name, last_name, nickname,
                    'Offense', round(offense_rank, 4))
                ranks.append(intermediate_rank)
                del intermediate_rank
                intermediate_rank = (first_name, last_name, nickname,
                    'Defense', round(defense_rank, 4))
                ranks.append(intermediate_rank)
                del intermediate_rank

        except MySQLdb.OperationalError:
            LOGGER.error("MySQL operational error occured")
            traceback.print_exc()
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")

        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL programming error")
            traceback.print_exc()
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")

        else:
            return ranks

    def delete_team(self, team_name):
        """TODO"""

    def delete_result(self, offense_winner, defense_winner, offense_loser, defense_loser, timestamp):
        """TODO"""

    def commit_data(self):
        """Method to save results to database

        Args:
            None

        Returns:
            None

        """

        self.db_conn.commit()

def main():
    """docstring"""

    data_mgr = DataManager(db_user='foosball',
        db_pass='foosball', db_host='127.0.0.1', db_name='foosball')
    #data_mgr.add_player('Hello', 'Weird', 'Person')
    #data_mgr.commit_data()
    #data_mgr.add_player('Buuba', 'Buuba', 'Buuba')
    #data_mgr.add_team(team_name='Shot',
    #    member_one=('Branden', 'Poops', 'Here'),
    #    member_two=('Hello', 'Weird', 'Person'))
    #data_mgr.commit_data()
    ranks = data_mgr.get_individual_rankings()
    sorted_ranks = sorted(ranks, key=lambda tup: tup[4], reverse=True)

    print sorted_ranks

    del data_mgr

if __name__ == '__main__':
    main()
