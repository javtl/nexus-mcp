"""Errors raised by tools. The gateway (Day 3) maps these to execution_status=FAILED."""


class ToolInputError(ValueError):
    """The tool received invalid input and did not execute."""


class ToolNotFoundError(LookupError):
    """The requested resource does not exist."""