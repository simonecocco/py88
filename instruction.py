'''
La classe Instruction contiene l'istruzione ed i suoi operandi, in modo da poterli richiamare al bisogno
'''


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
