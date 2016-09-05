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

        """

        cursor = self.db_conn.cursor()

        #TODO perform checks
        #TODO check if player already exists
        
        cursor.execute("INSERT INTO player (first_name, last_name, nickname) \
VALUES (%s, %s, %s)", (first_name, last_name, nickname))

    def add_team(self, team_name, first_member, second_member):
        """docstring"""

        cursor = self.db_conn.cursor()

    def add_result(self, offense_winner, defense_winner, offense_loser, defense_loser):
        """docstring"""

        cursor = self.db_conn.cursor()

    def delete_player(self, first_name, last_name, nickname):
        """docstring"""

        cursor = self.db_conn.cursor()

    def delete_team(self, team_name):
        """docstring"""

        cursor = self.db_conn.cursor()

    def delete_result(self, offense_winner, defense_winner, offense_loser, defense_loser, timestamp):
        """docstring"""

        cursor = self.db_conn.cursor()

    def total_players(self):
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
    data_mgr.add_player('Tyler', 'Shake', 'Shake')
    data_mgr.commit_data()
    del data_mgr

if __name__ == '__main__':
    main()
