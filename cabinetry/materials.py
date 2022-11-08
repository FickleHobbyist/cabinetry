from enum import Enum


class Material(Enum):
    """Simple enumeration class representing common cabinet material types and thicknesses"""
    PLY_3_4 = 23 / 32
    PLY_5_8 = 19 / 32
    PLY_1_2 = 15 / 32
    PLY_3_8 = 11 / 32
    PLY_1_4 = 1 / 4
    HARDWOOD_3_4 = 3 / 4
    HARDWOOD_LIKE_PLY_3_4 = 23 / 32

    def __init__(self, thickness):
        self.thickness: float = thickness
