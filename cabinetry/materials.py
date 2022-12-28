from aenum import Enum, NoAlias


class Material(Enum):
    _settings_ = NoAlias

    """Simple enumeration class representing common cabinet material types and thicknesses"""
    PLY_3_4_4x8 = (23 / 32, 'area', 4608, 0.80, 'sheets')
    PLY_3_4_4x8_VNR = (23 / 32, 'area', 4608, 0.80, 'sheets')
    PLY_3_4_5x5 = (23 / 32, 'area', 3600, 0.80, 'sheets')
    PLY_5_8_4x8 = (19 / 32, 'area', 4608, 0.80, 'sheets')
    PLY_1_2_4x8 = (15 / 32, 'area', 4608, 0.80, 'sheets')
    PLY_1_2_5x5 = (15 / 32, 'area', 3600, 0.80, 'sheets')
    PLY_3_8_4x8 = (11 / 32, 'area', 4608, 0.80, 'sheets')
    PLY_1_4_LITERAL_4x8 = (1 / 4, 'area', 4608, 0.80, 'sheets')
    PLY_1_4_4x8 = (15 / 64, 'area', 4608, 0.80, 'sheets')
    PLY_1_4_5x5 = (15 / 64, 'area', 3600, 0.80, 'sheets')
    HARDWOOD_PAINT_3_4 = (3 / 4, 'volume', 144, 0.80, 'board ft')
    HARDWOOD_STAIN_1_4 = (1 / 4, 'volume', 144, 0.80, 'board ft')
    HARDWOOD_STAIN_3_4 = (3 / 4, 'volume', 144, 0.80, 'board ft')
    HARDWOOD_STAIN_6_4_S2S = (5 / 4, 'volume', 144, 0.90, 'board ft')
    HARDWOOD_STAIN_8_4_S2S = (7 / 4, 'volume', 144, 0.90, 'board ft')
    HARDWOOD_BANDING_PLY_3_4 = (23 / 32, 'volume', 144, 0.80, 'board ft')
    NONE_3_4 = (3 / 4, 'volume', 144, 0.80, 'board ft')

    def __init__(self, thickness, unit_type, unit_size, unit_efficiency, unit_descriptor):
        # finished thickness
        self.thickness: float = thickness
        self.unit_type: str = unit_type
        self.unit_size: float = unit_size
        self.unit_efficiency: float = unit_efficiency
        self.unit_descriptor: str = unit_descriptor
