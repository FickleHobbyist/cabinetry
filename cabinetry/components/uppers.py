"""Module containing concrete components from which to build cabinets"""
from ..config import Config
from ..materials import Material
from ..base import Position, Orientation
from .factory import get_faceframe_factory
from . import ComponentContainer, FaceFrame, RectangularComponent


class UpperCabinetCase(ComponentContainer):
    # BOTTOM_INSET: Distance from bottom of cabinet to underside of bottom panel
    BOTTOM_INSET: float = 1.5
    # TOP_INSET: Distance from top of cabinet to topside of top panel
    TOP_INSET: float = 1.
    MATERIAL_NAILER: Material = Material.HARDWOOD_3_4
    MATERIAL_BACK_PANEL: Material = Material.PLY_1_4
    NAILER_WIDTH: float = 2.5

    def __init__(self,
                 width: float,
                 height: float = None,
                 name: str = 'UpperCabintCase',
                 *args, **kwargs) -> 'UpperCabinetCase':
        clr = kwargs.pop('color', Config.CABINET_CASE_COLOR)
        super().__init__(name=name, color=clr, *args, **kwargs)
        self.width = width
        self.height = height if height is not None else Config.UPPERS_HEIGHT
        self.material = Config.LOWERS_CASE_MATERIAL

        self.construct_components()

    def get_pv_mesh(self):
        return None

    def construct_components(self) -> None:
        box_depth = Config.UPPERS_DEPTH - Config.FACE_FRAME_MATERIAL.thickness
        box_width_inside = self.width - 2*self.material.thickness
        top_bottom_dado_depth = 0.5 * self.material.thickness
        back_panel_rabbet_width = 0.5 * self.material.thickness
        back_panel_rabbet_depth = self.MATERIAL_BACK_PANEL.thickness

        self.add_child(
            RectangularComponent(
                name='Left Side',
                material=self.material,
                width=box_depth,
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
                width=box_depth,
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
                width=box_width_inside + 2*top_bottom_dado_depth,
                height=box_depth - back_panel_rabbet_depth,
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
                width=box_width_inside + 2*top_bottom_dado_depth,
                height=box_depth - back_panel_rabbet_depth,
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
                width=box_width_inside,
                height=self.NAILER_WIDTH,
                position=Position(
                    x=self.material.thickness,
                    y=box_depth -
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
                width=box_width_inside,
                height=self.NAILER_WIDTH,
                position=Position(
                    x=self.material.thickness,
                    y=box_depth -
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
                width=box_width_inside + 2*back_panel_rabbet_width,
                height=self.height,
                position=Position(
                    x=self.material.thickness - back_panel_rabbet_width,
                    y=box_depth-back_panel_rabbet_depth,
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
                 name='UpperCabinet',
                 frame_type: str = 'N-Door',
                 frame_args: dict = {'door_dist': [
                     1]*2, 'dist_type': ['weighted']*2},
                 *args, **kwargs):
        super().__init__(name=name,
                         *args, **kwargs)
        self.width = width
        self.height = height
        self.frame_type = frame_type
        self.frame_args = frame_args
        self.construct_components()

    def construct_components(self):
        self.case = UpperCabinetCase(
            width=self.width,
            height=self.height,
            color=Config.CABINET_CASE_COLOR,
            position=Position(  # x=width, y=thickness, z=height
                x=0,
                y=Config.FACE_FRAME_MATERIAL.thickness,
                z=0,
            ),
        )
        self.add_child(self.case)

        faceframe_side_overhang = 1/8
        ff_factory = get_faceframe_factory(self.frame_type)

        width_stile = Config.FACE_FRAME_MEMBER_WIDTH

        self.face: FaceFrame = ff_factory(
            box_width=self.width,
            box_height=0,  # ignore
            height=self.height,
            box_material=self.case.material,
            side_overhang=faceframe_side_overhang,
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
