class IllegalOperator(Exception):
    def __init__(self, msg: str):
        Exception.__init__(self, msg)


class IllegalMemoryAddress(Exception):
    def __init__(self, msg: str):
        Exception.__init__(self, msg)
