# TODO: Reduce size of outfeed top by 0.5" in each dimension so two edge pieces can be cut from a 120" length of stock
# TODO: Re-run optimizer 
from cabinetry.base import Orientation, Position
from cabinetry.components.drawers import SimpleInsetDrawer
from cabinetry.components import ComponentContainer, ComponentGrid, RectangularComponent, PvAxes
import numpy as np
import pandas as pd
import pyvista as pv
import sqlite3
import itertools
import math
import os
from estimate_material import component_dict_serializer, find_instances, component_keyfunc

from cabinetry.materials import Material

FINISHED_HEIGHT = 34 + 3/16
TOP_COLOR = '#e6cd83'
TOP_THICKNESS = 3+3/16
TOP_PANEL_MATERIAL = Material.PLY_3_4_5x5
TOP_PANEL_BAND_MATERIAL = Material.HARDWOOD_STAIN_3_4
TOP_LATTICE_MATERIAL = Material.PLY_3_4_4x8
TOP_LATTICE_MEMBER_WIDTH = TOP_THICKNESS - 2*TOP_PANEL_MATERIAL.thickness
print(f"{TOP_LATTICE_MEMBER_WIDTH=}")
TOP_LENGTH = 60
TOP_WIDTH = 60
BASE_WIDTH_INSET = 3
BASE_LENGTH_INSET = (6, 3)  # (nearest saw, furthest)

DWR_COLOR = '#ab9f8d'
DWR_BOX_MATERIAL = Material.PLY_1_2_4x8
DWR_BOTTOM_MATERIAL = Material.PLY_1_4_4x8
DWR_FACE_MATERIAL = Material.PLY_3_4_4x8_VNR
SIDE_PANEL_MATERIAL = DWR_FACE_MATERIAL
SIDE_PANEL_COLOR = DWR_COLOR

BASE_COLOR = '#6A1616'
DIV_PANEL_MATERIAL = Material.PLY_3_4_4x8
BASE_MATERIAL = Material.HARDWOOD_STAIN_8_4_S2S
BASE_WIDTH = TOP_WIDTH - 2*BASE_WIDTH_INSET  # perpendicular to saw blade
BASE_LENGTH = TOP_LENGTH - sum(BASE_LENGTH_INSET)  # parallel to feed direction
BASE_HEIGHT = FINISHED_HEIGHT - TOP_THICKNESS
BASE_HEIGHT_ABOVE_GND = 3/4
STRETCHER_WIDTH = 3 + 1/4
# STRETCHER_WIDTH = 2*BASE_MATERIAL.thickness
LEG_WIDTH = 2*BASE_MATERIAL.thickness

SHORT_STRETCHER_LENGTH = BASE_LENGTH - 2*LEG_WIDTH
SHORT_STRETCHER_INSET = 0.5*(LEG_WIDTH - BASE_MATERIAL.thickness)

FACE2FACE_WIDTH_TOTAL = BASE_WIDTH - 2 * SHORT_STRETCHER_INSET
INNER_WIDTH_TOTAL = BASE_WIDTH - 2 * \
    (SHORT_STRETCHER_INSET + BASE_MATERIAL.thickness)
INNER_HEIGHT_TOTAL = BASE_HEIGHT - 2*STRETCHER_WIDTH - BASE_HEIGHT_ABOVE_GND
INNER_LENGTH_TOTAL = BASE_LENGTH - 2*LEG_WIDTH
print(f"{INNER_LENGTH_TOTAL=}, {INNER_HEIGHT_TOTAL=}, {FACE2FACE_WIDTH_TOTAL=}")


