from .tokens import Token, TokenType
from .nodes import *
from .error import ExecutionError
from .lexer import Lexer
from ui_components import IOBlock, CondBlock, InitBlock, CalcBlock, BlockBase


def full_compilation(block: BlockBase) -> Node | ExecutionError:
    lexer = Lexer(block.content)
    tokens = lexer.tokenize()
    if isinstance(tokens, ExecutionError):
        return tokens
    parser = Parser(tokens)
    if isinstance(block, IOBlock) and block.is_input:
        ast = parser.parse_input_block()
    elif isinstance(block, IOBlock):
        ast = parser.parse_output_block()
    elif isinstance(block, CondBlock):
        ast = parser.parse_cond_block()
    elif isinstance(block, InitBlock):
        ast = parser.parse_init_block()
    elif isinstance(block, CalcBlock):
        ast = parser.parse_calc_block()
    else:
        return ExecutionError("error.name.comp_error", "error.msg.failed_to_compile_block")
    return ast


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

    def parse_input_block(self) -> Node | ExecutionError:
        if self.tok != (TokenType.KEYWORD, "read"):
            return ExecutionError("error.name.syntax_error", "error.msg.expected_keyword", keyword="read")
        self.advance()

        nodes = []

        while True:
            if self.tok != TokenType.IDENT:
                return ExecutionError("error.name.syntax_error", "error.msg.expected_ident")
            ident = self.tok.value
            self.advance()
            if self.tok != (TokenType.KEYWORD, "as"):
                return ExecutionError("error.name.syntax_error", "error.msg.expected_keyword", keyword="as")
            self.advance()
            if self.tok != TokenType.TYPE:
                return ExecutionError("error.name.syntax_error", "error.msg.expected_type", keyword="as")
            type_ = self.__type_name_to_type(self.tok.value)
            self.advance()

            nodes.append(SetNode(ident, ReadNode(ident, type_), True))
            if self.tok != TokenType.COMMA:
                break
            self.advance()

        if not self.finished:
            return ExecutionError("error.name.syntax_error", "error.msg.unexpected_token", tok_type=self.tok.type.name)
        return CompoundNode(nodes)

    def parse_output_block(self) -> Node | ExecutionError:
        value = self.parse_expr()
        if self.is_error(value):
            return value
        if not self.finished:
            return ExecutionError("error.name.syntax_error", "error.msg.unexpected_token", tok_type=self.tok.type.name)
        return WriteNode(value)

    def parse_cond_block(self) -> Node | ExecutionError:
        value = self.parse_expr()
        if self.is_error(value):
            return value
        if not self.finished:
            return ExecutionError("error.name.syntax_error", "error.msg.unexpected_token", tok_type=self.tok.type.name)
        return WriteNode(value)

    def parse_init_block(self) -> Node | ExecutionError:
        nodes = []

        while True:
            if self.tok != TokenType.IDENT:
                return ExecutionError("error.name.syntax_error", "error.msg.expected_ident")
            ident = self.tok.value
            self.advance()
            if self.tok != TokenType.EQUALS:
                return ExecutionError("error.name.syntax_error", "error.msg.expected_sym", keyword="==")
            self.advance()
            value = self.parse_expr()
            if self.is_error(value):
                return value

            nodes.append(SetNode(ident, value, True))
            if self.tok != TokenType.COMMA:
                break
            self.advance()

        return CompoundNode(nodes)

    def parse_calc_block(self) -> Node | ExecutionError:
        nodes = []

        while True:
            if self.tok != TokenType.IDENT:
                return ExecutionError("error.name.syntax_error", "error.msg.expected_ident")
            ident = self.tok.value
            self.advance()
            if self.tok != TokenType.EQUALS:
                return ExecutionError("error.name.syntax_error", "error.msg.expected_sym", keyword="==")
            self.advance()
            value = self.parse_expr()
            if self.is_error(value):
                return value

            nodes.append(SetNode(ident, value, False))
            if self.tok != TokenType.COMMA:
                break
            self.advance()

        return CompoundNode(nodes)

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
        type_ = self.__type_name_to_type(self.tok.value)
        self.advance()
        return CastNode(value, type_)

    def parse_value(self) -> Node | ExecutionError:
        if self.finished:
            return ExecutionError("error.name.syntax_error", "error.msg.expected_value")

        if self.tok == TokenType.NUMBER:
            node = ValueNode(ExeNumber(self.tok.value))
            self.advance()
            return node
        elif self.tok == TokenType.BOOLEAN:
            node = ValueNode(ExeBoolean(self.tok.value))
            self.advance()
            return node
        elif self.tok == TokenType.STRING:
            node = ValueNode(ExeString(self.tok.value))
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

    @staticmethod
    def __type_name_to_type(type_name):
        if type_name == "Number":
            type_ = ExeValueType.NUMBER
        elif type_name == "Boolean":
            type_ = ExeValueType.BOOLEAN
        elif type_name == "String":
            type_ = ExeValueType.STRING
        else:
            raise ValueError(f"Unknown type name {type_name}")
        return type_
