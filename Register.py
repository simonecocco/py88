from IllegalRegister import IllegalRegister

class Register:
    def __init__(self, name: str, high_name: str|None=None, low_name: str|None=None, pointer_holder: bool=False):
        self.name: str = name
        self.h_name: str | None = high_name
        self.l_name: str | None = low_name
        self.can_hold_point: bool = pointer_holder
        self.value: int = 0

    def set(self, value: int):
        self.value = value

    def set_h(self, h: int):
        if self.h_name is None:
            raise IllegalRegister(f'the higher register didn\'t exist in {self.name}')
        self.value += h << 8

    def set_l(self, l: int):
        if self.l_name is None:
            raise IllegalRegister(f'the lower register didn\'t exist in {self.name}')
        self.value += l

    def get(self) -> int:
        return self.value

    def get_h(self) -> int:
        return self.value >> 8

    def get_l(self) -> int:
        return self.value & 0xFF
