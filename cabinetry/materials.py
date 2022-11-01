from enum import Enum


class Material(Enum):
    PLY_3QTR = 23 / 32
    PLY_HALF = 15 / 32
    PLY_QTR = 1/4
    HARDWOOD_3QTR = 3/4

    def __init__(self, thickness):
        self.thickness: float = thickness
