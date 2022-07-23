import re

from stack import Stack
from register import Registers
from divide_file import Program
from variable import Var

DTYPE: dict[str: int] = {'reg': 0, 'mem': 1, 'const': 2}


class Core:
    def __init__(self, stack: Stack, registers: Registers, data: Program, fun: dict):
        self.stack: Stack = stack
        self.registers: Registers = registers
        self.data: Program = data
        self.dprint = fun['d']
        self.oprint = fun['o']
        self.eprint = fun['e']

    def __toint__(self, number: str) -> int:
        conv: list[str] = re.findall(r'^(0[xX][A-Fa-f0-9]{1,})', number) #hex
        if len(conv) > 0:
            num: int = int(conv[0], 16)
            return num
        conv = re.findall(r'^(0[0-7]{1,})', number) #octal
        if len(conv) > 0:
            num: int = int(conv[0], 8)
            return num
        conv = re.findall(r'^(0b[01]{1,})', number) #binary
        if len(conv) > 0:
            num: int = int(conv[0], 2)
            return num
        conv = re.findall(r'^([0-9]{1,})', number) #decimal
        if len(conv) > 0:
            num: int = int(conv[0])
            return num

    def __getmemorylocation__(self, name: str):
        location: int = 0
        for item in self.data.getglobalmemory():
            if item.varname == name:
                break
            location += item.size
        return location

    def __getlocationfromregister__(self, reg: str):
        pass #todo

    def __solveop__(self, op: str) -> Var | str | int: #Var variabile, str è un registro, int un numero
        not_immediate: list[tuple] = re.findall(r'([\d]{0,})[\(]{0,}([\w\d]{0,})[\)]{0,}([-+]{0,1})[\(]{0,}([\w\d]{0,})[\)]{0,}', op)
        if len(not_immediate) > 0:
            pass
        else:
            return self.__toint__(op)

        if self.registers.isregister(op):
            return op
        elif '(' in op and ')' in op: # indirizzo, rende direttamente la variabile
            pass #todo
        elif '-' in op or '+' in op: # fa le operazioni interne all'operando
            pass
        else: # nel caso di un coso singolo
            pass

    def mov(self, dest: str, src: str) -> None:
        dest_op: Var | str | int = self.__solveop__(dest)
        src_op: Var | str | int = self.__solveop__(src)
        #todo
