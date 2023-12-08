from .constants import HC_STRS

KEYWORDS = ("read", "as", "and", "or", "not")
TYPE_NAMES = ("Number", "String", "Boolean")
CONSTANTS = ("true", "false", "_pi", "_e")
BUILTIN_FUNCTIONS = ("mod", "sin", "cos", "tan", "arcsin", "arccos", "arctan", "floor", "ceil", "round", "log", "sign",
                     "sqrt", "root")
ARITH_OPERATORS = "+-*/^=<>%"
OTHER_SYMBOLS = "()[]{},"


def highlight_text(text: str) -> str:
    highlighted_text = ""
    i = 0

    while i < len(text):
        token, i = highlight_token(text, i)
        highlighted_text += token

    return highlighted_text


def highlight_token(text: str, i: int) -> tuple[str, int]:
    first_c = text[i]

    if first_c.isspace():
        start = i
        while i < len(text) and text[i].isspace():
            i += 1
        return text[start:i], i
    if first_c.isalpha() or first_c == "_":
        return highlight_ident(text, i)
    elif first_c.isdigit() and first_c.isascii():
        return highlight_number(text, i)
    elif first_c == '"':
        return highlight_string(text, i)
    else:
        return highlight_symbol(text, i)


def highlight_ident(text: str, i: int) -> tuple[str, int]:
    start = i
    while i < len(text) and (text[i].isalnum() or text[i] == "_"):
        i += 1

    ident = text[start:i]
    if ident in KEYWORDS:
        return HC_STRS["orange"] + ident, i
    elif ident in TYPE_NAMES:
        return HC_STRS["teal"] + ident, i
    elif ident in CONSTANTS:
        return HC_STRS["magenta"] + ident, i
    elif ident in BUILTIN_FUNCTIONS:
        return HC_STRS["purple"] + ident, i
    return HC_STRS["reset"] + ident, i


def highlight_number(text: str, i: int) -> tuple[str, int]:
    start = i
    while i < len(text) and text[i].isdigit():
        i += 1

    if i < len(text) and text[i] == '.':
        i += 1
        while i < len(text) and text[i].isdigit():
            i += 1

    return HC_STRS["yellow"] + text[start:i], i


def highlight_string(text: str, i: int) -> tuple[str, int]:
    start_quote = HC_STRS["dark_green"] + '"'
    i += 1
    string = HC_STRS["green"]
    while i < len(text) and text[i] != '"':
        if text[i] != '$':
            string += text[i]
            i += 1
            continue
        i += 1
        if i >= len(text):
            string += "$"
            break
        if text[i] in '"$':
            string += HC_STRS["light_blue"] + "$" + text[i] + HC_STRS["green"]
            i += 1
        elif text[i].isalpha():
            ident_start = i
            i += 1
            while i < len(text) and text[i].isalnum():
                i += 1
            string += HC_STRS["light_blue"] + "$" + text[ident_start:i] + HC_STRS["green"]
        else:
            string += text[i]
            i += 1

    if i < len(text):
        end_quote = start_quote
        i += 1
    else:
        end_quote = ""
    return start_quote + string + end_quote, i


def highlight_symbol(text: str, i: int) -> tuple[str, int]:
    char = text[i]
    col = HC_STRS["reset"]
    i += 1
    if char in ARITH_OPERATORS:
        col = HC_STRS["red"]
    elif char in OTHER_SYMBOLS:
        col = HC_STRS["light_gray"]

    return col + char, i
