import re


class Var:
    def __init__(self, varname: str, size: str, value: str):
        self.varname: str = varname
        self.value: str | list | int | None = self.__assigntype__(value)
        self.size: int = 0
        self.elementsize: int = 0
        self.size, self.elementsize = self.__getsize__(size, 1 if type(self.value) == int else len(self.value))
        self.__adjustint__()

    def __adjustint__(self):
        base: int = int('FF'*self.elementsize, 16)
        if type(self.value) is int:
            self.value &= base
        elif type(self.value) is list:
            self.value = [elem & base for elem in self.value]

    def __escapechar__(self, c: str) -> str:
        if '\\n' in c:
            c = c.replace('\\n', '\n')
        if '\\t' in c:
            c = c.replace('\\t', '\t')
        if '\\\\' in c:
            c = c.replace('\\\\', '\\')
        if '\\b' in c:
            c = c.replace('\\b', '\b')
        if '\\r' in c:
            c = c.replace('\\r', '\r')
        if '\\"' in c:
            c = c.replace('\\"', '"')

        return c

    def __toint__(self, number: str) -> int:
        conv: list[str] = re.findall(r'^(0[xX][A-Fa-f0-9]{1,})', number) #hex
        if len(conv) > 0:
            num: int = int(conv[0], 16)
            return num
        conv = re.findall(r'^(0[0-7]{1,})', number) #octal
        if len(conv) > 0:
            num: int = int(conv[0], 8)
            return num
        conv = re.findall(r'^(0b[01]{1,})', number) #binary
        if len(conv) > 0:
            num: int = int(conv[0], 2)
            return num
        conv = re.findall(r'^([0-9]{1,})', number) #decimal
        if len(conv) > 0:
            num: int = int(conv[0])
            return num

    def __assigntype__(self, value: str) -> str | list | int:
        if value.startswith('"') and value.endswith('"'):  # stringa
            value = self.__escapechar__(value)
            return value[1:-1]
        if ',' in value:  # lista
            res: list[int] = [self.__toint__(num.strip()) for num in value.split(',')]
            return res

        return self.__toint__(value)

    def __getsize__(self, size: str, counter: int) -> [int, int]:
        size = size.lower()
        if 'int' in size or 'word' in size:
            return 2 * counter, 2
        elif 'byte' in size or 'ascii' in size:
            return 1 * counter, 1
        elif 'long' in size:
            return 4 * counter, 4
        elif 'asciz' in size:
            self.value += '\0', 1
            return (1 * counter) + 1
        elif 'space' in size:
            dim = self.value
            self.value = None
            return dim, dim
        # da implementare
        # elif 'align' in size:
        # elif 'extern' in size:

    def __repr__(self):
        return f'{self.varname}: {self.size} {self.value}'

    def __str__(self):
        return f'{self.value}'

    def __subdivide__(self, number: int, t: int) -> list[int]:
        r: list[int] = []
        for bytenumber in range(t):
            base: int = int('FF' + ('00' * bytenumber), 16)
            r.append((base & number) >> (8 * bytenumber))
        return r

    def getforstack(self, offset: int = 0) -> list[int]:
        t: type = type(self.value)
        res: list = []
        if t == str:
            return [ord(x) for x in self.value]
        elif t == int:
            res = self.__subdivide__(self.value, self.elementsize)
        elif t == list:
            l: list = []
            for num in self.value:
                l += self.__subdivide__(num, self.elementsize)
            res = l
        res = res[offset:]
        if len(res) % 2 != 0:
            res.append(0)
        return res
