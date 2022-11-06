from multiprocessing.sharedctypes import Value
from ..base import Position
from ..components import FaceFrame, GridCell
from .drawers import BlumDrawer
from .doors import ShakerDoor
import numpy as np


def _NxN_Empty_faceframe(
    box_width,
    box_height,
    box_material,
    side_overhang,
    row_dist: list = None,
    row_type: list[str] = None,
    col_dist: list = None,
    col_type: list[str] = None,
    *args, **kwargs,
) -> FaceFrame:
    row_dist = row_dist if row_dist is not None else [1]*2
    row_type = row_type if row_type is not None else ['weighted']*2
    col_dist = col_dist if col_dist is not None else [1]*2
    col_type = col_type if col_type is not None else ['weighted']*2

    face = FaceFrame(
        box_width=box_width,
        box_height=box_height,
        box_material=box_material,
        side_overhang=side_overhang,
        row_dist=np.array(row_dist),
        row_type=row_type,
        col_dist=np.array(col_dist),
        col_type=col_type,
        position=Position(  # x=width, y=thickness, z=height
            x=-side_overhang,
            y=0,
            z=0,
        ),
        *args, **kwargs,
    )
    return face


def _N_Drawer_faceframe(
    box_width,
    box_height,
    box_material,
    side_overhang,
    drawer_dist: list = None,
    dist_type: list[str] = None,
) -> FaceFrame:
    drawer_dist = drawer_dist if drawer_dist is not None else [1]*4
    dist_type = dist_type if dist_type is not None else ['weighted']*4
    face = FaceFrame(
        box_width=box_width,
        box_height=box_height,
        box_material=box_material,
        side_overhang=side_overhang,
        row_dist=np.array(drawer_dist),
        row_type=dist_type,
        col_dist=np.array([1]),
        col_type=['weighted'],
        position=Position(  # x=width, y=thickness, z=height
            x=-side_overhang,
            y=0,
            z=0,
        ),
    )

    cells = face.cells.reshape(face.cells.size,).tolist()
    for cell in cells:
        cell.add_child(
            BlumDrawer(
                opening_width=cell.width,
                opening_height=cell.height,
            )
        )

    return face


def _N_Door_vertical_faceframe(
    box_width,
    box_height,
    box_material,
    side_overhang,
    door_dist: list = None,
    dist_type: list[str] = None,
    hinge_side: str = 'left',
    *args, **kwargs,
) -> FaceFrame:
    door_dist = door_dist if door_dist is not None else [1]*2
    dist_type = dist_type if dist_type is not None else ['weighted']*2

    face = FaceFrame(
        box_width=box_width,
        box_height=box_height,
        box_material=box_material,
        side_overhang=side_overhang,
        row_dist=np.array([1]),
        row_type=['weighted'],
        col_dist=door_dist,
        col_type=dist_type,
        position=Position(  # x=width, y=thickness, z=height
            x=-side_overhang,
            y=0,
            z=0,
        ),
        *args, **kwargs,
    )

    _door_factory(face.cells, hinge_side_preference=hinge_side)

    return face


def _N_Door_horizontal_faceframe(
    box_width,
    box_height,
    box_material,
    side_overhang,
    door_dist: list = None,
    dist_type: list[str] = None,
    hinge_side_preference: str = 'left',
    *args, **kwargs,
) -> FaceFrame:
    door_dist = door_dist if door_dist is not None else [1]*2
    dist_type = dist_type if dist_type is not None else ['weighted']*2

    face = FaceFrame(
        box_width=box_width,
        box_height=box_height,
        box_material=box_material,
        side_overhang=side_overhang,
        row_dist=np.array([1]),
        row_type=['weighted'],
        col_dist=door_dist,
        col_type=dist_type,
        position=Position(  # x=width, y=thickness, z=height
            x=-side_overhang,
            y=0,
            z=0,
        ),
        *args, **kwargs,
    )
    
    _door_factory(face.cells, hinge_side_preference=hinge_side_preference)

    return face


def _1_Drawer_2_Door_faceframe(
    box_width,
    box_height,
    box_material,
    side_overhang,
    drawer_dist: list = None,
    dist_type: list[str] = None,
) -> FaceFrame:
    drawer_dist = drawer_dist if drawer_dist is not None else [5, 1]
    dist_type = dist_type if dist_type is not None else ['fixed' 'weighted']
    face = FaceFrame(
        box_width=box_width,
        box_height=box_height,
        box_material=box_material,
        side_overhang=side_overhang,
        row_dist=np.array(drawer_dist),
        row_type=dist_type,
        col_dist=np.array([1]),
        col_type=['weighted'],
        position=Position(  # x=width, y=thickness, z=height
            x=-side_overhang,
            y=0,
            z=0,
        ),
    )
    drawer_cell: GridCell = face.cells[0, 0]
    drawer_cell.add_child(
        BlumDrawer(
            opening_width=drawer_cell.width,
            opening_height=drawer_cell.height,
        )
    )
    subcell: GridCell = face.cells[1, 0]
    door_ff = FaceFrame(
        box_width=face.grid_width,
        box_height=subcell.height,
        box_material=box_material,
        side_overhang=0,
        width=face.grid_width,
        height=subcell.height,
        padding=(0,)*4,
        row_dist=np.array([1]),
        row_type=['weighted'],
        col_dist=np.array([1, 1]),
        col_type=['weighted']*2,
    )
    subcell.add_child(door_ff)

    _door_factory(door_ff.cells)

    return face


# Reference for ideas: https://keystonewood.com/wp-content/uploads/2022/06/Face-Frames-Form-6-2022.pdf
_FACEFRAME_FACTORIES: dict = {
    'NxN-Empty': _NxN_Empty_faceframe,
    'N-Drawer': _N_Drawer_faceframe,
    'N-Door-Horiz': _N_Door_horizontal_faceframe,
    'N-Door-Vert': _N_Door_vertical_faceframe,
    '1-Drawer-2-Door': _1_Drawer_2_Door_faceframe,
}


def register_faceframe_factory(name: str, func: callable):
    if name not in _FACEFRAME_FACTORIES.keys():
        _FACEFRAME_FACTORIES[name] = func


def get_faceframe_factory(name: str) -> callable:
    if name in _FACEFRAME_FACTORIES.keys():
        return _FACEFRAME_FACTORIES[name]
    else:
        key_str = "\n\t".join(_FACEFRAME_FACTORIES.keys())
        raise ValueError(
            f"'{name}' is not a registered FaceFrameFactory. Available factories are:\n\t{key_str}"
        )

# \/\/\/ Door Factories \/\/\/
# inputs: numpy array of GridCell objects

def _door_factory(
    cells: np.ndarray,
    hinge_side_preference: str = 'left',
) -> None:

    for row in cells:
        nDoors = row.size
        hinge_sides = ['left']
        match hinge_side_preference:
            case 'left' | 'right':
                hinge_sides.extend([hinge_side_preference]*(nDoors-2))
            case 'alternate':
                RL = ['right', 'left']
                hinge_sides.extend([RL[i % 2] for i in range(0, (nDoors-2))])
            case _:
                ValueError("arg 'hinge_side_preference' must be one\
                    of ['left','right','alternate']")

        hinge_sides.append('right')

        hinge_factors = ['double']
        hinge_factors.extend(['single']*(nDoors-2))
        hinge_factors.append('double')
        for cell, LR, hs in zip(row, hinge_sides, hinge_factors):
            cell.add_child(
            ShakerDoor(
                hinge_side=LR,
                hinge_stile_factor=hs,
                opening_width=cell.width,
                opening_height=cell.height,
            )
        )
