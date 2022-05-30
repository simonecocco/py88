from Register import Register
import re

class Interpreter:
    def dprint(self, msg):
        if self.debug:
            print(msg)

    def __init__(self, file: str, debug: bool):
        self.debug: bool = debug
        self.program = open(file, 'r')
        self.constants: list | None = None
        self.text: list | None = None
        self.bss: list | None = None
        self.data: list | None = None
        self.dprint(f'opening {file}')
        self.__loadsections__()
        self.program.close()
        self.registers: list = self.__loadregisters__()
        self.__stack__: list = []

    def __loadsections__(self) -> None:
        self.dprint('loading text, bss and data sections')
        program_instructions: list = self.program.readlines()
        current = ''
        for instruction in program_instructions:
            if '--' in instruction:
                instruction = instruction.split('--')[0]
            instruction = instruction.strip()

            if '.SECT .TEXT' in instruction and self.text is None:
                self.dprint('loading text...')
                current = '.TEXT'
                self.text = []
                continue
            elif '.SECT .DATA' in instruction and self.data is None:
                self.dprint('loading data...')
                current = '.DATA'
                self.data = []
                continue
            elif '.SECT .BSS' in instruction and self.bss is None:
                self.dprint('loading bss...')
                current = '.BSS'
                self.bss = []
                continue
            if current == '.TEXT' and self.text is not None:
                if len(instruction) < 2:
                    continue
                self.text.append(instruction)
            elif current == '.DATA' and self.data is not None:
                if len(instruction) < 3:
                    continue
                name: str = instruction.split(':')[0]
                dimension: str | int = instruction.split('.')[1]
                dimension = dimension.split(' ')[0]
                val: str = instruction.split(dimension)[1].strip()
                if 'BYTE' in dimension:
                    dimension = 1
                elif 'WORD' in dimension:
                    dimension = 2
                elif 'LONG' in dimension:
                    dimension = 4
                elif 'ASCII' in dimension:
                    val = val[1:-1]
                    dimension = len(val)
                elif 'ASCIZ' in dimension:
                    val = val[1:-1]
                    dimension = len(val) + 1
                self.data.append({'name': name, 'dim': dimension, 'val': val})
            elif current == '.BSS' and self.bss is not None :
                name: str = instruction.split(':')[0]
                dimension: int = int(instruction.split('.SPACE ')[1])  # todo implement ALIGN and EXTERN
                self.bss.append({'name': name, 'dim': dimension, 'val': None})
            else:
                if self.constants is None:
                    self.constants = []
                if len(instruction) < 3:
                    continue
                name: str = instruction.split('=')[0].strip()
                val: str = instruction.split('=')[1].strip()
                self.constants.append({'name': name, 'val': val})

    def __loadregisters__(self) -> list:
        self.dprint('loading registers')
        r_list: list = [
            Register('AX', 'AH', 'AL'),
            Register('BX', 'BH', 'BL', pointer_holder=True),
            Register('CX', 'CH', 'CL'),
            Register('DX', 'DH', 'DL'),
            Register('SP', pointer_holder=True),
            Register('BP', pointer_holder=True),
            Register('SI', pointer_holder=True),
            Register('DI', pointer_holder=True)
        ]
        return r_list

    def __solveregister__(self, value: str):
        for

    def __getoperands__(self, instruction: str) -> list:
        ret: list = []
        if ' ' in instruction:
            instr: str = instruction.split(' ')[0]
            operands: list = [op.strip() for op in instruction.split(' ')[0].split(',')]
            ret = [instr] + operands
        else:
            ret = [instruction]
        return ret

    def __syscall__(self):
        syscall_n = self.__stack__.pop(-1)
        self.dprint(f'Exec syscall n{syscall_n}')

        if syscall_n == 127: # printf
            format: str = self.__stack__.pop(-1)
            params: list = re.findall('/%[A-Za-z]/', format)
            if len(params) == 0:
                print(format, end='')
                return
            for param in params:
                format = f'{self.__stack__.pop(-1)}'.join(format.split(param, maxsplit=1))

            print(format, end='')

    def run(self):
        for instruction in self.text:
            cmd, op = self.__getoperands__(instruction)
            if 'PUSH' == cmd:
                self.__stack__.append(self.__solveregister__(op[0]))
            elif 'SYS' == cmd:
                self.__syscall__()
            else:
                continue