def add_rails_stiles(grid, depth, material, name_prefix):
    rail_anchors = (grid.row_pos + grid.row_sizes).tolist()
    rail_anchors.append(0)
    stile_anchors = (grid.col_pos + grid.col_sizes).tolist()
    stile_anchors.insert(0, 0)  # add an anchor at 0
    # Make full height stiles ANCHORED by left/right padding, if present
    for s_pos, pad_width in zip([stile_anchors[0], stile_anchors[-1]], [grid.padding[0], grid.padding[2]]):
        if pad_width > 0:
            grid.add_child(
                RectangularComponent(
                    name=f'{name_prefix} stile (full)',
                    width=depth,
                    height=grid.height,
                    material=material,
                    # x=width, y=thickness, z=height
                    position=Position(x=s_pos + material.thickness, y=0, z=0),
                    orientation=Orientation(rx=0, ry=0, rz=90),
                    color=grid.color,
                )
            )

    # Make rails ANCHORED by top/bottom padding, if present
    for r_pos, pad_width in zip([rail_anchors[0], rail_anchors[-1]], [grid.padding[3], grid.padding[1]]):
        if pad_width > 0:
            grid.add_child(
                RectangularComponent(
                    name=f'{name_prefix} rail (full)',
                    width=grid.grid_width,
                    height=depth,
                    material=material,
                    # x=width, y=thickness, z=height
                    position=Position(
                        x=grid.padding[0], y=0, z=r_pos + material.thickness),
                    orientation=Orientation(rx=-90, ry=0, rz=0),
                    color=grid.color,
                )
            )

    # Make grid height stiles within padding. Use col right edges as anchors
    for c_pos in stile_anchors[1:-1]:
        grid.add_child(
            RectangularComponent(
                name=f'{name_prefix} stile (short)',
                width=depth,
                height=grid.grid_height,
                material=material,
                # x=width, y=thickness, z=height
                position=Position(x=c_pos + material.thickness,
                                  y=0, z=grid.padding[1]),
                orientation=Orientation(rx=0, ry=0, rz=90),
                color=grid.color,
            )
        )

    cells = grid.cells
    # for every row in cells except for first (upper-most) row, each cell gets a rail above it
    for row in cells[1:, :]:
        for cell in row:
            grid.add_child(
                RectangularComponent(
                    name=f'{name_prefix} rail (short)',
                    width=cell.width,
                    height=depth,
                    material=material,
                    # x=width, y=thickness, z=height
                    position=Position(
                        x=cell.position.x,
                        y=0,
                        z=cell.position.z+cell.height + material.thickness
                    ),
                    orientation=Orientation(rx=-90, ry=0, rz=0),
                    color=grid.color,
                )
            )


