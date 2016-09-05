"""Foosball Data Manager

This class handles all data interactions with the database.

"""

import MySQLdb
import logging
import logging.config
import os
import sys
import traceback

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
username: %s\n\
password: %s\n\
hostname: %s\n\
database: %s", db_user, db_pass, db_host, db_name)
            self.db_conn = MySQLdb.connect(user=db_user, passwd=db_pass,
                host=db_host, db=db_name)

            cursor = self.db_conn.cursor()

            LOGGER.info("Creating player table if it doesn't exist")
            cursor.execute("CREATE TABLE IF NOT EXISTS player (\
player_id INT NOT NULL AUTO_INCREMENT,\
first_name VARCHAR(45) NOT NULL,\
last_name VARCHAR(45) NOT NULL,\
nickname VARCHAR(45) NULL,\
time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
PRIMARY KEY (player_id),\
UNIQUE INDEX player_id_UNIQUE (player_id ASC))")
        except MySQLdb.OperationalError:
            LOGGER.error("Cannot connect to MySQL server")
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")
        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL syntax error")
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")
        else:
            pass

    def add_player(self, first_name, last_name, nickname):
        """Method to add a player to database

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
            LOGGER.info("Checking if player already exists")
            LOGGER.debug("Player parameters:\n\
first name: %s\n\
last name: %s\n\
nickname: %s", first_name, last_name, nickname)
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT first_name, last_name, nickname FROM player")
            players = cursor.fetchall()
            for player in players:
                existing_first_name, existing_last_name, existing_nickname = \
                    player
            
                if (first_name == existing_first_name) and (last_name == 
                    existing_last_name) and (nickname == existing_nickname):
                    raise data_manager_exceptions.DBExistError("Player already \
exists")
        
            LOGGER.info("Adding player to database")
            cursor.execute("INSERT INTO player (first_name, last_name, \
nickname) VALUES (%s, %s, %s)", (first_name, last_name, nickname))
        except MySQLdb.OperationalError:
            LOGGER.error("Cannot connect to MySQL server")
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")
        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL syntax error")
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")
        else:
            pass

    def delete_player(self, first_name, last_name, nickname):
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

        if len(first_name) is 0:
            raise data_manager_exceptions.DBValueError("First name must be at \
least one character")

        if len(last_name) is 0:
            raise data_manager_exceptions.DBValueError("Last name must be at \
least one character")

        try:
            LOGGER.info("Checking that player already exists")
            LOGGER.debug("Player parameters:\n\
first name: %s\n\
last name: %s\n\
nickname: %s", first_name, last_name, nickname)
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
                    cursor.execute("DELETE FROM player WHERE player_id = %s",
                        (player_id, ))
                else:
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
            LOGGER.error("Cannot connect to MySQL server")
            raise data_manager_exceptions.DBConnectionError("Cannot connect \
to MySQL server")
        except MySQLdb.ProgrammingError:
            LOGGER.error("MySQL syntax error")
            raise data_manager_exceptions.DBSyntaxError("MySQL syntax error")
        else:
            pass

        return players

    def add_team(self, team_name, first_member, second_member):
        """docstring"""

        cursor = self.db_conn.cursor()

    def add_result(self, offense_winner, defense_winner, offense_loser, defense_loser):
        """docstring"""

        cursor = self.db_conn.cursor()

    def delete_team(self, team_name):
        """docstring"""

        cursor = self.db_conn.cursor()

    def delete_result(self, offense_winner, defense_winner, offense_loser, defense_loser, timestamp):
        """docstring"""

        cursor = self.db_conn.cursor()

    def total_teams(self):
        """docstring"""

        cursor = self.db_conn.cursor()

    def total_results(self):
        """docstring"""

        cursor = self.db_conn.cursor()


    def commit_data(self):
        """docstring"""

        self.db_conn.commit()

def main():
    """docstring"""

    data_mgr = DataManager('root', '', '127.0.0.1',
        'new_schema')
    data_mgr.add_player('Tyler', 'Tyler', 'Shake')
    data_mgr.commit_data()
    data_mgr.delete_player('Tyler', 'Shake', 'Shake')
    data_mgr.commit_data()
    del data_mgr

if __name__ == '__main__':
    main()
