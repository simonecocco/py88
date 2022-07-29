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

    def __getlabeladdress__(self, label: str) -> int:
        for i in range(len(self.program[TEXT])):
            instr: Instruction = self.program[TEXT][i]
            if instr.tag == label:
                return i

    # esegue il programm e ritorna il codice di fine
    def run(self, start_address: int = 0) -> int:
        instr: list = self.program[TEXT][start_address:]
        for address in range(len(instr)):
            instruction: Instruction = instr[address]
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
            elif 'JCXZ' in instruction.instruction:
                if self.core.jcxz():
                    target_address: int = self.__getlabeladdress__(instruction.op1)
                    self.dprint(f'salto condizionato a {instruction.op1} ({target_address})')
                    self.run(target_address)
            elif 'JNA' in instruction.instruction or 'JBE' in instruction.instruction:
                if self.core.je() or self.core.jl():
                    target_address: int = self.__getlabeladdress__(instruction.op1)
                    self.dprint(f'salto condizionato a {instruction.op1} ({target_address})')
                    self.run(target_address)
            elif 'JNB' in instruction.instruction or 'JAE' in instruction.instruction or 'JNC' in instruction.instruction:
                if self.core.je() or self.core.jg():
                    target_address: int = self.__getlabeladdress__(instruction.op1)
                    self.dprint(f'salto condizionato a {instruction.op1} ({target_address})')
                    self.run(target_address)
            elif 'JE' in instruction.instruction or 'JZ' in instruction.instruction:
                if self.core.je():
                    target_address: int = self.__getlabeladdress__(instruction.op1)
                    self.dprint(f'salto condizionato a {instruction.op1} ({target_address})')
                    self.run(target_address)
            elif 'JNLE' in instruction.instruction or 'JG' in instruction.instruction:
                if self.core.jg():
                    target_address: int = self.__getlabeladdress__(instruction.op1)
                    self.dprint(f'salto condizionato a {instruction.op1} ({target_address})')
                    self.run(target_address)
            elif 'JNB' in instruction.instruction or 'JAE' in instruction.instruction or 'JNC' in instruction.instruction:
                if self.core.je() or self.core.jg():
                    target_address: int = self.__getlabeladdress__(instruction.op1)
                    self.dprint(f'salto condizionato a {instruction.op1} ({target_address})')
                    self.run(target_address)
            else:
                raise IllegalInstruction(f'Istruzione non supportata o inesistente. ({instruction})')

    def cmpjump(self, instruction: Instruction):
        pass #todo metti qua tutte le istruzioni di salto
