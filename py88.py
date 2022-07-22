from divide_file import *


class Interpreter:
    def dprint(self, msg):
        if self.debug:
            print(msg)

    def __init__(self, file: str, debug: bool):
        self.debug: bool = debug
        self.program: Program = Program(file, self.dprint)

    # esegue il programm e ritorna il codice di fine
    def run(self) -> int:
        #todo
        pass

    def getText(self) -> list[Instruction]:
        return self.program.text

    def getData(self) -> list[Var]:
        return self.program.data

    def getBSS(self) -> list[Var]:
        return self.program.bss

    def getConstant(self) -> list[Var]:
        return self.program.constants
