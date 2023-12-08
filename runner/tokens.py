from enum import Enum, auto


class TokenType(Enum):
    IDENT = auto()
    KEYWORD = auto()
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    FORMAT_STRING = auto()
    TYPE = auto()
    EQUALS = auto()
    COMMA = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    CARET = auto()
    PERC = auto()
    LPAREN = auto()
    RPAREN = auto()
    DOUB_EQ = auto()
    BANG_EQ = auto()
    GREATER = auto()
    LESS = auto()
    GRT_EQ = auto()
    LESS_EQ = auto()


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.type == other.type and self.value == other.value
        return self.type == other or (self.type, self.value) == other

    def __str__(self):
        if self.value is not None:
            return f"Token(type={self.type.name}, value={self.value!r})"
        else:
            return f"Token(type={self.type.name})"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash((self.type, self.value))
