"""Foosball Exceptions

This file contains the implementations of all foosball exceptions.

"""

class FoosballError(Exception):
    """Base class for Foosball exceptions"""
    pass

class HTTPError(FoosballError):
    """Exception raised for HTTP errors

    Args:
        msg (str):  Error message

    Attributes:
        msg (str):  Error message

    """

    def __init__(self, msg):
        super(HTTPError, self).__init__(msg)
        self.msg = msg
