from variable import Var


class Stack:
    def __init__(self):
        #ogni elemento dello stack misura 2 byte
        self.__stackmemory__: list = []

    def insert(self, variable: Var = None, data: int = 0) -> None:
        tmp: list | None = variable.getForStack()
        self.__stackmemory__ += variable if tmp is None else tmp

    def get(self, address: int) -> int | Var:
        return self.__stackmemory__[address]

    def remove(self) -> int:
        return self.__stackmemory__.pop(-1)

    def __getitem__(self, item):
        return self.get(item)

    def __add__(self, other):
        self.insert(other)
        return self

    def __sub__(self, other):
        for _ in other:
            self.remove()
        return self
