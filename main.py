from app import App


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    # main()
    from ui_components.blocks import *
    from runner import full_compilation, ExecutionError, TerminalLink
    from runner.nodes import CompoundNode
    ast_0 = full_compilation(IOBlock(None, '"Insert the side of the cube"'))
    ast_1 = full_compilation(IOBlock(None, "read side as Number", True))
    ast_2 = full_compilation(InitBlock(None, "vol = side * side * side"))
    ast_3 = full_compilation(IOBlock(None, '"The volume is $vol"'))
    if isinstance(ast_0, ExecutionError):
        print(ast_0)
        exit()
    if isinstance(ast_1, ExecutionError):
        print(ast_1)
        exit()
    if isinstance(ast_2, ExecutionError):
        print(ast_2)
        exit()
    if isinstance(ast_3, ExecutionError):
        print(ast_3)
        exit()
    ast = CompoundNode([ast_0, ast_1, ast_2, ast_3])
    ast.evaluate({}, TerminalLink())
