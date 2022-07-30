'''
la classe core esegue le istruzioni andando a modificare stack, registri e i valori in memoria
'''

import re
import sys

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

    def __getmemoryaddress__(self, address: int, includeconstants: bool = False) -> list[Var, int]:  # ritorna la variabile che contiene il dato richiesto
        loc: int = 0
        var: Var | None = None
        for item in self.data.getglobalmemory(includeconstants):
            if address == loc or (loc < address < loc + item.size):
                var = item
                break
            loc += item.size
        else:
            raise IllegalMemoryAddress(f'Indirizzo non valido ({address})')
        return [var, loc]

    def __getvaluefrommemory__(self, name: str, includeconstants: bool = True) -> list[Var, int]:  # spazio di memoria, indirizzo
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

    def __getint__(self, op: list[int, int] | str | int) -> int:
        t: type = type(op)
        value: int

        if t is str:
            value = self.registers[op]
        elif t is int:
            value = op
        else:
            value = sum(op)

        return value

    def __assignint__(self, dest: list[int, int] | str | int, src: int) -> None:
        t: type = type(dest)

        if t is str:
            self.registers[dest] = src
        elif t is list:
            effective_address: int = sum(dest)
            var, loc = self.__getmemoryaddress__(effective_address)
            var.value = src
        else:
            raise IllegalOperator(f'la destinazione non può essere una costante ({dest})')

    def stackbackup(self):
        self.stack.__backup__()

    def restorestack(self):
        self.stack.__restore__()

    def saveretaddress(self, current_address: int) -> None:
        self.stack.insert(data=current_address)

    def __solveop__(self, op: str, includeconstants: bool = True) -> list[int, int] | str | int:  # Var variabile locazione e offset, str è un registro, int un numero
        ops_regex: str = r'([0-9]{0,})([\(]{0,}[\w\d]{1,}[\)]{0,}){0,1}([\s\-\+]{0,})([\(]{0,}[\w\d]{1,}[\)]{0,}){0,1}'
        number, op1, sign, op2 = re.findall(ops_regex, op)[0]

        if number == '0' and re.search(r'(x[A-Fa-f0-9]{1,}|b[01]{1,}|o[0-7]{1,})', op1) is not None:
            number += op1
            op1 = ''

        try:
            offset: int
            if op1 != '' and '(' not in op1 and ')' not in op1 and sign == '' and op2 == '':
                offset: int = 0
                if number != '':
                    offset = self.__toint__(number)
                if self.registers.isregister(op1):
                    return op1
                var, loc = self.__getvaluefrommemory__(op1, includeconstants)
                if var in self.data.constants:
                    return var.value
                return loc + offset
            elif '(' in op1 and ')' in op1:  # MOV 4(op), ...
                op1 = op1.replace('(', '').replace(')', '')
                var: Var
                loc: int
                offset: int = 0
                if number != '':
                    offset = self.__toint__(number)
                if self.registers.isregister(op1):
                    var, loc = self.__getmemoryaddress__(self.registers[op1], includeconstants)
                else:
                    var, loc = self.__getvaluefrommemory__(op1, includeconstants)
                return [loc, offset]
            elif op1 != '' and op2 != '' and sign == '':  # ottiene il valore presente nella memoria
                op1 = op1.replace('(', '').replace(')', '')
                op2 = op2.replace('(', '').replace(')', '')
                op1_a: int
                op2_a: int
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
                effective_address: int = op1_a + op2_a + num
                var, loc = self.__getmemoryaddress__(effective_address)
                offset = effective_address - loc
                return [loc, offset]
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
        except:
            self.dprint(f'errore in solveop:\nn:{number} op1:{op1} sign:{sign} op2:{op2}')
            sys.exit(1)

    def mov(self, dest: str, src: str) -> None:
        self.dprint(f'MOV {dest}, {src}')
        dest_op: list[int, int] | str | int = self.__solveop__(dest, False)
        src_op: list[int, int] | str | int = self.__solveop__(src)

        value: int = self.__getint__(src_op)

        self.__assignint__(dest_op, value)

    def push(self, data: str) -> None:
        data_op: list[int, int] | str | int = self.__solveop__(data)
        dtype: type = type(data_op)

        if dtype is str:
            self.stack.insert(data=self.registers[data_op])
            self.dprint(f'PUSH {self.registers[data_op]}')
        elif dtype is int:
            self.stack.insert(data=data_op)
            self.dprint(f'PUSH {data_op}')
        else: #deprecato
            var, loc, offset = data_op
            self.stack.insert(variable=var, data=loc, offset=offset)
            self.dprint(f'PUSH {var}+{offset}')

    def syscall(self) -> None:
        call_type: int = self.stack.remove()
        self.dprint(f'syscall n {call_type}')
        if call_type == 1: #exit
            exit_code: int = self.stack.get()
            self.dprint(f'Uscita con codice {exit_code}')
            sys.exit(exit_code)
        elif call_type == 4: #write
            out_buffer: int = self.stack.remove()
            buffer: str = str(self.__getmemoryaddress__(self.stack.remove())[0])
            nchars: int = self.stack.remove()
            if out_buffer != 1: #non è STDOUT #todo implementa
                raise IllegalOperator(f'Metodo non ancora supportato (write su {out_buffer})')
            else:
                dim: int = min(len(buffer), nchars)
                buffer = buffer[:dim]
                self.oprint(buffer)
        elif call_type == 117:
            c: str = str(input('')).strip()

            if len(c) < 1:
                self.eprint(f'Input vuoto')
                self.registers['AX'] = -1
            else:
                self.registers['AL'] = ord(c[0])
                self.registers['AH'] = 0
        elif call_type == 127: #printf
            var, loc = self.__getmemoryaddress__(self.stack.remove())
            str_printf: str = var.value
            splitted_string: list[str] = re.split(r'%[dsc]', str_printf)
            formatted_args: list[str] = re.findall(r'%[dsc]', str_printf)
            str_printf = ''
            for (splt, arg) in zip(splitted_string[:-1], formatted_args):
                str_printf += splt
                if arg == '%d':
                    str_printf += str(self.stack.remove())
                elif arg == '%s':
                    tmp, tmploc = self.__getmemoryaddress__(self.stack.remove())
                    str_printf += tmp.value
                elif arg == '%c':
                    str_printf += chr(self.stack.remove())
                else:
                    str_printf += arg
            str_printf += splitted_string[-1]
            self.oprint(str_printf)
        #todo implementa elif call_type == 3 #read
        #todo implementa elif call_type == 6: #close
        #todo implementa elif call_type == 5 #open
        #todo implementa elif call_type == 8 #create
        #todo implementa elif call_type == 19 #lseek
        #todo implementa elif call_type == 122 #putchar
        #todo implementa elif call_type == 121 #sprintf
        #todo implementa elif call_type == 125 #sscanf
        else:
            raise IllegalOperator(f'Syscall non valida o non implementata. ({call_type})')

    def add(self, op1: str, op2: str) -> None:
        dest: list[int, int] | str | int = self.__solveop__(op1, False)
        src: list[int, int] | str | int = self.__solveop__(op2)

        value: list[int] = [self.__getint__(dest), self.__getint__(src)]

        self.dprint(f'{op1}+{op2}={sum(value)}')

        self.__assignint__(dest, sum(value))

    def sub(self, op1: str, op2: str) -> None:
        dest: list[int, int] | str | int = self.__solveop__(op1, False)
        src: list[int, int] | str | int = self.__solveop__(op2)

        value: list[int] = [self.__getint__(dest), -self.__getint__(src)]

        self.dprint(f'{op1}-{op2}={sum(value)}')

        self.__assignint__(dest, sum(value))

    def xor(self, op1: str, op2: str) -> None:
        dest: list[int, int] | str | int = self.__solveop__(op1, False)
        src: list[int, int] | str | int = self.__solveop__(op2)

        value: list[int] = [self.__getint__(dest), self.__getint__(src)]

        self.dprint(f'{op1}^{op2}={value[0]^value[1]}')

        self.__assignint__(dest, value[0] ^ value[1])

    def cmp(self, op1: str, op2: str) -> None:
        a: list[int, int] | str | int = self.__solveop__(op1, False)
        b: list[int, int] | str | int = self.__solveop__(op2)

        value: list[int] = [self.__getint__(a), self.__getint__(b)]

        self.dprint(f'{a} CMP {b}')

        #0x1 a < b
        #0x2 a == b
        #0x4 a > b
        #0x8 overflow

        a, b = value
        self.registers['CMP'] = 0
        if a < b:
            self.registers['CMP'] = 0x1
        if a == b:
            self.registers['CMP'] = 0x2
        if a > b:
            self.registers['CMP'] = 0x4
        s: int = a + b
        if (s & 0xFFFF) > 0:
            self.registers['CMP'] = 0x8

    def jcxz(self) -> bool:
        return self.registers['CX'] == 0

    def jl(self) -> bool:
        return (self.registers['CMP'] & 0x1) > 0

    def je(self) -> bool:
        return (self.registers['CMP'] & 0x2) > 0

    def jg(self) -> bool:
        return (self.registers['CMP'] & 0x4) > 0

    def jo(self) -> bool:
        return (self.registers['CMP'] & 0x8) > 0

    def mul(self, op: str, b: bool = False):
        a: int = self.__getint__(self.__solveop__(op))
        reg: str = 'AX' if not b else 'AL'
        b: int = self.registers[reg]

        self.dprint(f'{op}*{reg}={a * b}')

        self.__assignint__(reg, a*b)

    def div(self, op: str, b: bool = False):
        a: int = self.__getint__(self.__solveop__(op))
        reg1: str = 'AX' if not b else 'AL'
        reg2: str = 'DX' if not b else 'AH'
        b: int = self.registers[reg1]

        div_value: int = 0 if b == 0 else a // b
        mod_value: int = 0 if b == 0 else a % b
        if b == 0:
            self.dprint(f'Divisione per 0! ({reg2})')

        self.dprint(f'{op}/{reg1}={div_value},{op}%{reg2}={mod_value}')

        self.__assignint__(reg1, div_value)
        self.__assignint__(reg2, mod_value)

    def inc(self, op: str):
        dest: list[int, int] | str | int = self.__solveop__(op, False)

        value: int = self.__getint__(dest) + 1

        self.dprint(f'{op}++')

        self.__assignint__(dest, value)

    def loopcondition(self) -> bool:
        if self.registers['CX'] >= 0:
            self.registers['CX'] = self.registers['CX'] - 1
            return True and self.registers['CX'] != 0xFFFF
        return False

    def pop(self, op: str):
        if op != '':
            dest: list[int, int] | str | int = self.__solveop__(op, False)
            self.__assignint__(dest, self.stack.remove())
        else:
            self.stack.remove()

    def andl(self, op1: str, op2: str) -> None:
        dest: list[int, int] | str | int = self.__solveop__(op1, False)
        src: list[int, int] | str | int = self.__solveop__(op2)

        value: list[int] = [self.__getint__(dest), self.__getint__(src)]

        self.dprint(f'{op1}&{op2}={value[0]&value[1]}')

        self.__assignint__(dest, value[0] & value[1])

    def orl(self, op1: str, op2: str) -> None:
        dest: list[int, int] | str | int = self.__solveop__(op1, False)
        src: list[int, int] | str | int = self.__solveop__(op2)

        value: list[int] = [self.__getint__(dest), self.__getint__(src)]

        self.dprint(f'{op1}|{op2}={value[0]|value[1]}')

        self.__assignint__(dest, value[0] | value[1])

    def neg(self, op: str):
        dest: list[int, int] | str | int = self.__solveop__(op, False)

        value: int = self.__getint__(dest)

        self.dprint(f'~{op}')

        self.__assignint__(dest, ~value)

    def dec(self, op: str):
        dest: list[int, int] | str | int = self.__solveop__(op, False)

        value: int = self.__getint__(dest) - 1

        self.dprint(f'{op}--')

        self.__assignint__(dest, value)
