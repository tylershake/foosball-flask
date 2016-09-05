"""Data Manager Exceptions

This file contains the implementations of all data manager exceptions.

"""

class DataManagerError(Exception):
    """Base class for Data Manager exceptions"""
    pass

class DBConnectionError(DataManagerError):
    """Exception raised for database connection errors

    Args:
        msg (str):  Error message

    Attributes:
        msg (str):  Error message

    """

    def __init__(self, msg):
        super(DBConnectionError, self).__init__(msg)
        self.msg = msg

class DBSyntaxError(DataManagerError):
    """Exception raised for database syntax errors

    Args:
        msg (str):  Error message

    Attributes:
        msg (str):  Error message

    """

    def __init__(self, msg):
        super(DBSyntaxError, self).__init__(msg)
        self.msg = msg

class DBValueError(DataManagerError):
    """Exception raised for database value errors

    Args:
        msg (str):  Error message

    Attributes:
        msg (str):  Error message

    """

    def __init__(self, msg):
        super(DBValueError, self).__init__(msg)
        self.msg = msg

class DBExistError(DataManagerError):
    """Exception raised for database exist errors

    Args:
        msg (str):  Error message

    Attributes:
        msg (str):  Error message

    """

    def __init__(self, msg):
        super(DBExistError, self).__init__(msg)
        self.msg = msg
