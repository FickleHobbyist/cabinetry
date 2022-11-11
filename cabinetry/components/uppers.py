"""Module containing concrete components from which to build cabinets"""
from ..config import Config
from ..materials import Material
from ..base import Position, Orientation
from .factory import get_faceframe_factory
from . import ComponentContainer, FaceFrame, RectangularComponent, CabinetCase


class UpperCabinetCase(CabinetCase):
    # BOTTOM_INSET: Distance from bottom of cabinet to underside of bottom panel
    BOTTOM_INSET: float = 1.5
    # TOP_INSET: Distance from top of cabinet to topside of top panel
    TOP_INSET: float = 1.
    MATERIAL_NAILER: Material = Material.HARDWOOD_PAINT_3_4
    MATERIAL_BACK_PANEL: Material = Material.PLY_1_4
    NAILER_WIDTH: float = 2.5

    def __init__(self,
                 width: float,
                 height: float = None,
                 cabinet_depth: float = Config.UPPERS_DEPTH,
                 name: str = 'UpperCabintCase',
                 *args, **kwargs) -> 'UpperCabinetCase':
        clr = kwargs.pop('color', Config.CABINET_CASE_COLOR)
        super().__init__(name=name, color=clr, *args, **kwargs)
        self.width = width
        self.height = height if height is not None else Config.UPPERS_HEIGHT
        self.cabinet_depth = cabinet_depth
        self.material = Config.LOWERS_CASE_MATERIAL

        self.construct_components()

    def get_pv_mesh(self):
        return None

    def construct_components(self) -> None:
        self.box_depth = self.cabinet_depth - Config.FACE_FRAME_MATERIAL.thickness
        self.box_width_inside = self.width - 2*self.material.thickness
        self.box_height_inside = (
            (self.height - (self.TOP_INSET + self.material.thickness)) # lower surface of top panel
            - (self.BOTTOM_INSET + self.material.thickness) # upper surface of bottom panel
            )
        self.box_inside_origin = Position(
            x=self.material.thickness,
            y=0,
            z=self.BOTTOM_INSET+self.material.thickness,
        )
        top_bottom_dado_depth = 0.5 * self.material.thickness
        back_panel_rabbet_width = 0.5 * self.material.thickness
        back_panel_rabbet_depth = self.MATERIAL_BACK_PANEL.thickness

        self.add_child(
            RectangularComponent(
                name='Left Side',
                material=self.material,
                width=self.box_depth,
                height=self.height,
                position=Position(
                    x=self.material.thickness,
                    y=0,
                    z=0
                ),
                orientation=Orientation(
                    rx=0,
                    ry=0,
                    rz=90
                ),
                color=self.color,
            )
        )
        self.add_child(
            RectangularComponent(
                name='Right Side',
                material=self.material,
                width=self.box_depth,
                height=self.height,
                position=Position(
                    x=self.width,
                    y=0,
                    z=0
                ),
                orientation=Orientation(
                    rx=0,
                    ry=0,
                    rz=90
                ),
                color=self.color,
            )
        )
        self.add_child(
            RectangularComponent(
                name='Top',
                material=self.material,
                width=self.box_width_inside + 2*top_bottom_dado_depth,
                height=self.box_depth - back_panel_rabbet_depth,
                position=Position(
                    x=self.material.thickness-top_bottom_dado_depth,
                    y=0,
                    z=self.height - self.TOP_INSET,
                ),
                orientation=Orientation(
                    rx=-90,
                    ry=0,
                    rz=0
                ),
                color=self.color,
            )
        )
        self.add_child(
            RectangularComponent(
                name='Bottom',
                material=self.material,
                width=self.box_width_inside + 2*top_bottom_dado_depth,
                height=self.box_depth - back_panel_rabbet_depth,
                position=Position(
                    x=self.material.thickness-top_bottom_dado_depth,
                    y=0,
                    z=self.BOTTOM_INSET + self.material.thickness
                ),
                orientation=Orientation(
                    rx=-90,
                    ry=0,
                    rz=0
                ),
                color=self.color,
            )
        )
        self.add_child(
            RectangularComponent(
                name='Bottom Nailer',
                material=self.MATERIAL_NAILER,
                width=self.box_width_inside,
                height=self.NAILER_WIDTH,
                position=Position(
                    x=self.material.thickness,
                    y=self.box_depth -
                    (self.MATERIAL_BACK_PANEL.thickness
                     + self.MATERIAL_NAILER.thickness),
                    z=self.BOTTOM_INSET + self.material.thickness,
                ),
                orientation=Orientation(
                    rx=0,
                    ry=0,
                    rz=0
                ),
                color=self.color,
            )
        )
        self.add_child(
            RectangularComponent(
                name='Top Nailer',
                material=self.MATERIAL_NAILER,
                width=self.box_width_inside,
                height=self.NAILER_WIDTH,
                position=Position(
                    x=self.material.thickness,
                    y=self.box_depth -
                    (self.MATERIAL_BACK_PANEL.thickness
                     + self.MATERIAL_NAILER.thickness),
                    z=self.height -
                    (self.TOP_INSET + self.material.thickness + self.NAILER_WIDTH),
                ),
                orientation=Orientation(
                    rx=0,
                    ry=0,
                    rz=0
                ),
                color=self.color,
            )
        )
        self.add_child(
            RectangularComponent(
                name='Back Panel',
                material=self.MATERIAL_BACK_PANEL,
                width=self.box_width_inside + 2*back_panel_rabbet_width,
                height=self.height,
                position=Position(
                    x=self.material.thickness - back_panel_rabbet_width,
                    y=self.box_depth-back_panel_rabbet_depth,
                    z=0
                ),
                orientation=Orientation(
                    rx=0,
                    ry=0,
                    rz=0
                ),
                color=self.color,
            )
        )

    def __repr__(self) -> str:
        return f"{self.__class__.name}(name={self.name}, width={self.width}, pos={self.position})"


