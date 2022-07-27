from variable import Var


class Stack:
    def __init__(self):
        #ogni elemento dello stack misura 2 byte
        self.__stackmemory__: list = []

    def insert(self, variable: Var = None, data: int = 0, offset: int = 0) -> None:
        tmp: list | None = None
        if variable is not None:
            var_value: list | None = variable.getForStack(offset)
            if var_value is None:
                self.__stackmemory__.append(data)
                print(f'stack aggiunto {data}')  # todo sistema il messaggio
            else:
                self.__stackmemory__ += var_value
                print(f'stack aggiunto {var_value}')  # todo sistema il messaggio
        else:
            self.__stackmemory__.append(data)
            print(f'stack aggiunto {data}') #todo sistema il messaggio

    def get(self, address: int = -1) -> int | Var:
        return (self.__stackmemory__[address] << 8) + self.__stackmemory__[address-1]

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
