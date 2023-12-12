from __future__ import annotations
from enum import auto
from .values import *
from .io_interface import Console
from enum import Enum


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
    CALL = auto()


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

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return self.__str__()


class ValueNode(Node):
    def __init__(self, value: ExeValue):
        super().__init__(NodeType.VALUE)
        self.value = value

    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        return self.value

    def __str__(self):
        return f"ValueNode(value={self.value})"


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

    def __str__(self):
        return f"BinNode(left_node={self.left_node}, right_node={self.right_node}, op={self.op.name})"


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

    def __str__(self):
        return f"UniNode(node={self.node}, op={self.op.name})"


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
                return ExeError("error.name.var_error", "error.msg.var_not_defined", var_name=ident)
            end_str += str(value.value)
        end_str += self.fmt_string[-1]
        return ExeString(end_str)

    def __str__(self):
        return f"FmtNode(fmt_string={self.fmt_string})"


class CastNode(Node):
    def __init__(self, node: Node, type_: ExeValueType):
        super().__init__(NodeType.CAST)
        self.node = node
        self.type = type_

    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        return cast_val(self.node.evaluate(sym_table, console), self.type)

    def __str__(self):
        return f"CastNode(node={self.node}, type={self.type})"


class GetNode(Node):
    def __init__(self, name: str):
        super().__init__(NodeType.GET_VAR)
        self.name = name

    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        value = sym_table.get(self.name)
        if value is None:
            return ExeError("error.name.var_error", "error.msg.var_not_defined", var_name=self.name)
        return value

    def __str__(self):
        return f"GetNode(name={self.name!r})"


class SetNode(Node):
    def __init__(self, name: str, value: Node, init: bool):
        super().__init__(NodeType.SET_VAR)
        self.name = name
        self.value = value
        self.init = init

    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        if self.init and self.name in sym_table:
            return ExeError("error.name.var_error", "error.msg.var_already_defined", var_name=self.name)
        elif not self.init and self.name not in sym_table:
            return ExeError("error.name.var_error", "error.msg.var_not_defined", var_name=self.name)
        value = self.value.evaluate(sym_table, console)
        if value.error():
            return value
        
        sym_table[self.name] = value
        return ExeEmpty()

    def __str__(self):
        return f"SetNode(name={self.name!r}, value={self.value}, init={self.init})"


class CompoundNode(Node):
    def __init__(self, nodes: list[Node]):
        super().__init__(NodeType.COMPOUND)
        self.nodes = nodes

    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        for node in self.nodes:
            value = node.evaluate(sym_table, console)
            if value.error():
                return value

        return ExeEmpty()

    def __str__(self):
        return f"CompoundNode(nodes={self.nodes})"


class WriteNode(Node):
    def __init__(self, node: Node):
        super().__init__(NodeType.WRITE)
        self.node = node

    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        value = to_string(self.node.evaluate(sym_table, console))
        if value.error():
            return value
        console.stdout_write(value.value)
        return ExeEmpty()

    def __str__(self):
        return f"WriteNode(node={self.node})"


class ReadNode(Node):
    def __init__(self, name: str, type_: ExeValueType):
        super().__init__(NodeType.READ)
        self.name = name
        self.type = type_

    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        while True:
            console.stdin_hint(f"{self.name} ({self.type})")
            value = ExeString(console.stdin_read())
            if self.type == ExeValueType.BOOLEAN:
                if "true".startswith(value.value.lower()):
                    value = ExeBoolean(True)
                elif "false".startswith(value.value.lower()):
                    value = ExeBoolean(False)
                else:
                    value = ExeError("", "")
            else:
                value = cast_val(value, self.type)
            if not value.error():
                sym_table[self.name] = value
                break
        return ExeEmpty()

    def __str__(self):
        return f"ReadNode(name={self.name!r}, type={self.type})"


class CallNode(Node):
    def __init__(self, func_name: str, arg_nodes: list[Node]):
        super().__init__(NodeType.CALL)
        self.func_name = func_name
        self.arg_nodes = arg_nodes

    def evaluate(self, sym_table: dict, console: Console) -> ExeValue:
        arg_values = []
        for arg_node in self.arg_nodes:
            value = arg_node.evaluate(sym_table, console)
            if value.error():
                return value
            arg_values.append(value)

        if self.func_name == "mod":
            value = mod_func(arg_values)
        elif self.func_name == "sin":
            value = sin_func(arg_values)
        elif self.func_name == "cos":
            value = cos_func(arg_values)
        elif self.func_name == "tan":
            value = tan_func(arg_values)
        elif self.func_name == "arcsin":
            value = arcsin_func(arg_values)
        elif self.func_name == "arccos":
            value = arccos_func(arg_values)
        elif self.func_name == "arctan":
            value = arctan_func(arg_values)
        elif self.func_name == "floor":
            value = floor_func(arg_values)
        elif self.func_name == "ceil":
            value = ceil_func(arg_values)
        elif self.func_name == "round":
            value = round_func(arg_values)
        elif self.func_name == "log":
            value = log_func(arg_values)
        elif self.func_name == "sign":
            value = sign_func(arg_values)
        elif self.func_name == "sqrt":
            value = sqrt_func(arg_values)
        elif self.func_name == "root":
            value = root_func(arg_values)
        elif self.func_name == "max":
            value = max_func(arg_values)
        elif self.func_name == "min":
            value = min_func(arg_values)
        elif self.func_name == "abs":
            value = abs_func(arg_values)
        else:
            value = ExeError("error.name.call_error", "error.msg.func_not_defined", func=self.func_name)
        return value

    def __str__(self):
        return f"CallNode(func_name={self.func_name!r}, arg_nodes={self.arg_nodes})"
