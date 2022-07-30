'''
py88 è un mini emulatore per il linguaggio assemblativo 8088.

Il file main.py si occupa di inizializzare l'ambiente ricavando le variabili,
validando il file e avviando l'esecuzione
'''

from sys import argv, exit
import file_checker as fc
from py88 import Interpreter


def exec_8088(file: str, debug=False) -> None:
    if not fc.check_file(file):
        print('This file is incompatible with py88 :(')
        exit(1)
    interpreter: Interpreter = Interpreter(file, debug)
    result_code: int = interpreter.run()

print('py88 - emulator for 8088 in python.')
print('Use -h for help')

if '-h' in argv:
    print('''
    Usage: python main.py file_8088.s [OPTIONS]
    Options:
    -d -> debug mode
    -h -> show this message and exit
    ''')
    exit(0)

debug_mode: bool = '-d' in argv
file: str | None = None

for arg in argv:
    if '.s' in arg:
        file = arg
        break

if file is None:
    print('The file must exist and terminate with .s')
    exit(1)

exec_8088(file, debug=debug_mode)

