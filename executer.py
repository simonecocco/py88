import re

from stack import Stack
from register import Registers
from divide_file import Program
from variable import Var
from exceptions import *

DTYPE: dict[str: int] = {'reg': 0, 'mem': 1, 'const': 2}


class Core:
    def __init__(self, stack: Stack, registers: Registers, data: Program, fun: dict):
        self.stack: Stack = stack
        self.registers: Registers = registers
        self.data: Program = data
        self.dprint = fun['d']
        self.oprint = fun['o']
        self.eprint = fun['e']

    def __toint__(self, number: str) -> int | None:
        conv: list[str] = re.findall(r'^(0[xX][A-Fa-f0-9]{1,})', number)  # hex
        if len(conv) > 0:
            num: int = int(conv[0], 16)
            return num
        conv = re.findall(r'^(0[0-7]{1,})', number)  # octal
        if len(conv) > 0:
            num: int = int(conv[0], 8)
            return num
        conv = re.findall(r'^(0b[01]{1,})', number)  # binary
        if len(conv) > 0:
            num: int = int(conv[0], 2)
            return num
        conv = re.findall(r'^([0-9]{1,})', number)  # decimal
        if len(conv) > 0:
            num: int = int(conv[0])
            return num

        return None

    def __getmemoryaddress__(self, address: int) -> list[
        Var, int]:  # ritorna la variabile che contiene il dato richiesto
        loc: int = 0
        var: Var | None = None
        for item in self.data.getglobalmemory():
            if address == loc or (loc < address < loc + item.size):
                var = item
                break
            loc += item.size
        else:
            raise IllegalMemoryAddress(f'Indirizzo non valido ({address})')
        return [var, loc]

    def __getvaluefrommemory__(self, name: str, includeconstants: bool = True) -> list[
        Var, int]:  # spazio di memoria, indirizzo
        location: int = 0
        space: Var | None = None
        for item in self.data.getglobalmemory(includeconstants):
            if item.varname == name:
                space = item
                break
            location += item.size
        else:
            raise IllegalMemoryAddress(f'Simbolo inesistente ({name})')
        return [space, location]

    def __solveop__(self, op: str, includeconstants: bool = True) -> list[Var, int, int] | str | int:  # Var variabile locazione e offset, str è un registro, int un numero
        not_immediate: list[tuple] = re.findall(
            r'([\d]{0,})([\(]{0,1}[\w\d]{1,}[\)]{0,1}){0,}([-+]{0,1})([\(]{0,1}[\w\d]{1,}[\)]{0,1}){0,}', op)
        number: str | None = ''
        sign: str | None = ''
        op1: str | None = ''
        op2: str | None = ''

        if len(not_immediate) > 0:  # da qua vediamo che tipo di operatore è
            number = not_immediate[0][0]
            sign = not_immediate[0][2]
            op1 = not_immediate[0][1]
            op2 = not_immediate[0][3]
        else:
            raise IllegalOperator(f'{op} non è stato riconosciuto come operatore valido')

        offset: int = -1
        if op1 != '' and '(' not in op1 and ')' not in op1 and sign == '' and op2 == '':
            offset: int = 0
            if number != '':
                offset = self.__toint__(number)
            if self.registers.isregister(op1):  # MOV CX; _EXIT
                return op1
            var, loc = self.__getvaluefrommemory__(op1, includeconstants)
            return [var, loc, offset]
        elif '(' in op1 and ')' in op1:  # MOV 4(op), ...
            op1 = op1.replace('(', '').replace(')', '')
            offset: int = 0
            if number != '':
                offset = self.__toint__(number)
            if self.registers.isregister(op1):
                memoryval, loc = self.__getvaluefrommemory__(self.registers[op1], includeconstants)
                return [memoryval, loc, offset]
            var, loc = self.__getvaluefrommemory__(op1, includeconstants)
            return [var, loc, offset]
        elif op1 != '' and op2 != '' and sign == '':  # ottiene il valore presente nella memoria
            op1 = op1.replace('(', '').replace(')', '')
            op2 = op2.replace('(', '').replace(')', '')
            op1_a: int = 0
            op2_a: int = 0
            num: int | None = None
            if number != '':
                num = self.__toint__(number)
            if self.registers.isregister(op1):
                op1_a = self.__toint__(self.registers[op1])
            else:
                _, op1_a = self.__getmemoryaddress__(self.registers[op1])
            if self.registers.isregister(op2):
                op2_a = self.__toint__(self.registers[op2])
            else:
                _, op2_a = self.__getmemoryaddress__(self.registers[op2])
            return self.__getmemoryaddress__(op1_a + op2_a + num)
        elif op1 != '' and op2 != '' and sign != '':  # c'è un'operazione
            num1: int | None = self.__toint__(op1)
            num2: int | None = self.__toint__(op2)
            if num1 is None:
                var, num1 = self.__getvaluefrommemory__(op1, includeconstants)
            if num2 is None:
                var, num2 = self.__getvaluefrommemory__(op2, includeconstants)
            if '-' in sign:
                num2 *= -1
            return num1 + num2
        elif number != '':  # c'è una costante
            return self.__toint__(number)
        else:
            raise IllegalOperator(f'{op} non contiene operatori validi')

    def mov(self, dest: str, src: str) -> None:
        self.dprint(f'MOV {dest}, {src}')
        dest_op: list[Var, int, int] | str | int = self.__solveop__(dest, False)
        src_op: list[Var, int, int] | str | int = self.__solveop__(src)

        dtype = type(dest_op)
        stype = type(src_op)
        value: int = 0
        if stype is int:
            value = src_op
        elif stype is str:
            value = self.registers[src_op]
        else:
            value = src_op[0].value if type(src_op) is int else src_op[1] + src_op[2]

        if dtype is str:
            self.registers[dest_op] = value
        elif dtype is list:
            dest_op[0].value = value
        else:
            raise IllegalOperator(f'la destinazione non può essere una costante ({dest_op})')

    def push(self, data: str) -> None:
        data_op: list[Var, int, int] | str | int = self.__solveop__(data)
        dtype: type = type(data_op)

        if dtype is str:
            self.stack.insert(data=self.registers[data_op])
            self.dprint(f'PUSH {self.registers[data_op]}')
        elif dtype is int:
            self.stack.insert(data=data_op)
            self.dprint(f'PUSH {data_op}')
        else:
            var, loc, offset = data_op
            self.stack.insert(variable=var, data=loc, offset=offset)
            self.dprint(f'PUSH {var}+{offset}')

    def syscall(self) -> None:
        call_type: int = self.stack.get()
        self.dprint(f'syscll n {call_type}')
        #todo