def construct_torsion_box_top() -> ComponentContainer:
    C = ComponentContainer(
        orientation=Orientation(
            rx=-90,
            ry=0,
            rz=0,
        ),
        position=Position(
            x=0,
            y=0,
            z=FINISHED_HEIGHT,
        )
    )
    C.add_child(PvAxes())

    top_sheet = RectangularComponent(
        name='torsion box sheet',
        parent=C,
        width=TOP_LENGTH - 2*TOP_PANEL_BAND_MATERIAL.thickness,
        height=TOP_WIDTH - 2*TOP_PANEL_BAND_MATERIAL.thickness,
        material=TOP_PANEL_MATERIAL,
        color=TOP_COLOR,
        position=Position(
            x=TOP_PANEL_BAND_MATERIAL.thickness,
            y=0,
            z=TOP_PANEL_BAND_MATERIAL.thickness,
        ),
        orientation=Orientation(
            rx=0,
            ry=0,
            rz=0,
        ),
    )
    bottom_sheet = RectangularComponent(
        name='torsion box sheet',
        parent=C,
        width=TOP_LENGTH - 2*TOP_PANEL_BAND_MATERIAL.thickness,
        height=TOP_WIDTH - 2*TOP_PANEL_BAND_MATERIAL.thickness,
        material=TOP_PANEL_MATERIAL,
        color=TOP_COLOR,
        position=Position(
            x=TOP_PANEL_BAND_MATERIAL.thickness,
            y=TOP_THICKNESS - TOP_PANEL_MATERIAL.thickness,
            z=TOP_PANEL_BAND_MATERIAL.thickness,
        ),
        orientation=Orientation(
            rx=0,
            ry=0,
            rz=0,
        ),
    )

    nRow = 1
    nCol = 1
    banding_grid = ComponentGrid(
        parent=C,
        color=BASE_COLOR,
        width=TOP_LENGTH,
        height=TOP_WIDTH,
        row_dist=np.array([1]*nRow),
        row_type=['weighted']*nRow,
        col_dist=np.array([1]*nCol),
        col_type=['weighted']*nCol,
        row_spacing=0,
        column_spacing=0,
        padding=(TOP_PANEL_BAND_MATERIAL.thickness,)*4,
        position=Position(
            x=0,
            y=0,
            z=0,
        )
    )
    add_rails_stiles(banding_grid, TOP_THICKNESS,
                     TOP_PANEL_BAND_MATERIAL, 'top banding')

    nRow = 7
    nCol = 5
    lattice_grid = ComponentGrid(
        parent=C,
        color=TOP_COLOR,
        width=TOP_LENGTH - 2*TOP_PANEL_BAND_MATERIAL.thickness,
        height=TOP_WIDTH - 2*TOP_PANEL_BAND_MATERIAL.thickness,
        row_dist=np.array([1]*nRow),
        row_type=['weighted']*nRow,
        col_dist=np.array([1]*nCol),
        col_type=['weighted']*nCol,
        row_spacing=TOP_LATTICE_MATERIAL.thickness,
        column_spacing=TOP_LATTICE_MATERIAL.thickness,
        padding=(TOP_LATTICE_MATERIAL.thickness,)*4,
        position=Position(
            x=TOP_PANEL_BAND_MATERIAL.thickness,
            y=TOP_PANEL_MATERIAL.thickness,
            z=TOP_PANEL_BAND_MATERIAL.thickness,
        )
    )
    add_rails_stiles(lattice_grid, TOP_LATTICE_MEMBER_WIDTH,
                     TOP_LATTICE_MATERIAL, 'top lattice')
    return C


def make_leg() -> ComponentContainer:
    leg = ComponentContainer(
        orientation=Orientation(
            rx=0,
            ry=0,
            rz=0,
        )
    )
    LP1 = RectangularComponent(
        name='Leg Pc',
        width=LEG_WIDTH,
        height=BASE_HEIGHT - BASE_HEIGHT_ABOVE_GND,
        material=BASE_MATERIAL,
        color=BASE_COLOR,
        position=Position(
            x=0,
            y=0,
            z=BASE_HEIGHT_ABOVE_GND,
        )
    )
    leg.add_child(LP1)
    LP2 = RectangularComponent(
        name='Leg Pc',
        width=LEG_WIDTH,
        height=BASE_HEIGHT - BASE_HEIGHT_ABOVE_GND,
        material=BASE_MATERIAL,
        color=BASE_COLOR,
        position=Position(
            x=0,
            y=BASE_MATERIAL.thickness,
            z=BASE_HEIGHT_ABOVE_GND,
        )
    )
    leg.add_child(LP2)
    return leg


def make_stretcher(length) -> RectangularComponent:
    return RectangularComponent(
        name='Stretcher',
        width=length,
        height=STRETCHER_WIDTH,
        material=BASE_MATERIAL,
        color=BASE_COLOR,
        position=Position(
            x=0,
            y=0,
            z=BASE_HEIGHT_ABOVE_GND,
        )
    )


def construct_end_panel() -> ComponentContainer:
    panel = ComponentContainer()
    # panel.add_child(PvAxes())
    L1 = make_leg()
    panel.add_child(L1)

    SS1 = make_stretcher(SHORT_STRETCHER_LENGTH)
    SS1.position.x = LEG_WIDTH
    SS1.position.y = SHORT_STRETCHER_INSET
    panel.add_child(SS1)

    SS2 = make_stretcher(SHORT_STRETCHER_LENGTH)
    SS2.position.x = LEG_WIDTH
    SS2.position.y = SHORT_STRETCHER_INSET
    SS2.position.z = BASE_HEIGHT - STRETCHER_WIDTH
    panel.add_child(SS2)

    L2 = make_leg()
    L2.position.x = BASE_LENGTH - LEG_WIDTH
    panel.add_child(L2)
    return panel


