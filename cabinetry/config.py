from .materials import Material


class Config:
    """Configuration class defining common object parameters"""
    # \/\/ General parameters \/\/
    CABINET_CASE_COLOR: str = '#e6cd83'
    FACE_FRAME_COLOR: str = '#6e583b'
    FACE_FRAME_MATERIAL: Material = Material.HARDWOOD_3_4
    FACE_FRAME_MEMBER_WIDTH: float = 1.5

    # \/\/ Lower cabinets configuration \/\/
    COUNTER_HEIGHT: float = 36
    COUNTERTOP_THICKNESS: float = 1.5
    LOWERS_DEPTH: float = 24.
    LOWERS_CASE_MATERIAL: Material = Material.PLY_3_4

    # \/\/ Drawer specific parameters \/\/
    DRAWER_BOX_COLOR: str = '#e6cd83'
    MAX_DRAWER_BOX_HEIGHT: float = 5.

    # \/\/ Door and drawer parameters \/\/
    FRAMED_PANEL_INSET_COLOR: str = '#e6cd83'
    FRAMED_PANEL_INSET_MATERIAL = Material.PLY_1_4
    # OVERLAY_GAP = Gap between door and drawer face elements
    OVERLAY_GAP: float = 1/4

    # \/\/ Upper cabinets configuration \/\/
    # Ceiling height, crown space height, and counter to uppers gap
    # are used to compute total height for upper cabinets
    CEILING_HEIGHT: float = 96.
    CROWN_SPACE_HEIGHT: float = 3.
    COUNTER_TO_UPPERS_GAP: float = 18
    UPPERS_DEPTH: float = 12.
    UPPERS_CASE_MATERIAL: Material = Material.PLY_3_4
    UPPERS_HEIGHT: float = (CEILING_HEIGHT - (
                            CROWN_SPACE_HEIGHT
                            + COUNTER_TO_UPPERS_GAP
                            + COUNTER_HEIGHT))

