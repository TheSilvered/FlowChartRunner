from __future__ import annotations
from abc import abstractmethod
from enum import auto
from .values import *


class NodeType(Enum):
    VALUE = auto()
    BIN_OP = auto()
    UNI_OP = auto()
    SET_VAR = auto()
    GET_VAR = auto()


class BinOp(Enum):
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
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
    FMT_STR = auto()


class Node(ABC):
    def __init__(self, type_):
        self.type = type_

    @abstractmethod
    def evaluate(self, sym_table: dict) -> ExeValue:
        pass


class ValueNode(Node):
    def __init__(self, value: ExeValue):
        super().__init__(NodeType.VALUE)
        self.value = value

    def evaluate(self, sym_table: dict) -> ExeValue:
        return self.value


class BinNode(Node):
    def __init__(self, left_node: Node, right_node: Node, op: BinOp):
        super().__init__(NodeType.BIN_OP)
        self.left_node = left_node
        self.right_node = right_node
        self.op = op

    def evaluate(self, sym_table: dict) -> ExeValue:
        if self.op == BinOp.ADD:
            return add_val(self.left_node.evaluate(sym_table), self.right_node.evaluate(sym_table))
        elif self.op == BinOp.SUB:
            return sub_val(self.left_node.evaluate(sym_table), self.right_node.evaluate(sym_table))
        elif self.op == BinOp.MUL:
            return mul_val(self.left_node.evaluate(sym_table), self.right_node.evaluate(sym_table))
        elif self.op == BinOp.DIV:
            return div_val(self.left_node.evaluate(sym_table), self.right_node.evaluate(sym_table))
        elif self.op == BinOp.POW:
            return pow_val(self.left_node.evaluate(sym_table), self.right_node.evaluate(sym_table))
        elif self.op == BinOp.L_AND:
            left_val = to_boolean(self.left_node.evaluate(sym_table))
            if left_val.error() or not left_val.value:
                return left_val
            return to_boolean(self.right_node.evaluate(sym_table))
        elif self.op == BinOp.L_OR:
            left_val = to_boolean(self.left_node.evaluate(sym_table))
            if left_val.error() or left_val.value:
                return left_val
            return to_boolean(self.right_node.evaluate(sym_table))
        elif self.op == BinOp.EQ:
            return eq_val(self.left_node.evaluate(sym_table), self.right_node.evaluate(sym_table))
        elif self.op == BinOp.NE:
            return ne_val(self.left_node.evaluate(sym_table), self.right_node.evaluate(sym_table))
        elif self.op == BinOp.GT:
            return gt_val(self.left_node.evaluate(sym_table), self.right_node.evaluate(sym_table))
        elif self.op == BinOp.LT:
            return gt_val(self.left_node.evaluate(sym_table), self.right_node.evaluate(sym_table))
        elif self.op == BinOp.GE:
            return gt_val(self.left_node.evaluate(sym_table), self.right_node.evaluate(sym_table))
        elif self.op == BinOp.LE:
            return gt_val(self.left_node.evaluate(sym_table), self.right_node.evaluate(sym_table))
        else:
            raise RuntimeError(f"Unknown BinOp {self.op}")


class UniNode(Node):
    def __init__(self, node: Node, op: UniOp):
        super().__init__(NodeType.UNI_OP)
        self.node = node
        self.op = op

    def evaluate(self, sym_table: dict) -> ExeValue:
        if self.op == UniOp.NOT:
            return not_val(self.node.evaluate(sym_table))
        elif self.op == UniOp.NEG:
            return neg_val(self.node.evaluate(sym_table))
        elif self.op == UniOp.POS:
            return pos_val(self.node.evaluate(sym_table))
        elif self.op == UniOp.FMT_STR:
            raise RuntimeError(f"String formatting is not yet supported")
        else:
            raise RuntimeError(f"Unknown UniOp {self.op}")
