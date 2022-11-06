"""Module containing concrete components from which to build cabinets"""
from ..config import Config
from ..base import Position, Orientation
from . import ComponentContainer, FaceFrame, RectangularComponent
from .factory import get_faceframe_factory


class LowerCabinetCase(ComponentContainer):
    TOEKICK_HEIGHT = 3.5  # TO_BOTTOM_OF FACEFRAME
    TOEKICK_DEPTH = 2.5
    STRETCHER_WIDTH = 2.5
    FLOOR_DADO_DEPTH = 0.375
    DADO_HEIGHT_ABOVE_TOEKICK_CUTOUT = 0.5
    CABINET_DEPTH = Config.LOWERS_DEPTH

    def __init__(self,
                 width: float,
                 height: float = None,
                 name='LowerCabinetCase',
                  *args, **kwargs) -> None:
        clr = kwargs.pop('color', Config.CABINET_CASE_COLOR)
        super().__init__(
            name=name, color=clr, *args, **kwargs)
        self.width = width
        self.height = height if height is not None else (
            Config.COUNTER_HEIGHT - Config.COUNTERTOP_THICKNESS)
        self.material = Config.LOWERS_CASE_MATERIAL

        self.construct_components()

    def construct_components(self) -> None:
        # Top surface of bottom panel
        self.bottom_height_above_floor = self.TOEKICK_HEIGHT + Config.FACE_FRAME_MEMBER_WIDTH
        box_depth = self.CABINET_DEPTH - Config.FACE_FRAME_MATERIAL.thickness
        box_width_inside = self.width - 2*self.material.thickness

        toekick_cutout_height = (self.bottom_height_above_floor -
                                 self.material.thickness - self.DADO_HEIGHT_ABOVE_TOEKICK_CUTOUT)
        base_block_height = self.bottom_height_above_floor - self.material.thickness

        self.add_child(
            RectangularComponent(
                name='Left Side',
                material=self.material,
                width=box_depth,
                height=self.height,
                position=Position(x=self.material.thickness, y=0, z=0),
                orientation=Orientation(0, 0, 90),
                color=self.color,
            )
        )
        self.add_child(
            RectangularComponent(
                name='Right Side',
                material=self.material,
                width=box_depth,
                height=self.height,
                position=Position(x=self.width, y=0, z=0),
                orientation=Orientation(0, 0, 90),
                color=self.color,
            )
        )
        self.add_child(
            RectangularComponent(
                name='Bottom',
                material=self.material,
                width=box_width_inside + 2*self.FLOOR_DADO_DEPTH,
                height=box_depth,
                position=Position(
                    x=self.material.thickness-self.FLOOR_DADO_DEPTH,
                    y=0,
                    z=self.bottom_height_above_floor
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
                name='Toekick',
                material=self.material,
                width=self.width,
                height=toekick_cutout_height,
                position=Position(
                    x=0,
                    y=self.TOEKICK_DEPTH,
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
        self.add_child(
            RectangularComponent(
                name='Base Block - Front',
                material=self.material,
                width=box_width_inside,
                height=base_block_height,
                position=Position(
                    x=self.material.thickness,
                    y=self.TOEKICK_DEPTH+self.material.thickness,
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
        self.add_child(
            RectangularComponent(
                name='Base Block - Rear',
                material=self.material,
                width=box_width_inside,
                height=base_block_height,
                position=Position(
                    x=self.material.thickness,
                    y=box_depth-self.material.thickness,
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
        self.add_child(
            RectangularComponent(
                name='Top Stretcher - Front',
                material=self.material,
                width=box_width_inside,
                height=self.STRETCHER_WIDTH,
                position=Position(
                    x=self.material.thickness,
                    y=0,
                    z=self.height
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
                name='Top Stretcher - Rear (Horiz)',
                material=self.material,
                width=box_width_inside,
                height=self.STRETCHER_WIDTH,
                position=Position(
                    x=self.material.thickness,
                    y=box_depth-self.STRETCHER_WIDTH,
                    z=self.height
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
                name='Top Stretcher - Rear (Vert)',
                material=self.material,
                width=box_width_inside,
                height=self.STRETCHER_WIDTH,
                position=Position(
                    x=self.material.thickness,
                    y=box_depth - self.material.thickness,
                    z=(self.height -
                       (self.material.thickness + self.STRETCHER_WIDTH))
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


class LowerCabinet(ComponentContainer):
    """Container class composed of LowerCabinetCase, FaceFrame, DrawerFaces, etc."""

    def __init__(self, width: float = 36,
                 height: float = 34.5,
                 name='LowerCabinet',
                 frame_type: str = 'N-Drawer',
                 frame_args: dict = {'drawer_dist': [
                     1]*4, 'dist_type': ['weighted']*4},
                 *args, **kwargs):
        super(LowerCabinet, self).__init__(name=name,
                                           *args, **kwargs)
        self.width = width
        self.height = height
        self.frame_type = frame_type
        self.frame_args = frame_args
        self.construct_components()

    def construct_components(self):
        self.clear_children()
        self.case = LowerCabinetCase(
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

        if self.frame_type is not None:
            faceframe_side_overhang = 1/8
            ff_factory = get_faceframe_factory(self.frame_type)

            self.face: FaceFrame = ff_factory(
                box_width=self.width,
                box_height=(self.height -
                            (self.case.bottom_height_above_floor-self.case.material.thickness)),
                box_material=self.case.material,
                side_overhang=faceframe_side_overhang,
                **self.frame_args,
            )
            self.face.position.z = self.case.TOEKICK_HEIGHT

            self.face.construct_components()
            # self.face.construct_test_components()
            self.add_child(self.face)

        
