from cabinetry.base import Orientation, Position
from cabinetry.config import Config
from cabinetry.components import ComponentGrid
from cabinetry.components.uppers import UpperCabinet
from cabinetry.components.lowers import LowerCabinet
import numpy as np


TOP_DRAWER_HEIGHT = 5


_4_Drawer_offset_args = {
    'drawer_dist': [TOP_DRAWER_HEIGHT, 1, 1, 1],
    'dist_type': ['fixed', 'weighted', 'weighted', 'weighted'],
}
_3_Drawer_offset_args = {
    'drawer_dist': [TOP_DRAWER_HEIGHT, 1, 1],
    'dist_type': ['fixed', 'weighted', 'weighted'],
}
_1_Drawer_2_Door_args = {
    'drawer_dist': [TOP_DRAWER_HEIGHT, 1],
    'dist_type': ['fixed', 'weighted'],
}


def _N_Drawer_eq_args(num_drawers: int):
    return {
        'drawer_dist': [1]*num_drawers,
        'dist_type': ['weighted']*num_drawers,
    }


def _N_Door_eq_args(num_doors):
    return {
        'door_dist': [1]*num_doors,
        'dist_type': ['weighted']*num_doors,
    }


def main():
    lower_cabs: list[LowerCabinet] = []
    lower_cabs.append(
        LowerCabinet(
            width=36,
            frame_type='N-Drawer',
            frame_args=_N_Drawer_eq_args(4),
        )
    )
    lower_cabs.append(
        LowerCabinet(
            width=33,
            frame_type='N-Drawer',
            frame_args=_4_Drawer_offset_args,
        )
    )
    lower_cabs.append(
        LowerCabinet(
            width=30,
            frame_type='N-Drawer',
            frame_args=_3_Drawer_offset_args,
        )
    )
    lower_cabs.append(
        LowerCabinet(
            width=27,
            frame_type='1-Drawer-2-Door',
            frame_args=_1_Drawer_2_Door_args,
        )
    )
    lower_cabs.append(
        LowerCabinet(
            width=24,
            frame_type='N-Drawer',
            frame_args=_N_Drawer_eq_args(3),
        )
    )
    # lower_cabs.append(
    #     LowerCabinet(
    #         width=60,
    #         frame_type='N-Door',
    #         frame_args=_N_Door_eq_args(3),
    #     )
    # )
    # lower_cabs.append(
    #     LowerCabinet(
    #         width=72,
    #         frame_type='N-Door',
    #         frame_args=_N_Door_eq_args(4),
    #     )
    # )

    widths = [cab.width for cab in lower_cabs]
    nCab = len(widths)
    spacing = 0.25
    depth = lower_cabs[0].case.CABINET_DEPTH
    base_frame = ComponentGrid(
        name='global_frame',
        width=sum(widths) + spacing*(nCab-1),
        height=depth,
        row_dist=np.array([Config.UPPERS_HEIGHT, Config.COUNTER_HEIGHT]),
        row_type=['fixed']*2,
        col_dist=np.array(widths),
        col_type=['fixed']*nCab,
        column_spacing=spacing,
        row_spacing=Config.COUNTER_TO_UPPERS_GAP,
        orientation=Orientation(
            rx=0,
            ry=0,
            rz=0,
        )
    )

    upper_cells = base_frame.cells[0, :]
    for cell in upper_cells:
        cell.add_child(
            UpperCabinet(
                width=cell.width,
                position=Position(
                    x=0,
                    y=Config.LOWERS_DEPTH-Config.UPPERS_DEPTH,
                    z=0,
                )
            )
        )

    lower_cells = base_frame.cells[1, :]
    for lower_cab, cell in zip(lower_cabs, lower_cells):
        cell.add_child(lower_cab)
    base_frame.render(show_edges=True, opacity=1)


if __name__ == "__main__":
    main()
