from divide_file import *
from stack import Stack
from register import Registers
from colorama import Fore, Back
from executer import Core
from exceptions import *


class Interpreter:
    def dprint(self, msg: str) -> None:
        if self.debug:
            print(Fore.YELLOW + msg + Fore.RESET)

    def eprint(self, msg: str) -> None:
        print(Back.RED + msg + Back.RESET)

    def oprint(self, msg: str) -> None:
        print(Fore.GREEN + msg + Fore.RESET)

    def __init__(self, file: str, debug: bool):
        self.debug: bool = debug
        self.program: Program = Program(file, {'d': self.dprint, 'e': self.eprint, 'o': self.oprint})
        self.registers: Registers = Registers()
        self.programstack: Stack = Stack(self.registers)
        self.core: Core = Core(self.programstack, self.registers, self.program, {'d': self.dprint, 'e': self.eprint, 'o': self.oprint})

    def getText(self) -> list[Instruction]:
        return self.program.text

    def getData(self) -> list[Var]:
        return self.program.data

    def getBSS(self) -> list[Var]:
        return self.program.bss

    def getConstant(self) -> list[Var]:
        return self.program.constants

    def __getlabeladdress__(self, label: str) -> int:
        for i in range(len(self.program[TEXT])):
            instr: Instruction = self.program[TEXT][i]
            if instr.tag == label:
                return i

        raise IllegalMemoryAddress(f'Etichetta non presente ({label})')

    # esegue il programm e ritorna il codice di fine
    def run(self, start_address: int = 0) -> int:
        instr: list = self.program[TEXT]
        offset: int = start_address
        for address in range(len(instr)):
            instruction: Instruction = instr[address + offset]
            if 'MOV' in instruction.instruction: #MOV A<-B
                self.core.mov(instruction.op1, instruction.op2)
            elif 'PUSH' in instruction.instruction: #PUSH A
                self.core.push(instruction.op1)
            elif 'SYS' in instruction.instruction: #SYS
                self.core.syscall()
            elif 'ADD' in instruction.instruction: #ADD A<-B
                self.core.add(instruction.op1, instruction.op2)
            elif 'SUB' in instruction.instruction: #SUB A<-B
                self.core.sub(instruction.op1, instruction.op2)
            elif 'CALL' in instruction.instruction: #CALL
                target_address: int = self.__getlabeladdress__(instruction.op1)
                self.dprint(f'chiamata a funzione {instruction.op1} all\'indirizzo {target_address}')
                self.core.stackbackup()
                self.core.saveretaddress(address)
                self.run(target_address)
                self.core.restorestack()
                self.dprint(f'funzione terminata')
            elif 'XOR' in instruction.instruction: #xor
                self.core.xor(instruction.op1, instruction.op2)
            elif 'CMP' in instruction.instruction:
                self.core.cmp(instruction.op1, instruction.op2)
            elif self.cmpjump(instruction.instruction, True):
                if self.cmpjump(instruction.instruction):
                    target_address: int = self.__getlabeladdress__(instruction.op1)
                    self.dprint(f'salto condizionato a {instruction.op1} ({target_address})')
                    offset = target_address - address
            elif 'MUL' in instruction.instruction:
                self.core.mul(instruction.op1, b='MULB' in instruction.instruction)
            elif 'DIV' in instruction.instruction:
                self.core.div(instruction.op1, b='DIVB' in instruction.instruction)
            elif 'JMP' in instruction.instruction:
                target_address: int = self.__getlabeladdress__(instruction.op1)
                self.dprint(f'salto incondizionato a {instruction.op1} ({target_address})')
                offset = target_address - address
            elif 'INC' in instruction.instruction:
                self.core.inc(instruction.op1)
            elif 'LOOP' in instruction.instruction:
                if self.core.loopcondition():
                    target_address: int = self.__getlabeladdress__(instruction.op1)
                    self.dprint(f"loop su {instruction.op1} (CX:{self.core.registers['CX']})")
                    offset = target_address - address
            elif 'POP' in instruction.instruction:
                self.core.pop(instruction.op1)
            elif 'RET' in instruction.instruction:
                return 0
            elif 'AND' in instruction.instruction:
                self.core.andl(instruction.op1, instruction.op2)
            elif 'OR' in instruction.instruction:
                self.core.orl(instruction.op1, instruction.op2)
            else:
                raise IllegalInstruction(f'Istruzione non supportata o inesistente. ({instruction})')

    def cmpjump(self, jumptype: str, test: bool = True) -> bool:
        if 'JCXZ' in jumptype:
            if test:
                return True
            return self.core.jcxz()
        elif 'JNA' in jumptype or 'JBE' in jumptype:
            if test:
                return True
            return self.core.je() or self.core.jl()
        elif 'JNB' in jumptype or 'JAE' in jumptype or 'JNC' in jumptype:
            if test:
                return True
            return self.core.je() or self.core.jg()
        elif 'JE' in jumptype or 'JZ' in jumptype:
            if test:
                return True
            return self.core.je()
        elif 'JNLE' in jumptype or 'JG' in jumptype:
            if test:
                return True
            return self.core.jg()
        elif 'JGE' in jumptype or 'JNL' in jumptype:
            if test:
                return True
            return self.core.je() or self.core.jg()
        elif 'JO' in jumptype:
            if test:
                return True
            return self.core.jo()
        elif 'JS' in jumptype:
            if test:
                return True
            return self.core.jl()
        elif 'JB' in jumptype or 'JNAE' in jumptype or 'JC' in jumptype:
            if test:
                return True
            return self.core.jl()
        elif 'JNBE' in jumptype or 'JA' in jumptype:
            if test:
                return True
            return self.core.jg()
        elif 'JNE' in jumptype or 'JNZ' in jumptype:
            if test:
                return True
            return self.core.jg() or self.core.jl()
        elif 'JL' in jumptype or 'JNGE' in jumptype:
            if test:
                return True
            return self.core.jl()
        elif 'JLE' in jumptype or 'JNG' in jumptype:
            if test:
                return True
            return self.core.je() or self.core.jl()
        elif 'JNO' in jumptype:
            if test:
                return True
            return not self.core.jo()
        elif 'JNS' in jumptype:
            if test:
                return True
            return not self.core.je() or self.core.jg()
