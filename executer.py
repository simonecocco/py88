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

    def __solveop__(self, op: str) -> Var | str | int: #Var variabile, str è un registro, int un numero
        not_immediate: list[tuple] = re.findall(r'([\d]{0,})([\(]{0,1}[\w\d]{1,}[\)]{0,1}){0,}([-+]{0,1})([\(]{0,1}[\w\d]{1,}[\)]{0,1}){0,}', op)
        number: int = 0
        sign: str | None = ''
        op1: str | None = ''
        op2: str | None = ''

        if len(not_immediate) > 0: # da qua vediamo che tipo di operatore è
            number = not_immediate[0][0]
            sign = not_immediate[0][2]
            op1 = not_immediate[0][1]
            op1 = not_immediate[0][3]
        else:
            raise IllegalOperator(f'{op} non è stato riconosciuto come operatore valido')

        #todo se contiene ( e ) allora...
        #todo deve restituire un valore che poi andrà messo sullo stack (ovviamente andando a restituire quello su cui punta)
        #todo invece se è una variabile ottieni il suo indirizzo
        #todo se è una costante ottieni il suo valore
        #todo se è un registro restituisci il nome registro

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
