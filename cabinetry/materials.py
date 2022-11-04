from enum import Enum


class Material(Enum):
    PLY_3_4 = 23 / 32
    PLY_5_8 = 19 / 32
    PLY_1_2 = 15 / 32
    PLY_3_8 = 11 / 32
    PLY_1_4 = 1 / 4
    HARDWOOD_3_4 = 3 / 4

    def __init__(self, thickness):
        self.thickness: float = thickness