def construct_side_panel() -> ComponentContainer:
    C = ComponentContainer()
    # C.add_child(PvAxes())
    long_stretcher_length = BASE_WIDTH - 2*LEG_WIDTH
    long_stretcher_inset = BASE_MATERIAL.thickness

    LS1 = make_stretcher(long_stretcher_length)
    LS1.position.x = BASE_MATERIAL.thickness + long_stretcher_inset
    LS1.position.y = LEG_WIDTH
    LS1.orientation.rz = 90
    C.add_child(LS1)

    LS2 = make_stretcher(long_stretcher_length)
    LS2.position.x = BASE_MATERIAL.thickness + long_stretcher_inset
    LS2.position.y = LEG_WIDTH
    LS2.position.z = BASE_HEIGHT - STRETCHER_WIDTH
    LS2.orientation.rz = 90
    C.add_child(LS2)

    panel = RectangularComponent(
        parent=C,
        name='side panel',
        width=long_stretcher_length,
        height=INNER_HEIGHT_TOTAL,
        material=SIDE_PANEL_MATERIAL,
        color=SIDE_PANEL_COLOR,
        position=Position(
            x=BASE_MATERIAL.thickness + long_stretcher_inset,
            y=LEG_WIDTH,
            z=STRETCHER_WIDTH + BASE_HEIGHT_ABOVE_GND,
        ),
        orientation=Orientation(
            rx=0,
            ry=0,
            rz=90,
        )
    )

    return C


def construct_drawers(parent_cell, fixed_heights_internal, weighted_heights) -> None:
    face_to_box_bottom = 1/8
    box_bottom_to_interior_bottom = DWR_BOX_MATERIAL.thickness
    dwr_height_offset = face_to_box_bottom + box_bottom_to_interior_bottom
    nFixed = len(fixed_heights_internal)
    nWeighted = len(weighted_heights)
    dwr_sizes = [iSz + dwr_height_offset for iSz in fixed_heights_internal]
    dwr_dist = [*dwr_sizes, *weighted_heights]
    reveal = 1/16
    dwr_len = 24

    dwr_grid_left = ComponentGrid(
        parent=parent_cell,
        width=parent_cell.width,
        height=parent_cell.height,
        row_dist=np.array(dwr_dist),
        row_type=[*['fixed']*nFixed, *['weighted']*nWeighted],
        col_dist=np.array([1]),
        col_type=['weighted'],
        row_spacing=reveal,
        padding=(reveal,)*4,
    )

    cells = dwr_grid_left.cells[:, 0]
    for cell in cells:
        cell.add_child(
            SimpleInsetDrawer(
                opening_width=cell.width,
                opening_height=cell.height,
                length=dwr_len,
                face_material=DWR_FACE_MATERIAL,
                box_material=DWR_BOX_MATERIAL,
                bottom_material=DWR_BOTTOM_MATERIAL,
                reveal=(0,)*4,
                # spoof the SimpleInsetDrawer to make proper width
                drawer_slide_thickness=0.5-reveal,
                vertical_box_clearance=face_to_box_bottom,
                max_box_height=8,
                face_color=DWR_COLOR,
            )
        )
    print(f"actual dwr face heights = {dwr_grid_left.row_sizes}")
    dwr_sz_internal_chk = [
        face_size - dwr_height_offset for face_size in dwr_grid_left.row_sizes]
    print(f"internal dwr heights = {dwr_sz_internal_chk}")


