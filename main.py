from app import App


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    # main()
    from runner.nodes import *
    from runner.values import *
    one = ValueNode(ExeNumber(1))
    two = ValueNode(ExeNumber(2))
    add = BinNode(one, two, BinOp.ADD)
    print(add.evaluate().value)
