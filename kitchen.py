from cabinetry.base import Orientation, Position
from cabinetry.config import Config
from cabinetry.components import ComponentContainer, ComponentGrid, GhostComponent
from cabinetry.components.uppers import UpperCabinet
from cabinetry.components.lowers import LowerCabinet, Pantry
from cabinetry.components.shelves import StandardShelf
from cabinetry.components.doors import ShakerDoor
from cabinetry.components.factory import _door_factory, _drawer_factory, get_faceframe_factory, get_shelf_factory
from cabinetry.components.decorators import faceframe_with_shelves
import numpy as np


TOP_DRAWER_HEIGHT = 5


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


def assemble_in_grid(cabs: list, spacing: float = 0, **kwargs):
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


def construct_kitchen():
    base_frame = ComponentContainer()
    south_wall_lowers: list[LowerCabinet] = []
    south_wall_lowers.append(
        Pantry(
            width=36,
            height=93,
            frame_args={
                'row_dist': [90/3, 1],
                'row_type': ['fixed', 'weighted'],
                'col_dist': [1]*2,
                'col_type': ['weighted']*2,
            }
        )
    )
    south_wall_lowers.append(
        Pantry(
            width=15,
            height=93,
            frame_args={
                'row_dist': [93/3, 1],
                'row_type': ['fixed', 'weighted'],
                'col_dist': [1],
                'col_type': ['weighted'],
            }
        )
    )
    south_wall_lowers.append(
        LowerCabinet(
            width=21,
            frame_factory=get_faceframe_factory('N-Drawer'),
            frame_args=_N_Drawer_offset_args(3),
        )
    )
    south_wall_lowers.append(
        LowerCabinet(
            width=18,
            frame_factory=get_faceframe_factory('N-Drawer'),
            frame_args=_N_Drawer_offset_args(3),
        )
    )
    south_wall_lowers = assemble_in_grid(
        cabs=south_wall_lowers,
        spacing=0,
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

    west_wall_lowers = assemble_in_grid(
        cabs=west_wall_lowers,
        spacing=0,
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

    north_wall_lowers: list[LowerCabinet] = []
    # Simulated Lemans corner cabinet
    north_wall_lowers.append(
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
    north_wall_lowers.append(microwave_cab)

    # Stand-in for corner cabinet on peninsula
    north_wall_lowers.append(
        LowerCabinet(
            width=18,
            frame_factory=get_faceframe_factory('N-Door-Horiz'),
            frame_args={
                'door_dist': [1, 1],
                'dist_type': ['weighted', 'weighted'],
            },
        )
    )

    north_wall_lowers = assemble_in_grid(
        cabs=north_wall_lowers,
        spacing=0,
        name='north_wall_lowers',
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
                    x=(27 + 0)*i,
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
            x=(27 + 0)*3+18,
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
                x=(27 + 0)*3+18,
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
                (island.children[-1].width + 0),
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
            (island.children[-1].width + 0),
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

    south_wall_uppers: list[UpperCabinet] = []
    upper_widths = [30, 12]
    num_doors = [2, 1]
    nShelves = 3
    for width, ndoors in zip(upper_widths, num_doors):
        cab = UpperCabinet(
            width=width,
            frame_factory=get_faceframe_factory('N-Door-Horiz'),
            frame_args={
                'door_dist': [1]*ndoors,
                'dist_type': ['weighted']*ndoors
            },
            # depth and height relative to front of lowers at the floor level
            position=Position(
                x=0,
                y=Config.LOWERS_DEPTH-Config.UPPERS_DEPTH,
                z=Config.COUNTER_HEIGHT+Config.COUNTER_TO_UPPERS_GAP,
            )
        )
        south_wall_uppers.append(cab)

    # Corner cabinet to be simulated by 24" wide and 12" wide
    corner_cab_left = UpperCabinet(
        width=24,
        frame_factory=get_faceframe_factory('MxN-Empty'),
        frame_args={
            'row_dist': [1],
            'row_type': ['weighted'],
            'col_dist': [9, 1],
            'col_type': ['fixed', 'weighted'],
        },
        # depth and height relative to front of lowers at the floor level
        position=Position(
            x=0,
            y=Config.LOWERS_DEPTH-Config.UPPERS_DEPTH,
            z=Config.COUNTER_HEIGHT+Config.COUNTER_TO_UPPERS_GAP,
        )
    )
    # Add door to left side only
    cell = corner_cab_left.face.cells[0, 0]
    cell.add_child(
        ShakerDoor(
            hinge_side='left',
            hinge_stile_factor='double',
            opening_width=cell.width,
            opening_height=cell.height,
        )
    )

    # Adding 12" cabinet and rotating to make positioning it easier
    # The door and case details aren't exactly right here but close
    # enough for a rough estimate.
    # TODO: Make a corner cabinet class to better represent this geometry
    corner_cab_right = UpperCabinet(
        parent=corner_cab_left,
        width=12,
        frame_factory=get_faceframe_factory('N-Door-Horiz'),
        frame_args={
            'door_dist': [1],
            'dist_type': ['weighted'],
        },
        position=Position(
            x=corner_cab_left.width-Config.UPPERS_DEPTH,
            y=0,
            z=0,
        ),
        orientation=Orientation(
            rx=0,
            ry=0,
            rz=-90
        )
    )

    south_wall_uppers.append(corner_cab_left)

    for cab in south_wall_uppers:
        shelf_grid = ComponentGrid(
            parent=cab.case,
            width=cab.case.box_width_inside,
            height=cab.case.box_height_inside,
            position=cab.case.box_inside_origin,
            row_dist=np.array([1]*(nShelves+1)),
            row_type=['weighted']*(nShelves+1),
            col_dist=[1],
            col_type=['weighted'],
        )
        get_shelf_factory('banded')(grid=shelf_grid, case=cab.case)

    south_wall_uppers = assemble_in_grid(
        cabs=south_wall_uppers,
        spacing=0,
        name='south_wall_uppers',
        parent=base_frame,
        orientation=Orientation(
            rx=0,
            ry=0,
            rz=90,
        ),
        # position at origin of first lower cabinet
        position=south_wall_lowers.cells[0, 2].get_global_pose()[0],
    )

    # pos, ori = corner_cab_right.get_global_pose()
    west_wall_uppers: list[UpperCabinet] = []
    west_wall_uppers.append(
        UpperCabinet(
            width=12,
            frame_factory=get_faceframe_factory('N-Door-Horiz'),
            frame_args={
                'door_dist': [1],
                'dist_type': ['weighted'],
            },
        )
    )
    west_wall_uppers.append(
        UpperCabinet(
            width=36,
            frame_factory=get_faceframe_factory('N-Door-Horiz'),
            frame_args={
                'door_dist': [1]*2,
                'dist_type': ['weighted']*2,
            },
        )
    )

    west_wall_uppers = assemble_in_grid(
        cabs=west_wall_uppers,
        spacing=0,
        name='west_wall_uppers',
        parent=base_frame,
        position=(
            corner_cab_right.get_global_pose()[0]
            + (corner_cab_right.width+0, 0, 0)),
        orientation=Orientation(
            rx=0,
            ry=0,
            rz=0
        )
    )

    base_frame.render()


if __name__ == "__main__":
    construct_kitchen()
