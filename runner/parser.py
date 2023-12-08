from .tokens import Token, TokenType
from .nodes import *
from .error import ExecutionError

# Operator precedence
# or
# and
# not
# ==, !=, >, <, >=, <=
# +, -
# *, /, %
# ^
# as
# (unary) +, (unary) -


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.idx = 0

    def parse_input_block(self):
        pass

    def parse_output_block(self):
        pass

    def parse_cond_block(self):
        pass

    def parse_init_block(self):
        pass

    def parse_calc_block(self):
        pass

    @property
    def tok(self):
        if self.idx >= len(self.tokens):
            return Token(None)
        return self.tokens[self.idx]

    @property
    def finished(self):
        return self.idx >= len(self.tokens)

    def advance(self):
        self.idx += 1

    @staticmethod
    def is_error(node: Node | ExecutionError):
        return isinstance(node, ExecutionError)

    def __parse_bin_op(self, operators, next_level):
        left_node = next_level()
        if self.is_error(left_node):
            return left_node

        if self.tok in operators:
            op = operators[self.tok]
        else:
            return left_node

        self.advance()
        right_node = next_level()
        if self.is_error(right_node):
            return right_node

        return BinNode(left_node, right_node, op)

    def parse_expr(self) -> Node | ExecutionError:
        return self.__parse_bin_op(
            {
                Token(TokenType.KEYWORD, "or"): BinOp.L_OR
            },
            self.parse_l_and
        )

    def parse_l_and(self) -> Node | ExecutionError:
        return self.__parse_bin_op(
            {
                Token(TokenType.KEYWORD, "and"): BinOp.L_AND
            },
            self.parse_l_not
        )

    def parse_l_not(self) -> Node | ExecutionError:
        if self.tok == (TokenType.KEYWORD, "not"):
            self.advance()
            value = self.parse_relation()
            if self.is_error(value):
                return value
            return UniNode(value, UniOp.NOT)
        return self.parse_relation()

    def parse_relation(self) -> Node | ExecutionError:
        return self.__parse_bin_op(
            {
                Token(TokenType.DOUB_EQ): BinOp.EQ,
                Token(TokenType.BANG_EQ): BinOp.NE,
                Token(TokenType.GREATER): BinOp.GT,
                Token(TokenType.LESS):    BinOp.LT,
                Token(TokenType.GRT_EQ):  BinOp.GE,
                Token(TokenType.LESS_EQ): BinOp.LE
            },
            self.parse_addend
        )

    def parse_addend(self) -> Node | ExecutionError:
        return self.__parse_bin_op(
            {
                Token(TokenType.PLUS): BinOp.ADD,
                Token(TokenType.MINUS): BinOp.SUB
            },
            self.parse_factor
        )

    def parse_factor(self) -> Node | ExecutionError:
        return self.__parse_bin_op(
            {
                Token(TokenType.STAR): BinOp.MUL,
                Token(TokenType.SLASH): BinOp.DIV,
                Token(TokenType.PERC): BinOp.MOD
            },
            self.parse_pow
        )

    def parse_pow(self) -> Node | ExecutionError:
        return self.__parse_bin_op(
            {
                Token(TokenType.CARET): BinOp.POW
            },
            self.parse_cast
        )

    def parse_cast(self):
        value = self.parse_value()
        if self.is_error(value) or self.tok != (TokenType.KEYWORD, "as"):
            return value
        self.advance()
        if self.tok != TokenType.TYPE:
            return ExecutionError("error.name.syntax_error", "error.msg.expected_type")
        if self.tok.value == "Number":
            type_ = ExeValueType.NUMBER
        elif self.tok.value == "Boolean":
            type_ = ExeValueType.BOOLEAN
        elif self.tok.value == "String":
            type_ = ExeValueType.STRING
        else:
            raise ValueError(f"Unknown type name {self.tok.value}")
        self.advance()
        return CastNode(value, type_)

    def parse_value(self) -> Node | ExecutionError:
        if self.finished:
            return ExecutionError("error.name.syntax_error", "error.msg.expected_value")

        if self.tok == TokenType.NUMBER:
            node = ValueNode(ExeValue(ExeValueType.NUMBER, self.tok.value))
            self.advance()
            return node
        elif self.tok == TokenType.BOOLEAN:
            node = ValueNode(ExeValue(ExeValueType.BOOLEAN, self.tok.value))
            self.advance()
            return node
        elif self.tok == TokenType.STRING:
            node = ValueNode(ExeValue(ExeValueType.STRING, self.tok.value))
            self.advance()
            return node
        elif self.tok == TokenType.FORMAT_STRING:
            node = FmtNode(self.tok.value)
            self.advance()
            return node
        elif self.tok == TokenType.IDENT:
            node = GetNode(self.tok.value)
            self.advance()
            return node
        elif self.tok == TokenType.PLUS:
            self.advance()
            value = self.parse_value()
            if self.is_error(value):
                return value
            return UniNode(value, UniOp.POS)
        elif self.tok == TokenType.MINUS:
            self.advance()
            value = self.parse_value()
            if self.is_error(value):
                return value
            return UniNode(value, UniOp.NEG)
        elif self.tok == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expr()
            if self.is_error(expr):
                return expr
            if self.tok != TokenType.RPAREN:
                return ExecutionError("error.name.syntax_error", "error.msg.expected_sym", string=")")
            self.advance()
            return expr
        else:
            return ExecutionError("error.name.syntax_error", "error.msg.unexpected_token", tok_type=self.tok.type.name)
