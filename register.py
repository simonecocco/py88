'''
La classe che gestisce tutta la parte dei registri.
Consente di memorizzare un valore tramite registers[x] = y
E di leggere il registro y = registers[x]
Ogni registro è unsigned int da 2 byte, supporta anche i registri HL da 1 byte (unsigned char)
'''

import sys
from colorama import Back


class Registers:
    def __init__(self):
        self.registers: dict[str: int] = {
            'AX': 0,
            'BX': 0,
            'CX': 0,
            'DX': 0,
            'SP': 0,
            'BP': 0,
            'SI': 0,
            'DI': 0,
            'CMP': 0
        }

    def __callerror__(self, registername: str) -> None:
        print(Back.RED + f'Questo registro non esiste. ({registername})' + Back.RESET)
        sys.exit(1)

    def isregister(self, regname: str) -> bool:
        regname = regname.replace('H', 'X').replace('L', 'X')
        return regname in self.registers.keys()

    def __setitem__(self, regname, value):
        try:
            if 'H' in regname or 'L' in regname:
                original_register: str = regname.replace('H', 'X').replace('L', 'X')
                value &= 0xFF #prevengo più di 1 byte
                if 'H' in regname:
                    self.registers[original_register] &= 0x00FF
                    self.registers[original_register] |= (value << 8)
                else:
                    self.registers[original_register] &= 0xFF00
                    self.registers[original_register] |= value
            else:
                value &= 0xFFFF #prevengo più di 2 byte
                self.registers[regname] = value
        except KeyError:
            self.__callerror__(regname)

    def __getitem__(self, item):
        try:
            if 'H' in item or 'L' in item:
                original_register: str = item.replace('H', 'X').replace('L', 'X')
                value: int = self[original_register]
                if 'H' in item:
                    return (value & 0xFF00) >> 8
                else:
                    return value & 0xFF
            else:
                return self.registers[item]
        except KeyError:
            self.__callerror__(item)
