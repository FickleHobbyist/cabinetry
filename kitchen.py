from cabinetry.base import Orientation, Position
from cabinetry.config import Config
from cabinetry.components import ComponentContainer, ComponentGrid, GhostComponent
from cabinetry.components.uppers import UpperCabinet
from cabinetry.components.lowers import LowerCabinet, Pantry
from cabinetry.components.shelves import StandardShelf
from cabinetry.components.factory import _door_factory, _drawer_factory, get_faceframe_factory, get_shelf_factory
from cabinetry.components.decorators import faceframe_with_shelves
import numpy as np


TOP_DRAWER_HEIGHT = 5
CABINET_SPACING = 0.25


def _N_Drawer_eq_args(num_drawers: int):
    return {
        'drawer_dist': [1]*num_drawers,
        'dist_type': ['weighted']*num_drawers,
    }


def _N_Drawer_offset_args(num_drawers: int):
    return {
        'drawer_dist': [TOP_DRAWER_HEIGHT, *[1]*(num_drawers-1)],
        'dist_type': ['fixed', *['weighted']*num_drawers],
    }


def create_grid_with_spacing(cabs: list, spacing: float = CABINET_SPACING, **kwargs):
    widths = [cab.width for cab in cabs]
    nCab = len(widths)
    name = kwargs.pop('name', 'global-frame')

    grid = ComponentGrid(
        name=name,
        width=sum(widths) + spacing*(nCab-1),
        height=1,
        row_dist=np.array([1]),
        row_type=['weighted']*1,
        col_dist=np.array(widths),
        col_type=['fixed']*nCab,
        column_spacing=spacing,
        row_spacing=0,
        padding=(0, 0, 0, 0),
        **kwargs
    )
    for cab, cell in zip(cabs, grid.cells[0, :]):
        cell.add_child(cab)

    return grid