def construct_base() -> ComponentContainer:
    base = ComponentContainer()
    base.add_child(construct_end_panel())
    e2 = construct_end_panel()
    e2.position.y = BASE_WIDTH-LEG_WIDTH
    base.add_child(e2)
    base.add_child(construct_side_panel())
    s2 = construct_side_panel()
    s2.position.x = BASE_LENGTH
    s2.position.y = BASE_WIDTH
    s2.orientation.rz = 180
    base.add_child(s2)

    top_structure_grid = ComponentGrid(
        parent=base,
        color=BASE_COLOR,
        width=INNER_LENGTH_TOTAL,
        height=INNER_WIDTH_TOTAL,
        row_dist=np.array([1]*2),
        row_type=['weighted']*2,
        col_dist=np.array([1]*2),
        col_type=['weighted']*2,
        row_spacing=BASE_MATERIAL.thickness,
        column_spacing=BASE_MATERIAL.thickness,
        padding=(0,)*4,
        position=Position(
            x=LEG_WIDTH,
            y=LEG_WIDTH - SHORT_STRETCHER_INSET,
            z=BASE_HEIGHT,
        ),
        orientation=Orientation(
            rx=-90,
            ry=0,
            rz=0,
        )
    )
    add_rails_stiles(top_structure_grid, STRETCHER_WIDTH,
                     BASE_MATERIAL, 'top base cross brace')

    bottom_structure_grid = ComponentGrid(
        parent=base,
        color=BASE_COLOR,
        width=INNER_LENGTH_TOTAL,
        height=INNER_WIDTH_TOTAL,
        row_dist=np.array([1]*2),
        row_type=['weighted']*2,
        col_dist=np.array([1]*2),
        col_type=['weighted']*2,
        row_spacing=BASE_MATERIAL.thickness,
        column_spacing=BASE_MATERIAL.thickness,
        padding=(0,)*4,
        position=Position(
            x=LEG_WIDTH,
            y=LEG_WIDTH - SHORT_STRETCHER_INSET,
            z=BASE_HEIGHT_ABOVE_GND + STRETCHER_WIDTH - DIV_PANEL_MATERIAL.thickness,
        ),
        orientation=Orientation(
            rx=-90,
            ry=0,
            rz=0,
        ),
    )
    add_rails_stiles(bottom_structure_grid, STRETCHER_WIDTH -
                     DIV_PANEL_MATERIAL.thickness, BASE_MATERIAL, 'bottom base cross brace')

    bottom_floor_panel = RectangularComponent(
        name='floor panel',
        parent=base,
        width=INNER_LENGTH_TOTAL,
        height=0.5*INNER_WIDTH_TOTAL + 0.5*BASE_MATERIAL.thickness,
        material=DIV_PANEL_MATERIAL,
        color=TOP_COLOR,
        position=Position(
            x=LEG_WIDTH,
            y=BASE_WIDTH - (LEG_WIDTH - SHORT_STRETCHER_INSET),
            z=BASE_HEIGHT_ABOVE_GND + STRETCHER_WIDTH - DIV_PANEL_MATERIAL.thickness,
        ),
        orientation=Orientation(
            rx=90,
            ry=0,
            rz=0,
        ),
    )

    main_face_grid = ComponentGrid(
        width=INNER_LENGTH_TOTAL,
        height=INNER_HEIGHT_TOTAL,
        row_dist=np.array([1]),
        row_type=['weighted'],
        col_dist=np.array([1, 1]),
        col_type=['weighted']*2,
        row_spacing=0,
        column_spacing=DIV_PANEL_MATERIAL.thickness,
        padding=(0,)*4,
        position=Position(
            x=LEG_WIDTH,
            y=SHORT_STRETCHER_INSET,
            z=STRETCHER_WIDTH + BASE_HEIGHT_ABOVE_GND,
        )
    )

    div = main_face_grid.col_div_cells[0]
    edge_band_material = Material.HARDWOOD_STAIN_1_4

    div.add_child(
        RectangularComponent(
            name='center div edge banding',
            width=DIV_PANEL_MATERIAL.thickness,
            height=div.height,
            material=edge_band_material,
            color=BASE_COLOR,
            position=Position(
                x=0,
                y=0,
                z=0,
            ),
            orientation=Orientation(
                rx=0,
                ry=0,
                rz=0,
            ),

        )
    )

    div.add_child(
        RectangularComponent(
            name='center div panel',
            width=FACE2FACE_WIDTH_TOTAL - 2*edge_band_material.thickness,
            height=div.height,
            material=DIV_PANEL_MATERIAL,
            color=DWR_COLOR,
            position=Position(
                x=DIV_PANEL_MATERIAL.thickness,
                y=edge_band_material.thickness,
                z=0,
            ),
            orientation=Orientation(
                rx=0,
                ry=0,
                rz=90,
            ),

        )
    )

    div.add_child(
        RectangularComponent(
            name='center div edge banding',
            width=DIV_PANEL_MATERIAL.thickness,
            height=div.height,
            material=edge_band_material,
            color=BASE_COLOR,
            position=Position(
                x=0,
                y=FACE2FACE_WIDTH_TOTAL - edge_band_material.thickness,
                z=0,
            ),
            orientation=Orientation(
                rx=0,
                ry=0,
                rz=0,
            ),
        )
    )
    base.add_child(main_face_grid)

    dwr_size_internal = [
        2.75,
        2.75,
        # 3.75,
        # 5.5,
        # 9.25 # weighted
    ]
    dwr_weights = [
        2,
        3,
    ]
    construct_drawers(main_face_grid.cells[0, 0], dwr_size_internal, dwr_weights)
    # dwr_size_internal = [
    #     2.75,
    #     2.75,
    #     2.75,
    #     2.75,
    #     # 3.75,
    #     # 5.5,
    #     # 9.25 # weighted
    # ]
    # dwr_weights = [
    #     # 2,
    #     # 3,
    # ]
    construct_drawers(main_face_grid.cells[0, 1], dwr_size_internal, dwr_weights)

    return base


