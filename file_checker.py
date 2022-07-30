'''
file_checker.py si occupa di controllare se il file esiste, se non è una directory e se il file è leggibile
'''

import os


def check_file(file: str) -> bool:
    return os.path.exists(file) and os.path.isfile(file) and os.access(file, os.R_OK)
