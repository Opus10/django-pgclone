"""Core exceptions for pgclone. All exceptions are caught by CLI and rendered as error messages"""


class Error(Exception):
    """Base exception"""


class KeyError(Error, KeyError):
    """When a key error happens specific to pgclone"""


class ValueError(Error, ValueError):
    """When a value error happens specific to pgclone"""


class RuntimeError(Error, RuntimeError):
    """When a runtime error happens specific to pgclone"""
