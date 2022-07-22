import re
import sys

TEXT: str = 'TEXT'
BSS: str = 'BSS'
DATA: str = 'DATA'
CONSTANT: str = 'CONSTANT'
NONE: str = 'NONE'
TYPE: dict[str, int] = {NONE: -1, TEXT: 0, BSS: 1, DATA: 2, CONSTANT: 3}


class Instruction:
    def __init__(self, instruction: str, op1: str | None = None, op2: str | None = None, tag: str | None = None):
        self.instruction: str = instruction
        self.op1: str | None = op1
        self.op2: str | None = op2
        self.tag: str | None = tag
        if self.tag == '':
            self.tag = None
        elif self.tag != '' and self.tag is not None:
            self.tag = self.tag.replace(':', '')

    def __repr__(self):
        rpr: str = ''
        if self.tag is not None and self.tag != '':
            rpr += f'{self.tag}: '
        rpr += f'{self.instruction} '
        if self.op1 is not None and self.op1 != '':
            rpr += self.op1
        if self.op2 is not None and self.op2 != '':
            rpr += ', '+self.op2
        return rpr

    #todo avvia il programma, ti tocca fare bss, data e costanti


class Var:
    def __init__(self, varname: str, size: str, value: str):
        self.varname: str = varname
        self.value: str = value #todo da modificare il tipo di dato
        self.size: str = size #todo da modificare il tipo in dimensione

    def __getsize__(self, size: str, counter: int = 1) -> int:
        size = size.lower()
        if 'int' in size or 'word' in size:
            return 2 * counter
        elif 'byte' in size or 'ascii' in size:
            return 1 * counter
        elif 'long' in size:
            return 4 * counter
        elif 'asciz' in size:
            return (1 * counter) + 1
        elif 'space' in size:
            return counter
        # todo da implementare
        # elif 'align' in size:
        # elif 'extern' in size:

    def __repr__(self):
        return f'{self.varname}: {self.size} {self.value}'


class Program:
    def __init__(self, program_name: str, debug_function):
        self.dprint = debug_function
        self.text: list[Instruction] | None = None
        self.data: list | None = None
        self.bss: list | None = None
        self.constants: list | None = None
        program = open(program_name, 'r')
        program_instructions: list = program.readlines()
        program.close()
        self.__load__(program_instructions)

    # rende l'istruzione leggibile usando lo strip e togliendo i commenti
    def __purifyinstruction__(self, instruction: str) -> str:
        if '--' in instruction:
            instruction = instruction.split('--')[0]
        return instruction.strip()

    # controlla se è una definizione di settore
    def __sector__(self, instruction: str, current_stat: int) -> [bool, int]:
        if '.SECT .TEXT' in instruction and self.text is None:
            self.dprint('Carico il codice')
            self.text = []
            return True, TYPE[TEXT]
        elif '.SECT .DATA' in instruction and self.data is None:
            self.dprint('Carico le costanti')
            self.data = []
            return True, TYPE[DATA]
        elif '.SECT .BSS' in instruction and self.bss is None:
            self.dprint('Carico le variabili')
            self.bss = []
            return True, TYPE[BSS]
        elif len(instruction) > 1 and current_stat == TYPE[NONE]:
            self.dprint('Carico le costanti')
            self.constants = []
            return False, TYPE[CONSTANT]
        else:
            return False, current_stat

    def __parseinstruction__(self, instruction: str, section: int, tag: str | None) -> None:
        if section == TYPE[TEXT] and self.text is not None:
            if len(instruction) > 1:
                instr_param: tuple = re.findall(r'([\w]{1,})[\s]{0,}([\-()\w\d]{0,})[,\s]{0,}([\-()\w\d]{0,})', instruction)[0]
                instr: Instruction = Instruction(*[x.strip() for x in instr_param], tag=tag)
                self.text.append(instr)
        elif section == TYPE[DATA] and self.data is not None:
            if len(instruction) > 3:
                var_param: tuple = re.findall(r'.([\w]{1,})\s([\d\S\s]{1,})', instruction)[0]
                var: Var = Var(*([tag] + [x.strip() for x in var_param]))
                self.data.append(var)
        elif section == TYPE[BSS] and self.bss is not None:
            if len(instruction) > 3:
                var_param: tuple = re.findall(r'.([\w]{1,})\s([\d\S\s]{1,})', instruction)[0]
                var: Var = Var(*([tag] + [x.strip() for x in var_param]))
                self.bss.append(var)
        else:
            if len(instruction) > 3:
                const_param: tuple = re.findall(r'([\S]{1,})[\s]{0,1}=[\s]{0,1}([\w\d]{1,})', instruction)[0]
                const: Var = Var(const_param[0], 'int', const_param[1])
                self.constants.append(const)

    # carica i vari tipi di sezioni
    def __load__(self, instructions: list):
        self.dprint('Carico le varie sezioni')
        current_section: int = TYPE[NONE]
        tag: str | None = None
        for instruction in instructions:
            instruction = self.__purifyinstruction__(instruction)
            sector, current_section = self.__sector__(instruction, current_section)
            if sector:
                continue
            if instruction.endswith(':'):
                tag = instruction
                continue
            if re.search('^[\w]{1,}:', instruction) is not None:
                tmp: list[str] = [x.strip() for x in instruction.split(':')]
                tag = tmp[0]
                instruction = tmp[1]
            self.__parseinstruction__(instruction, current_section, tag)
            tag = None

    def __getitem__(self, item):
        if type(item) == str and item == TEXT:
            return self.text
        if type(item) == str and item == DATA:
            return self.data
        if type(item) == str and item == BSS:
            return self.bss
        if type(item) == str and item == CONSTANT:
            return self.constants