if __name__ == "__main__":
    base_frame = ComponentContainer()
    base = construct_base()
    base.position.x = BASE_LENGTH_INSET[0]
    base.position.y = BASE_WIDTH_INSET
    base_frame.add_child(base)
    top = construct_torsion_box_top()
    base_frame.add_child(top)

    cmp = find_instances(base_frame, RectangularComponent)

    # savedir = 'outfeed_stl'
    # if not os.path.isdir(savedir):
    #     os.makedirs(savedir)
    # for cmp_ in cmp:
    #     mesh = cmp_.get_pv_mesh()

    #     fp = os.path.join(savedir, f"{cmp_.name}.stl")
    #     i = 1
    #     while os.path.isfile(fp):
    #         fp = os.path.join(savedir, f"{cmp_.name}_{i:d}.stl")
    #         i += 1

    #     mesh.save(fp)

    cmp_df = pd.DataFrame.from_dict(list(map(component_dict_serializer, cmp)))

    with sqlite3.connect('outfeed_components.db') as conn:
        cmp_df.to_sql('components', conn, method='multi', if_exists='replace')

    all_cmp_sorted = sorted(cmp, key=component_keyfunc)
    material_grps = itertools.groupby(all_cmp_sorted, key=component_keyfunc)
    for material_name, grp in material_grps:
        total = {'area': 0, 'volume': 0}
        material = Material[material_name]
        component_list = []
        for component in grp:
            component_list.append(component)
            total['area'] += component.area
            total['volume'] += component.volume

        qty = math.ceil(total[material.unit_type] /
                        (material.unit_size * material.unit_efficiency))

        print(
            f"material = {material_name}, "
            + f"total {material.unit_type} = {total[material.unit_type]:.0f}, "
            + f"requires {qty:d} {material.unit_descriptor} assuming "
            + f"{100*material.unit_efficiency:.0f}% efficiency per unit")

    base_frame.render(opacity=.9)
