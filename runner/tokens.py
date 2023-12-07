from enum import Enum, auto


class TokenType(Enum):
    IDENT = auto()
    KEYWORD = auto()
    NUMBER = auto()
    STRING = auto()
    FORMAT_STRING = auto()
    TYPE = auto()
    INT = auto()
    REAL = auto()
    EQUALS = auto()
    COMMA = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    POW = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOC = auto()  # end of code

    ERROR = auto()


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __eq__(self, other):
        return self.type == other or (self.type, self.value) == other


def error_token(name, msg, **fmt_args):
    return Token(TokenType.ERROR, (name, msg, fmt_args))
