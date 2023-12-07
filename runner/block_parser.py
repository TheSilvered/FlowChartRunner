from nodes import *
from tokens import *
from values import *


class Parser:
    def __init__(self, code):
        self.code = code
        self.idx = 0

    def get_input_ast(self):
        pass

    def get_output_ast(self):
        pass

    def get_init_ast(self):
        pass

    def get_cond_ast(self):
        pass

    def get_calc_ast(self):
        pass

    def __at_end(self):
        return self.idx >= len(self.code)

    def __ch(self):
        return "\0" if self.__at_end() else self.code[self.idx]

    def __advance(self):
        self.idx += 1

    def __consume(self, consume, initial_idx):
        if not consume:
            self.idx = initial_idx

    def __next__(self):
        self.idx += 1
        if self.__at_end():
            raise StopIteration

    def __iter__(self):
        return self

    def __get_next_token(self):
        ch = self.__ch()
        if ch == "\0":
            return Token(TokenType.EOC)
        elif ch in "0123456789":
            return self.__get_num(False)

    def __get_num(self, consume):
        initial_idx = self.idx

        num = ""
        for ch in self:
            if ch not in "0123456789":
                break
            num += ch

        if self.__ch() != ".":
            self.__consume(consume, initial_idx)
            return Token(TokenType.NUMBER, int(num))

        self.__advance()
        if self.__ch() not in "0123456789":
            return error_token("error.name.syntax_error", "error.msg.invalid_num_literal")

        for ch in self:
            if ch not in "0123456789":
                break
            num += ch