def main():
    base_frame = ComponentContainer()
    north_wall_lowers: list[LowerCabinet] = []
    north_wall_lowers.append(
        Pantry(
            width=36,
            height=90,
            frame_args={
                'row_dist': [90/3, 1],
                'row_type': ['fixed', 'weighted'],
                'col_dist': [1]*2,
                'col_type': ['weighted']*2,
            }
        )
    )
    north_wall_lowers.append(
        Pantry(
            width=15,
            height=90,
            frame_args={
                'row_dist': [90/3, 1],
                'row_type': ['fixed', 'weighted'],
                'col_dist': [1],
                'col_type': ['weighted'],
            }
        )
    )
    north_wall_lowers.append(
        LowerCabinet(
            width=21,
            frame_factory=get_faceframe_factory('N-Drawer'),
            frame_args=_N_Drawer_offset_args(3),
        )
    )
    north_wall_lowers.append(
        LowerCabinet(
            width=18,
            frame_factory=get_faceframe_factory('N-Drawer'),
            frame_args=_N_Drawer_offset_args(3),
        )
    )
    north_wall_lowers = create_grid_with_spacing(
        cabs=north_wall_lowers,
        spacing=CABINET_SPACING,
        name='north_wall_lowers',
        parent=base_frame,
        orientation=Orientation(
            rx=0,
            ry=0,
            rz=90,
        ),
    )

    west_wall_lowers: list[LowerCabinet] = []

    # Simulated Lemans corner cabinet
    west_wall_lowers.append(
        LowerCabinet(
            width=45,
            frame_factory=get_faceframe_factory('N-Door-Horiz'),
            frame_args={
                'door_dist': [1, 17],
                'dist_type': ['weighted', 'fixed'],
            },
        )
    )
    # 27" to left of range
    west_wall_lowers.append(
        LowerCabinet(
            width=27,
            frame_factory=get_faceframe_factory('N-Drawer'),
            frame_args=_N_Drawer_offset_args(3),
        )
    )
    west_wall_lowers.append(
        GhostComponent(
            width=48.5,
        )
    )
    # 21" to right of range, x2
    for _ in range(0, 2):
        west_wall_lowers.append(
            LowerCabinet(
                width=21,
                frame_factory=get_faceframe_factory('N-Drawer'),
                frame_args=_N_Drawer_eq_args(2),
            )
        )

    west_wall_lowers.append(
        LowerCabinet(
            width=33,
            frame_factory=get_faceframe_factory('N-Drawer'),
            frame_args=_N_Drawer_eq_args(2),
        )
    )

    west_wall_lowers = create_grid_with_spacing(
        cabs=west_wall_lowers,
        spacing=CABINET_SPACING,
        name='west_wall_lowers',
        parent=base_frame,
        orientation=Orientation(
            rx=0,
            ry=0,
            rz=0,
        ),
        position=Position(
            x=-Config.LOWERS_DEPTH,
            y=93,
            z=0,
        )
    )

    east_wall_lowers: list[LowerCabinet] = []
    # Simulated Lemans corner cabinet
    east_wall_lowers.append(
        LowerCabinet(
            width=45,
            frame_factory=get_faceframe_factory('N-Door-Horiz'),
            frame_args={
                'door_dist': [1, 17],
                'dist_type': ['weighted', 'fixed'],
            },
        )
    )
    microwave_cab = LowerCabinet(
        width=24,
        frame_factory=faceframe_with_shelves(
            get_faceframe_factory('MxN-Empty'),
            shelf_class=StandardShelf,
        ),
        frame_args={
            'row_dist': [15.5, 1],
            'row_type': ['fixed', 'weighted'],
            'col_dist': [1],
            'col_type': ['weighted'],
        },
    )
    # Add drawer to bottom cell of microwave_cab. Top remains open for microwave
    _drawer_factory(microwave_cab.face.cells[1])
    east_wall_lowers.append(microwave_cab)

    # Stand-in for corner cabinet on peninsula
    east_wall_lowers.append(
        LowerCabinet(
            width=18,
            frame_factory=get_faceframe_factory('N-Door-Horiz'),
            frame_args={
                'door_dist': [1, 1],
                'dist_type': ['weighted', 'weighted'],
            },
        )
    )

    east_wall_lowers = create_grid_with_spacing(
        cabs=east_wall_lowers,
        spacing=CABINET_SPACING,
        name='east_wall_lowers',
        parent=base_frame,
        orientation=Orientation(
            rx=0,
            ry=0,
            rz=-90,
        ),
        position=Position(
            x=176,
            y=93+Config.LOWERS_DEPTH,
            z=0,
        )
    )

    island = ComponentContainer(
        name='island',
        parent=base_frame,
        position=Position(
            x=42,
            y=-8,
            z=0,
        )
    )

    for i in range(0, 3):
        island.add_child(
            LowerCabinet(
                width=27,
                frame_factory=get_faceframe_factory('N-Door-Horiz'),
                frame_args={
                    'door_dist': [1, 1],
                    'dist_type': ['weighted', 'weighted'],
                },
                position=Position(
                    x=(27 + CABINET_SPACING)*i,
                    y=0,
                    z=0,
                )
            )
        )

    # Book case on end of island
    bookcase = LowerCabinet(
        width=24,
        depth=18,
        frame_factory=get_faceframe_factory('MxN-Empty'),
        frame_args={
            'row_dist': [1],
            'row_type': ['weighted'],
            'col_dist': [1],
            'col_type': ['weighted'],
        },
        position=Position(
            x=(27 + CABINET_SPACING)*3+18,
            y=0,
            z=0,
        ),
        orientation=Orientation(
            rx=0,
            ry=0,
            rz=90
        )
    )
    shelf_grid = ComponentGrid(
        parent=bookcase.case,
        width=bookcase.case.box_width_inside,
        height=bookcase.case.box_height_inside,
        position=bookcase.case.box_inside_origin,
        row_dist=np.array([1]*2),
        row_type=['weighted']*2,
        col_dist=np.array([1]),
        col_type=['weighted']*1,
        row_spacing=Config.SHELF_MATERIAL.thickness,
    )
    get_shelf_factory('banded')(grid=shelf_grid, case=bookcase.case)
    island.add_child(bookcase)

    # 4-drawer left of trash
    island.add_child(
        LowerCabinet(
            width=18,
            depth=24,
            frame_factory=get_faceframe_factory('N-Drawer'),
            frame_args={
                'drawer_dist': [*[TOP_DRAWER_HEIGHT]*3, 1],
                'dist_type': [*['fixed']*3, 'weighted'],
            },
            position=Position(
                x=(27 + CABINET_SPACING)*3+18,
                y=48+1/8,
                z=0,
            ),
            orientation=Orientation(
                rx=0,
                ry=0,
                rz=180
            )
        )
    )
    # Cabinet with top drawer and pull-out trash
    island.add_child(
        LowerCabinet(
            width=21,
            depth=24,
            frame_factory=get_faceframe_factory('N-Drawer'),
            frame_args={
                'drawer_dist': [TOP_DRAWER_HEIGHT, 1],
                'dist_type': ['fixed', 'weighted'],
            },
            position=Position(
                x=island.children[-1].position.x -
                (island.children[-1].width + CABINET_SPACING),
                y=48+1/8,
                z=0,
            ),
            orientation=Orientation(
                rx=0,
                ry=0,
                rz=180
            )
        )
    )
    # Sink
    sink_cab = LowerCabinet(
        parent=island,
        width=36,
        position=Position(
            x=island.children[-1].position.x -
            (island.children[-1].width + CABINET_SPACING),
            y=48+1/8,
            z=0,
        ),
        orientation=Orientation(
            rx=0,
            ry=0,
            rz=180
        ),
        frame_factory=faceframe_with_shelves(
            get_faceframe_factory('MxN-Empty'),
            shelf_class=StandardShelf,
        ),
        frame_args={
            'row_dist': [10, 1],
            'row_type': ['fixed', 'weighted'],
            'col_dist': [1],
            'col_type': ['weighted'],
        },
    )
    under_sink_cell = sink_cab.face.cells[1, 0]
    under_sink_grid = ComponentGrid(
        parent=under_sink_cell,
        width=under_sink_cell.width,
        height=under_sink_cell.height,
        row_dist=np.array([1]),
        row_type=['weighted'],
        col_dist=np.array([1, 1]),
        col_type=['weighted', 'weighted'],
        column_spacing=Config.FACE_FRAME_MEMBER_WIDTH - 0.5*Config.OVERLAY_GAP,
    )
    # Add doors to bottom cell of sink_cab. Top remains open for sink
    _door_factory(under_sink_grid.cells)

    base_frame.render()


if __name__ == "__main__":
    main()
