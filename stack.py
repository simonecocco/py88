'''
è la classe che si occupa di emulare il comportamento dello stack memorizzando interi a 2byte (indirizzi e dati)
'''

from variable import Var
from register import Registers


class Stack:
    def __init__(self, registers: Registers):
        #ogni elemento dello stack misura 2 byte
        self.__stackmemory__: list = []
        self.__bkp__: list = []
        self.registers: Registers = registers

    def __backup__(self) -> None:
        self.__bkp__ = self.__stackmemory__.copy()

    def __restore__(self) -> None:
        self.__stackmemory__ = self.__bkp__.copy()
        self.registers['SP'] = len(self.__stackmemory__)

    def insert(self, variable: Var = None, data: int = 0, offset: int = 0) -> None:
        tmp: list | None = None
        if variable is not None:
            var_value: list | None = variable.getforstack(offset)
            if var_value is None:
                tmp: list = [data & 0xFF, (data >> 8) & 0xFF]
                self.__stackmemory__ += tmp

            else:
                if len(var_value) % 2 != 0:
                    var_value += [0]
                self.__stackmemory__ += var_value

        else:
            tmp: list = [data & 0xFF, (data >> 8) & 0xFF]
            self.__stackmemory__ += tmp

        self.registers['SP'] = self.registers['SP'] + 2

    def get(self, address: int = -1) -> int | Var:
        return (self.__stackmemory__[address] << 8) + self.__stackmemory__[address-1]

    def remove(self) -> int:
        data: int = self.get()
        self.__stackmemory__.pop(-1)
        self.__stackmemory__.pop(-1)
        return data

    def __getitem__(self, item):
        return self.get(item)

    def __add__(self, other):
        self.insert(other)
        return self

    def __sub__(self, other):
        for _ in other:
            self.remove()
        return self

