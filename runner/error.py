from language_manager import Language


class ExecutionError:
    def __init__(self, name, msg, **fmt_args):
        self.name = name
        self.msg = msg
        self.fmt_args = fmt_args

    def format(self, language: Language):
        return language[self.name] + ": " + language[self.msg].format(**self.fmt_args)

    def __str__(self):
        return f"ExecutionError(name={self.name!r}, msg={self.msg!r}, fmt_args={self.fmt_args})"

    def __repr__(self):
        return str(self)
