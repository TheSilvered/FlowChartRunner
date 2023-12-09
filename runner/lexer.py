from .tokens import Token, TokenType
from .error import ExecutionError
from string import digits, ascii_letters
import math

KEYWORDS = ("read", "as", "and", "or", "not")
TYPE_NAMES = ("Number", "String", "Boolean")
CONSTANTS = ("true", "false", "_pi", "_e")

char_to_tok_type = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "%": TokenType.PERC,
    "^": TokenType.CARET,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    ",": TokenType.COMMA
}


class Lexer:
    def __init__(self, code):
        self.idx = 0
        self.code = code

    @property
    def finished(self):
        return self.idx >= len(self.code)

    @property
    def ch(self):
        return "\0" if self.finished else self.code[self.idx]

    def advance(self):
        self.idx += 1

    def tokenize(self) -> list[Token] | ExecutionError:
        tokens = []

        while not self.finished:
            if self.ch.isspace():
                self.advance()
                continue

            if self.ch in digits:
                token = self.__make_num()
            elif self.ch in ascii_letters + "_":
                token = self.__make_ident()
            elif self.ch == '"':
                token = self.__make_str()
            else:
                token = self.__make_sym()

            if isinstance(token, ExecutionError):
                return token
            tokens.append(token)

        return tokens

    def __make_num(self):
        num = self.ch
        self.advance()
        while self.ch in digits:
            num += self.ch
            self.advance()

        if self.ch in ascii_letters + "_":
            return ExecutionError("error.name.syntax_error", "error.msg.ident_after_num")

        if not self.ch == ".":
            return Token(TokenType.NUMBER, int(num))

        num += "."
        self.advance()
        if self.ch not in digits:
            return ExecutionError("error.name.syntax_error", "error.msg.invalid_num_literal")
        num += self.ch
        self.advance()
        while self.ch in digits:
            num += self.ch
            self.advance()
        return Token(TokenType.NUMBER, float(num))

    def __make_ident(self):
        ident = ""
        while self.ch in digits + ascii_letters + "_":
            ident += self.ch
            self.advance()

        if ident == "true":
            return Token(TokenType.BOOLEAN, True)
        elif ident == "false":
            return Token(TokenType.BOOLEAN, False)
        elif ident == "_pi":
            return Token(TokenType.NUMBER, math.pi)
        elif ident == "_e":
            return Token(TokenType.NUMBER, math.e)
        elif ident in KEYWORDS:
            return Token(TokenType.KEYWORD, ident)
        elif ident in TYPE_NAMES:
            return Token(TokenType.TYPE, ident)

        return Token(TokenType.IDENT, ident)

    def __make_str(self):
        fmt_string = []
        str_content = ""
        self.advance()
        while self.ch != '"':
            if self.finished:
                return ExecutionError("error.name.syntax_error", "error.msg.open_string")

            if self.ch != "$":
                str_content += self.ch
                self.advance()
                continue
            self.advance()
            if self.ch in '"$':
                str_content += self.ch
                self.advance()
                continue
            elif self.ch in ascii_letters + "_":
                ident_tok = self.__make_ident()
                fmt_string.append(str_content)
                str_content = ""
                fmt_string.append(ident_tok.value)
            else:
                str_content += ""

        self.advance()
        if len(fmt_string) != 0:
            fmt_string.append(str_content)
            return Token(TokenType.FORMAT_STRING, fmt_string)
        return Token(TokenType.STRING, str_content)

    def __make_sym(self):
        if self.ch in char_to_tok_type:
            tok = Token(char_to_tok_type[self.ch])
            self.advance()
            return tok

        if self.ch == "=":
            self.advance()
            if self.ch == "=":
                self.advance()
                return Token(TokenType.DOUB_EQ)
            return Token(TokenType.EQUALS)
        elif self.ch == ">":
            self.advance()
            if self.ch == "=":
                self.advance()
                return Token(TokenType.GRT_EQ)
            return Token(TokenType.GREATER)
        elif self.ch == "<":
            self.advance()
            if self.ch == "=":
                self.advance()
                return Token(TokenType.LESS_EQ)
            return Token(TokenType.LESS)
        elif self.ch == "!":
            self.advance()
            if self.ch != "=":
                return ExecutionError("error.name.syntax_error", "error.msg.unexpected_char", char=self.ch)
            self.advance()
            return Token(TokenType.BANG_EQ)
        return ExecutionError("error.name.syntax_error", "error.msg.unexpected_char", char=self.ch)
