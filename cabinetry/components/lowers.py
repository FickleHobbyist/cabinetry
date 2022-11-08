"""Module containing concrete components from which to build cabinets"""
from .decorators import faceframe_with_shelves
from ..config import Config
from ..base import Position, Orientation
from .shelves import StandardShelf
from . import ComponentContainer, ComponentGrid, FaceFrame, GridCell, RectangularComponent, CabinetCase
from .factory import _banded_shelf_factory, _door_factory, _standard_shelf_factory, get_faceframe_factory
import numpy as np


class LowerCabinetCase(CabinetCase):
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
        self.box_depth = self.CABINET_DEPTH - Config.FACE_FRAME_MATERIAL.thickness
        self.box_width_inside = self.width - 2*self.material.thickness
        self.box_height_inside = (
            (self.height - self.material.thickness)  # inside of top stretcher
            - self.bottom_height_above_floor)
        self.box_inside_origin = Position(
            x=self.material.thickness,
            y=0,
            z=self.bottom_height_above_floor,
        )

        toekick_cutout_height = (self.bottom_height_above_floor -
                                 self.material.thickness - self.DADO_HEIGHT_ABOVE_TOEKICK_CUTOUT)
        base_block_height = self.bottom_height_above_floor - self.material.thickness

        self.add_child(
            RectangularComponent(
                name='Left Side',
                material=self.material,
                width=self.box_depth,
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
                width=self.box_depth,
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
                width=self.box_width_inside + 2*self.FLOOR_DADO_DEPTH,
                height=self.box_depth,
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
                width=self.box_width_inside,
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
                width=self.box_width_inside,
                height=base_block_height,
                position=Position(
                    x=self.material.thickness,
                    y=self.box_depth-self.material.thickness,
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
                width=self.box_width_inside,
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
                width=self.box_width_inside,
                height=self.STRETCHER_WIDTH,
                position=Position(
                    x=self.material.thickness,
                    y=self.box_depth-self.STRETCHER_WIDTH,
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
                width=self.box_width_inside,
                height=self.STRETCHER_WIDTH,
                position=Position(
                    x=self.material.thickness,
                    y=self.box_depth - self.material.thickness,
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
                 frame_factory: callable = get_faceframe_factory('N-Drawer'),
                 frame_args: dict = None,
                 *args, **kwargs):
        super(LowerCabinet, self).__init__(name=name,
                                           *args, **kwargs)
        self.width = width
        self.height = height
        self.frame_factory = frame_factory
        self.frame_args = frame_args if frame_args is not None else {
            'drawer_dist': [1]*4,
            'dist_type': ['weighted']*4
        }
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

        if self.frame_factory is not None:
            faceframe_side_overhang = 1/8
            # ff_factory = get_faceframe_factory(self.frame_type)

            self.face: FaceFrame = self.frame_factory(
                box_width=self.width,
                box_height=(self.height -
                            (self.case.bottom_height_above_floor-self.case.material.thickness)),
                box_material=self.case.material,
                side_overhang=faceframe_side_overhang,
                parent=self,
                **self.frame_args,
            )
            self.face.position.z = self.case.TOEKICK_HEIGHT

            self.face.construct_components()


class Pantry(LowerCabinet):
    def __init__(self,
                 width: float = 36,
                 height: float = 90,
                 name='PantryCabinet',
                 *args, **kwargs):
        frame_factory = kwargs.pop(
            'frame_factory',
            faceframe_with_shelves(
                face_factory=get_faceframe_factory(
                    'MxN-Empty'),
                shelf_class=StandardShelf,
            )
        )
        frame_args = kwargs.pop(
            'frame_args',
            {
                'row_dist': [height/3, 1],
                'row_type': ['fixed', 'weighted'],
                'col_dist': [1, 1],
                'col_type': ['weighted', 'weighted'],
            }
        )
        super().__init__(width=width,
                         height=height,
                         name=name,
                         frame_factory=frame_factory,
                         frame_args=frame_args,
                         *args, **kwargs)

        for row, i in zip(self.face.cells, range(0, self.face.cells.shape[0])):
            row = row.reshape(1, row.size)
            cell_01 = GridCell.spanning(row, parent=self.face)

            grid = ComponentGrid(
                parent=cell_01,
                width=self.case.box_width_inside,
                height=cell_01.height,
                position=Position(
                    x=-0.5*abs(cell_01.width - self.case.box_width_inside),
                    y=Config.FACE_FRAME_MATERIAL.thickness,
                    z=0,
                ),
                row_dist=np.array([1]*(3+i)),
                row_type=['weighted']*(3+i),
                col_dist=np.array([1]),
                col_type=['weighted'],
                row_spacing=Config.SHELF_MATERIAL.thickness,
            )
            _banded_shelf_factory(grid, self.case)

        _door_factory(self.face.cells)