class UpperCabinet(ComponentContainer):
    """Container class composed of UpperCabinetCase, FaceFrame, DrawerFaces, etc."""

    def __init__(self, width: float,
                 height: float = Config.UPPERS_HEIGHT,
                 depth: float = Config.UPPERS_DEPTH,
                 name='UpperCabinet',
                 frame_factory: callable = get_faceframe_factory('N-Door-Horiz'),
                 frame_args: dict = {'door_dist': [
                     1]*2, 'dist_type': ['weighted']*2},
                 *args, **kwargs):
        super().__init__(name=name,
                         *args, **kwargs)
        self.width = width
        self.height = height
        self.depth = depth
        self.frame_factory = frame_factory
        self.frame_args = frame_args
        self.construct_components()

    def construct_components(self):
        self.case = UpperCabinetCase(
            width=self.width - 2*Config.FACE_FRAME_OVERHANG,
            height=self.height,
            cabinet_depth=self.depth,
            color=Config.CABINET_CASE_COLOR,
            position=Position(  # x=width, y=thickness, z=height
                x=Config.FACE_FRAME_OVERHANG,
                y=Config.FACE_FRAME_MATERIAL.thickness,
                z=0,
            ),
        )
        self.add_child(self.case)
        
        width_stile = Config.FACE_FRAME_MEMBER_WIDTH

        self.face: FaceFrame = self.frame_factory(
            box_width=self.case.width,
            box_height=0,  # ignore
            height=self.height,
            box_material=self.case.material,
            side_overhang=Config.FACE_FRAME_OVERHANG,
            padding=(
                width_stile,
                self.case.BOTTOM_INSET+self.case.material.thickness,
                width_stile,
                self.case.TOP_INSET+self.case.material.thickness,
            ),
            **self.frame_args,
        )
        self.face.construct_components()
        self.add_child(self.face)
