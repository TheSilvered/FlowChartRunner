from __future__ import annotations
from abc import abstractmethod
from enum import auto
from .values import *
from .io_interface import Console


class NodeType(Enum):
    VALUE = auto()
    BIN_OP = auto()
    UNI_OP = auto()
    SET_VAR = auto()
    GET_VAR = auto()
    FMT_STR = auto()
    CAST = auto()
    COMPOUND = auto()
    WRITE = auto()
    READ = auto()


class BinOp(Enum):
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    POW = auto()
    L_AND = auto()
    L_OR = auto()
    EQ = auto()
    NE = auto()
    GT = auto()
    LT = auto()
    GE = auto()
    LE = auto()


class UniOp(Enum):
    NEG = auto()
    POS = auto()
    NOT = auto()


class Node(ABC):
    def __init__(self, type_):
        self.type = type_

    @abstractmethod
    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        pass


class ValueNode(Node):
    def __init__(self, value: ExeValue):
        super().__init__(NodeType.VALUE)
        self.value = value

    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        return self.value


class BinNode(Node):
    def __init__(self, left_node: Node, right_node: Node, op: BinOp):
        super().__init__(NodeType.BIN_OP)
        self.left_node = left_node
        self.right_node = right_node
        self.op = op

    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        left_val = self.left_node.evaluate(sym_table, console)
        if left_val.error():
            return left_val

        if self.op == BinOp.ADD:
            return add_val(left_val, self.right_node.evaluate(sym_table, console))
        elif self.op == BinOp.SUB:
            return sub_val(left_val, self.right_node.evaluate(sym_table, console))
        elif self.op == BinOp.MUL:
            return mul_val(left_val, self.right_node.evaluate(sym_table, console))
        elif self.op == BinOp.DIV:
            return div_val(left_val, self.right_node.evaluate(sym_table, console))
        elif self.op == BinOp.MOD:
            return mod_val(left_val, self.right_node.evaluate(sym_table, console))
        elif self.op == BinOp.POW:
            return pow_val(left_val, self.right_node.evaluate(sym_table, console))
        elif self.op == BinOp.L_AND:
            left_val = to_boolean(left_val)
            if left_val.error() or not left_val.value:
                return left_val
            return to_boolean(self.right_node.evaluate(sym_table, console))
        elif self.op == BinOp.L_OR:
            left_val = to_boolean(left_val)
            if left_val.error() or left_val.value:
                return left_val
            return to_boolean(self.right_node.evaluate(sym_table, console))
        elif self.op == BinOp.EQ:
            return eq_val(left_val, self.right_node.evaluate(sym_table, console))
        elif self.op == BinOp.NE:
            return ne_val(left_val, self.right_node.evaluate(sym_table, console))
        elif self.op == BinOp.GT:
            return gt_val(left_val, self.right_node.evaluate(sym_table, console))
        elif self.op == BinOp.LT:
            return gt_val(left_val, self.right_node.evaluate(sym_table, console))
        elif self.op == BinOp.GE:
            return gt_val(left_val, self.right_node.evaluate(sym_table, console))
        elif self.op == BinOp.LE:
            return gt_val(left_val, self.right_node.evaluate(sym_table, console))
        else:
            raise RuntimeError(f"Unknown BinOp {self.op.name}")


class UniNode(Node):
    def __init__(self, node: Node, op: UniOp):
        super().__init__(NodeType.UNI_OP)
        self.node = node
        self.op = op

    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        if self.op == UniOp.NOT:
            return not_val(self.node.evaluate(sym_table, console))
        elif self.op == UniOp.NEG:
            return neg_val(self.node.evaluate(sym_table, console))
        elif self.op == UniOp.POS:
            return pos_val(self.node.evaluate(sym_table, console))
        else:
            raise RuntimeError(f"Unknown UniOp {self.op.name}")


class FmtNode(Node):
    def __init__(self, fmt_string: list):
        super().__init__(NodeType.FMT_STR)
        self.fmt_string = fmt_string

    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        end_str = ""
        for s, ident in zip(self.fmt_string[::2], self.fmt_string[1::2]):
            end_str += s
            value = sym_table.get(ident)
            if value is None:
                return ExeError("error.name.var_error", "error.msg.var_not_defined")
            end_str += str(value.value)
        end_str += self.fmt_string[-1]
        return ExeString(end_str)


class CastNode(Node):
    def __init__(self, node: Node, type_: ExeValueType):
        super().__init__(NodeType.CAST)
        self.node = node
        self.type = type_

    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        value = self.node.evaluate(sym_table, console)
        if self.type == ExeValueType.BOOLEAN:
            value = to_boolean(value)
        elif self.type == ExeValueType.STRING:
            value = to_string(value)
        elif self.type == ExeValueType.NUMBER:
            value = to_number(value)
        else:
            raise RuntimeError(f"Unknown ExeValueType {self.type.name}")
        return value


class GetNode(Node):
    def __init__(self, name: str):
        super().__init__(NodeType.GET_VAR)
        self.name = name

    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        value = sym_table.get(self.name)
        if value is None:
            return ExeError("error.name.var_error", "error.msg.var_not_defined")
        return value


class SetNode(Node):
    def __init__(self, name: str, value: Node, init: bool):
        super().__init__(NodeType.SET_VAR)
        self.name = name
        self.value = value
        self.init = init

    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        if self.init and self.name in sym_table:
            return ExeError("error.name.var_error", "error.msg.var_already_defined")
        elif not self.init and self.name not in sym_table:
            return ExeError("error.name.var_error", "error.msg.var_not_defined")
        value = self.value.evaluate(sym_table, console)
        if value.error():
            return value
        
        sym_table[self.name] = value
        return ExeEmpty()


class CompoundNode(Node):
    def __init__(self, nodes):
        super().__init__(NodeType.COMPOUND)
        self.nodes = nodes

    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        for node in self.nodes:
            value = node.evaluate()
            if value.error:
                return value

        return ExeEmpty()
