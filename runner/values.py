from __future__ import annotations
from abc import ABC, abstractmethod
from .error import ExecutionError


class ExeValueType:
    EMPTY = "Empty"
    NUMBER = "Number"
    STRING = "String"
    BOOLEAN = "Boolean"
    ERROR = "<error-type>"


class ExeValue(ABC):
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def empty(self) -> bool:
        return self.type == ExeValueType.EMPTY

    def number(self) -> bool:
        return self.type == ExeValueType.NUMBER

    def string(self) -> bool:
        return self.type == ExeValueType.STRING

    def boolean(self) -> bool:
        return self.type == ExeValueType.BOOLEAN

    def error(self) -> bool:
        return self.type == ExeValueType.ERROR

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return str(self)


class ExeEmpty(ExeValue):
    def __init__(self):
        super().__init__(ExeValueType.EMPTY, None)

    def __str__(self):
        return "ExeEmpty()"


class ExeNumber(ExeValue):
    def __init__(self, value: int | float):
        super().__init__(ExeValueType.NUMBER, value)

    def __str__(self):
        return f"ExeNumber({self.value})"


class ExeString(ExeValue):
    def __init__(self, value: str):
        super().__init__(ExeValueType.STRING, value)

    def __str__(self):
        return f"ExeString({self.value!r})"


class ExeBoolean(ExeValue):
    def __init__(self, value):
        super().__init__(ExeValueType.BOOLEAN, bool(value))

    def __str__(self):
        return f"ExeBoolean({self.value})"


class ExeError(ExeValue):
    def __init__(self, name, msg, **format_args):
        super().__init__(ExeValueType.ERROR, ExecutionError(name, msg, **format_args))

    def __str__(self):
        return f"ExeError({self.value})"


def _type_error(left, right, op):
    return ExeError(
        "error.name.type_error",
        "error.msg.invalid_op_types",
        left_type=left.type,
        right_type=right.type,
        operand=op
    )


def _skip_error(*args):
    for arg in args:
        if arg.error():
            return arg
    return None


def add_val(left: ExeValue, right: ExeValue) -> ExeValue:
    error = _skip_error(left, right)
    if error is not None:
        return error

    if left.number() and right.number():
        return ExeNumber(left.value + right.value)
    elif left.string() or right.string():
        return ExeString(str(left.value) + str(right.value))
    else:
        return _type_error(left, right, "+")


def sub_val(left: ExeValue, right: ExeValue) -> ExeValue:
    error = _skip_error(left, right)
    if error is not None:
        return error

    if left.number() and right.number():
        return ExeNumber(left.value + right.value)
    else:
        return _type_error(left, right, "-")


def mul_val(left: ExeValue, right: ExeValue) -> ExeValue:
    error = _skip_error(left, right)
    if error is not None:
        return error

    if left.number() and right.number():
        return ExeNumber(left.value * right.value)
    else:
        return _type_error(left, right, "*")


def div_val(left: ExeValue, right: ExeValue) -> ExeValue:
    error = _skip_error(left, right)
    if error is not None:
        return error

    if left.number() and right.number():
        if right.value == 0:
            return ExeError("error.name.math_error", "error.msg.division_by_zero")
        return ExeNumber(left.value / right.value)
    else:
        return _type_error(left, right, "/")


def mod_val(left: ExeValue, right: ExeValue) -> ExeValue:
    error = _skip_error(left, right)
    if error is not None:
        return error

    if left.number() and right.number():
        if right.value == 0:
            return ExeError("error.name.math_error", "error.msg.modulo_by_zero")
        return ExeNumber(left.value % right.value)
    else:
        return _type_error(left, right, "%")


def pow_val(left: ExeValue, right: ExeValue) -> ExeValue:
    error = _skip_error(left, right)
    if error is not None:
        return error

    if left.number() and right.number():
        result = left.value ** right.value
        if isinstance(result, complex):
            return ExeError("error.name.math_error", "error.msg.negative_root")
        return ExeNumber(result)
    else:
        return _type_error(left, right, "^")


