from divide_file import *
from stack import Stack
from register import Registers
from colorama import Fore, Back
from executer import Core

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
        self.programstack: Stack = Stack()
        self.registers: Registers = Registers()
        self.core: Core = Core(self.programstack, self.registers, self.program, {'d': self.dprint, 'e': self.eprint, 'o': self.oprint})

    def getText(self) -> list[Instruction]:
        return self.program.text

    def getData(self) -> list[Var]:
        return self.program.data

    def getBSS(self) -> list[Var]:
        return self.program.bss

    def getConstant(self) -> list[Var]:
        return self.program.constants

    # esegue il programm e ritorna il codice di fine
    #todo
    def run(self) -> int:
        for instruction in self.program[TEXT]:
            if 'MOV' in instruction.instruction: #MOV A<-B
                self.core.mov(instruction.op1, instruction.op2)
            elif 'PUSH' in instruction.instruction: #PUSH A
                self.core.push(instruction.op1)
            elif 'SYS' in instruction.instruction: #SYS
                self.core.syscall()
            elif 'ADD' in instruction.instruction: #ADD A<-B
                pass #todo
            elif 'SUB' in instruction.instruction: #SUB A<-B
                pass #todo
            else:
                self.eprint(f'Istruzione non trovata. ({instruction})')
