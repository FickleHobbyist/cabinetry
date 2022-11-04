from cabinetry.base import Orientation, Position
from cabinetry.components import ComponentContainer, ComponentGrid
from cabinetry.components.drawers import BlumDrawer
from cabinetry.components.lowers import LowerCabinet, LowerCabinetCase
import numpy as np

TOP_DRAWER_HEIGHT = 5

_4_Drawer_eq_args = {
    'drawer_dist': [1]*4,
    'dist_type': ['weighted']*4,
}
_4_Drawer_offset_args = {
    'drawer_dist': [TOP_DRAWER_HEIGHT, 1, 1, 1],
    'dist_type': ['fixed', 'weighted', 'weighted', 'weighted'],
}
_3_Drawer_eq_args = {
    'drawer_dist': [1]*3,
    'dist_type': ['weighted']*3,
}
_3_Drawer_offset_args = {
    'drawer_dist': [TOP_DRAWER_HEIGHT, 1, 1],
    'dist_type': ['fixed', 'weighted', 'weighted'],
}
_1_Drawer_2_Door_args = {
    'drawer_dist': [TOP_DRAWER_HEIGHT, 1],
    'dist_type': ['fixed', 'weighted'],
}


def main():
    lower_cabs: list[LowerCabinet] = []
    lower_cabs.append(
        LowerCabinet(
            width=36,
            frame_type='N-Drawer',
            frame_args=_4_Drawer_eq_args,
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
    # lower_cabs.append(
    #     LowerCabinet(
    #         width=27,
    #         frame_type='1-Drawer-2-Door',
    #         frame_args=_1_Drawer_2_Door_args,
    #     )
    # )
    # cab = lower_cabs[-1]
    # dwr_cell = cab.face.cells[0]
    # dwr_cell.add_child(
    #     BlumDrawer(
    #         opening_width=cell.width,
    #         opening_height=cell.height,
    #     )
    # )

    lower_cabs.append(
        LowerCabinet(
            width=24,
            frame_type='N-Drawer',
            frame_args=_3_Drawer_eq_args,
        )
    )

    for cab in lower_cabs:
        cells = cab.face.cells.reshape(cab.face.cells.size,).tolist()
        for cell in cells:
            cell.add_child(
                BlumDrawer(
                    opening_width=cell.width,
                    opening_height=cell.height,
                )
            )

    widths = [cab.width for cab in lower_cabs]
    nCab = len(widths)
    spacing = 0.25
    depth = lower_cabs[0].case.CABINET_DEPTH
    base_frame = ComponentGrid(
        name='global_frame',
        width=sum(widths) + spacing*(nCab-1),
        height=depth,
        row_dist=np.array([1]),
        row_type=['weighted'],
        col_dist=np.array(widths),
        col_type=['fixed']*nCab,
        column_spacing=spacing,
        orientation=Orientation(
            rx=0,
            ry=0,
            rz=0,
        )
    )

    for cab, cell in zip(lower_cabs, base_frame.cells.reshape(base_frame.cells.size,).tolist()):
        cell.add_child(cab)
    base_frame.render(show_edges=True)


if __name__ == "__main__":
    main()