def eq_val(left: ExeValue, right: ExeValue) -> ExeValue:
    error = _skip_error(left, right)
    if error is not None:
        return error

    if left.empty() or right.empty():
        return _type_error(left, right, "==")

    if left.type != right.type:
        return ExeBoolean(False)
    return ExeBoolean(left.value == right.value)


def ne_val(left: ExeValue, right: ExeValue) -> ExeValue:
    return not_val(eq_val(left, right))


def gt_val(left: ExeValue, right: ExeValue) -> ExeValue:
    error = _skip_error(left, right)
    if error is not None:
        return error

    if left.number() and right.number():
        return ExeBoolean(left.value > right.value)
    elif left.string() and right.string():
        return ExeBoolean(left.value > right.value)
    else:
        return _type_error(left, right, ">")


def lt_val(left: ExeValue, right: ExeValue) -> ExeValue:
    error = _skip_error(left, right)
    if error is not None:
        return error

    if left.number() and right.number():
        return ExeBoolean(left.value < right.value)
    elif left.string() and right.string():
        return ExeBoolean(left.value < right.value)
    else:
        return _type_error(left, right, "<")


def ge_val(left: ExeValue, right: ExeValue) -> ExeValue:
    error = _skip_error(left, right)
    if error is not None:
        return error

    if left.number() and right.number():
        return ExeBoolean(left.value >= right.value)
    elif left.string() and right.string():
        return ExeBoolean(left.value >= right.value)
    else:
        return _type_error(left, right, ">=")


def le_val(left: ExeValue, right: ExeValue) -> ExeValue:
    error = _skip_error(left, right)
    if error is not None:
        return error

    if left.number() and right.number():
        return ExeBoolean(left.value <= right.value)
    elif left.string() and right.string():
        return ExeBoolean(left.value <= right.value)
    else:
        return _type_error(left, right, "<=")


# ================================================= Unary Operations ================================================= #

def to_boolean(value: ExeValue) -> ExeValue:
    if value.error():
        return value

    if value.empty():
        return ExeError(
            "error.name.type_error",
            "error.msg.invalid_cast",
            op_type=value.type,
            cast_type=ExeValueType.BOOLEAN
        )

    return ExeBoolean(value.value)


def to_string(value: ExeValue) -> ExeValue:
    if value.error():
        return value

    if value.empty():
        return ExeError(
            "error.name.type_error",
            "error.msg.invalid_cast",
            op_type=value.type,
            cast_type=ExeValueType.STRING
        )

    return ExeString(str(value.value))


def to_number(value: ExeValue) -> ExeValue:
    if value.error():
        return value

    if value.empty():
        return ExeError(
            "error.name.type_error",
            "error.msg.invalid_cast",
            op_type=value.type,
            cast_type=ExeValueType.NUMBER
        )

    if value.boolean():
        return ExeNumber(1 if value.value else 0)
    elif value.string():
        try:
            num = int(value.value)
        except ValueError:
            try:
                num = float(value.value)
            except ValueError:
                return ExeError(
                    "error.name.value_error",
                    "error.name.bad_num_lit",
                    literal=value.value
                )
        return ExeNumber(num)
    return value


def cast_val(value: ExeValue, type_: ExeValueType) -> ExeValue:
    if type_ == ExeValueType.BOOLEAN:
        value = to_boolean(value)
    elif type_ == ExeValueType.STRING:
        value = to_string(value)
    elif type_ == ExeValueType.NUMBER:
        value = to_number(value)
    else:
        raise RuntimeError(f"Unknown ExeValueType {type_}")
    return value


def not_val(value: ExeValue) -> ExeValue:
    value = to_boolean(value)
    if value.error():
        return value

    return ExeBoolean(not value.value)


def neg_val(value: ExeValue) -> ExeValue:
    if value.error():
        return value

    if value.number():
        return ExeNumber(-value.value)
    else:
        return ExeError(
            "error.name.type_error",
            "error.msg.invalid_uni_op_types",
            operand="-",
            op_type=value.type
        )


def pos_val(value: ExeValue) -> ExeValue:
    if value.error():
        return value

    if value.number():
        return value
    else:
        return ExeError(
            "error.name.type_error",
            "error.msg.invalid_uni_op_types",
            operand="+",
            op_type=value.type
        )
