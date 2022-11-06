from abc import abstractmethod
from dataclasses import dataclass, field
from warnings import warn
from ..config import Config  # .. refers to cabinetry top level package
from ..base import Poseable, Position, RenderTree
from ..materials import Material
import pyvista as pv
import numpy as np


class ComponentContainer(RenderTree, Poseable):
    """Useful for categorizing groups of components

    :param width: width of component
    :type width: float
    :param height: height of component
    :type height: float
    :param material: Material class of component. See cabinetry.materials.Material.
    :type material: Material
    :return: Constructed object
    :rtype: RectangularComponent
    """

    def __init__(self, *args, **kwargs):
        clr = kwargs.pop('color', None)
        super(ComponentContainer, self).__init__(color=clr, *args, **kwargs)


class RectangularComponent(RenderTree, Poseable):
    """Low level component which produces renderable geometry"""

    def __init__(self, width: float, height: float, material: Material, **kwargs) -> 'RectangularComponent':
        """Class constructor"""
        super(RectangularComponent, self).__init__(**kwargs)
        self.width: float = width
        self.height: float = height
        self.material: Material = material

    @property
    def area(self) -> float:
        """area = width * height

        :return: Area of large faces of component
        :rtype: float
        """
        return self.width * self.height

    @property
    def volume(self) -> float:
        """volume = area * material.thickness

        :return: Volume of component
        :rtype: float
        """
        return self.area * self.material.thickness

    def get_pv_mesh(self) -> pv.PolyData:
        xMin = 0
        xMax = self.width
        yMin = 0
        yMax = self.material.thickness
        zMin = 0
        zMax = self.height
        M = self.get_frame_to_base()

        box = pv.Box((xMin, xMax, yMin, yMax, zMin, zMax),
                     level=0, quads=False)
        box.transform(M)
        return box


@dataclass(init=True, repr=True)
class GridRowOrCol():
    size_type: str = 'weighted'
    size: float = 1.
    _size_type: str = field(default='weighted', init=False, repr=False)

    @property
    def size_type(self):
        return self._size_type

    @size_type.setter
    def size_type(self, val):
        valid_types = ['weighted', 'fixed']
        if type(val) is property:
            val = GridRowOrCol._size_type  # use default value
        if val not in valid_types:
            raise ValueError(
                f"Invalid size_type '{val}'. size_type must be one of: {valid_types}")
        else:
            self._size_type = val

    @staticmethod
    def compute_size_and_position(rows_or_cols: list['GridRowOrCol'], total_space, spacing):
        n = len(rows_or_cols)
        # remove spaces between RowsOrCols
        cell_space = total_space - (n-1)*spacing
        # Collect array of sizes and list of types
        rc_sizes = np.array(
            list(map(lambda rc: rc.size, rows_or_cols)), dtype='float')
        rc_types = list(map(lambda rc: rc.size_type, rows_or_cols))
        # Identify indices with weighted type
        rc_weighted_id = np.array(
            list(map(lambda s: s == 'weighted', rc_types)), dtype='bool')
        # Remove fixed space from cell space
        weighted_space = cell_space - sum(rc_sizes[~rc_weighted_id])
        if weighted_space <= 0 and any(rc_weighted_id):
            raise ValueError(
                f"Sum of fixed rows/cols is greater than available space")
        rc_proportions = rc_sizes[rc_weighted_id] / \
            sum(rc_sizes[rc_weighted_id])
        rc_sizes[rc_weighted_id] = rc_proportions * weighted_space

        return rc_sizes, rows_or_cols[0]._compute_linear_pos(rc_sizes, spacing, total_space)

    @staticmethod
    @abstractmethod
    def _compute_linear_pos(sizes, spacing, total_space): pass


class GridRow(GridRowOrCol):
    @staticmethod
    def _compute_linear_pos(row_sizes, spacing, total_space):
        # for rows, return linear position such that index 0 is at the far end
        linear_pos = total_space - \
            (np.cumsum(row_sizes) + np.arange(0, len(row_sizes), 1) * spacing)
        return linear_pos


class GridCol(GridRowOrCol):
    @staticmethod
    def _compute_linear_pos(col_sizes, spacing, _):
        # for cols, return linear position such that index 0 is at left side
        linear_pos = np.arange(0, len(col_sizes), 1) * spacing + \
            np.concatenate(([0], np.cumsum(col_sizes[:-1])), axis=0)
        return linear_pos


class GridCell(ComponentContainer):
    """Low-level element of a ComponentGrid."""

    def __init__(self,
                 width: float,
                 height: float,
                 *args, **kwargs):
        super(GridCell, self).__init__(*args, **kwargs)
        # width and height are managed by ComponentGrid
        self.width: float = width
        self.height: float = height


class ComponentGrid(ComponentContainer):
    """Constructs a structured grid of GridCell component containers.

    Currently designed to be immutable once constructed.
    """

    def __init__(self,
                 width: float,
                 height: float,
                 row_dist: np.array = None,
                 row_type: list[str] = None,
                 col_dist: np.array = None,
                 col_type: list[str] = None,
                 row_spacing: float = 0,
                 column_spacing: float = 0,
                 padding: tuple = None, *args, **kwargs):
        super(ComponentGrid, self).__init__(*args, **kwargs)
        self.width: float = width
        self.height: float = height
        row_dist = row_dist if row_dist is not None else np.array([1])
        row_type = row_type if row_type is not None else ['weighted']
        col_dist = col_dist if col_dist is not None else np.array([1])
        col_type = col_type if col_type is not None else ['weighted']

        self.rows: list[GridRow] = []
        self.cols: list[GridCol] = []

        for typ, sz in zip(row_type, row_dist):
            self.add_row(typ, sz)
        for typ, sz in zip(col_type, col_dist):
            self.add_col(typ, sz)

        # Padding tuple (left, bottom, right, top) - controls inner position of grid
        self.padding = padding if padding is not None else (0, 0, 0, 0)
        self.row_spacing = row_spacing
        self.column_spacing = column_spacing

        self.construct_cells()

    def add_row(self, size_type, size):
        """Add a row to the bottom of the grid."""
        self.rows.append(GridRow(size_type, size))

    def add_col(self, size_type, size):
        """Add a row to the right of the grid."""
        self.cols.append(GridCol(size_type, size))

    def construct_cells(self):
        cells: list[GridCell] = []
        # Grid origin located at bottom left corner of padded region
        grid_pos_x = self.padding[0]
        grid_pos_y = self.padding[1]
        # Subtract top+bottom padding from height
        self.grid_height = self.height - (self.padding[3] + self.padding[1])
        # Subtract left+right padding from width
        self.grid_width = self.width - (self.padding[0] + self.padding[2])

        # Get row/col positions and sizes
        row_sizes, row_pos = GridRow.compute_size_and_position(
            self.rows, self.grid_height, self.row_spacing)
        col_sizes, col_pos = GridCol.compute_size_and_position(
            self.cols, self.grid_width, self.column_spacing)

        row_pos += grid_pos_y  # account for bottom padding
        col_pos += grid_pos_x  # account for left padding
        self.row_pos = row_pos
        self.row_sizes = row_sizes
        self.col_pos = col_pos
        self.col_sizes = col_sizes

        # Construct full grid of row and column positions and sizes
        r_pos_grid, c_pos_grid = np.meshgrid(row_pos, col_pos, indexing='ij')
        r_sz_grid, c_sz_grid = np.meshgrid(row_sizes, col_sizes, indexing='ij')

        for r_pos, c_pos, r_sz, c_sz in zip(r_pos_grid.reshape(r_pos_grid.size,).tolist(),
                                            c_pos_grid.reshape(
                                                c_pos_grid.size,).tolist(),
                                            r_sz_grid.reshape(
                                                r_sz_grid.size,).tolist(),
                                            c_sz_grid.reshape(c_sz_grid.size,).tolist()):

            cellName = f"{self.name}_cell_{len(cells):d}"
            # print(f"constructed GridCell: '{cellName}', pos: {(r_pos, c_pos)}, size: {(r_sz, c_sz)}")
            gc = GridCell(
                name=cellName,
                height=r_sz,
                width=c_sz,
                position=Position(x=c_pos, y=0, z=r_pos),
            )
            self.add_child(gc)
            cells.append(gc)

        self.cells = np.array(cells).reshape(len(self.rows), len(self.cols))
        return self.cells


class FaceFrame(ComponentGrid):
    """Cabinet FaceFrame component."""    
    def __init__(self,
                 box_width: float,
                 box_height: float,
                 box_material: Material,
                 width_rail: float = Config.FACE_FRAME_MEMBER_WIDTH,
                 width_stile: float = Config.FACE_FRAME_MEMBER_WIDTH,
                 side_overhang: float = 1/8,
                 color: pv.color_like = Config.FACE_FRAME_COLOR,
                 *args, **kwargs):
        """Object constructor

        :param box_width: Outer width of box
        :type box_width: float
        :param box_height: Outer height of box
        :type box_height: float
        :param box_material: Material of box to which the FaceFrame will be attached
        :type box_material: Material
        :param width_rail: Width of horizontal divider components, defaults to Config.FACE_FRAME_MEMBER_WIDTH
        :type width_rail: float, optional
        :param width_stile: Width of vertical divider components, defaults to Config.FACE_FRAME_MEMBER_WIDTH
        :type width_stile: float, optional
        :param side_overhang: Excess width on either side of cabinet, defaults to 1/8
        :type side_overhang: float, optional
        :param color: Color for frame divider components, defaults to Config.FACE_FRAME_COLOR
        :type color: pv.color_like, optional
        """
        width = kwargs.pop('width', box_width+2*side_overhang)
        height = kwargs.pop('height', box_height +
                            (width_rail - box_material.thickness))
        # left, bottom, right, top
        padding = kwargs.pop('padding', (width_stile, width_rail)*2)
        super(FaceFrame, self).__init__(width=width,
                                        height=height,
                                        padding=padding,
                                        row_spacing=width_rail,
                                        column_spacing=width_stile,
                                        *args, **kwargs)

        self.width_rail = width_rail
        self.width_stile = width_stile
        self.side_overhang = side_overhang
        self.material = Config.FACE_FRAME_MATERIAL
        self.color = color

    def construct_test_components(self):
        # \/\/ Testing Only \/\/
        # Use DFS to add RectangularComponents to lowest level GridCell in FaceFrame tree
        stack = self.cells.reshape(self.cells.size,).tolist()
        i = 0
        while stack:
            item = stack.pop()
            if item.children:  # not empty
                stack.extend(item.children)
            elif isinstance(item, GridCell):
                # print(cell)
                item.add_child(
                    RectangularComponent(
                        name=f"component_{i}",
                        height=item.height,
                        width=item.width,
                        material=self.material,
                        color='red',
                    )
                )
                i += 1
        # /\/\ Testing Only /\/\

    def construct_components(self):
        # DFS on to find FaceFrame components in FaceFrame tree
        # stack = self.cells.reshape(self.cells.size,).tolist()
        stack = [self]
        while stack:
            item = stack.pop()  # GridCell, FaceFrame, or possibly another component item
            if item.children:  # not empty
                stack.extend(item.children)
            if isinstance(item, FaceFrame):
                item.construct_rails_and_stiles()

    def construct_rails_and_stiles(self):
        rail_anchors = (self.row_pos + self.row_sizes).tolist()
        rail_anchors.append(0)
        stile_anchors = (self.col_pos + self.col_sizes).tolist()
        stile_anchors.insert(0, 0)  # add an anchor at 0
        # Make full height stiles sized by left/right padding
        for s_pos, s_width in zip([stile_anchors[0], stile_anchors[-1]], [self.padding[0], self.padding[2]]):
            if s_width > 0:
                self.add_child(
                    RectangularComponent(
                        width=s_width,
                        height=self.height,
                        material=self.material,
                        # x=width, y=thickness, z=height
                        position=Position(x=s_pos, y=0, z=0),
                        color=self.color,
                    )
                )

        # Make rails sized by top/bottom padding
        for r_pos, r_width in zip([rail_anchors[0], rail_anchors[-1]], [self.padding[3], self.padding[1]]):
            if r_width > 0:
                self.add_child(
                    RectangularComponent(
                        width=self.grid_width,
                        height=r_width,
                        material=self.material,
                        # x=width, y=thickness, z=height
                        position=Position(x=self.padding[0], y=0, z=r_pos),
                        color=self.color,
                    )
                )

        # Make grid height stiles within padding. Use col right edges as anchors
        for c_pos in stile_anchors[1:-1]:
            self.add_child(
                RectangularComponent(
                    width=self.width_stile,
                    height=self.grid_height,
                    material=self.material,
                    # x=width, y=thickness, z=height
                    position=Position(x=c_pos, y=0, z=self.padding[1]),
                    color=self.color,
                )
            )

        cells = self.cells
        # for every row in cells except for first (upper-most) row, each cell gets a rail above it
        for row in cells[1:, :]:
            for cell in row:
                self.add_child(
                    RectangularComponent(
                        width=cell.width,
                        height=self.width_rail,
                        material=self.material,
                        # x=width, y=thickness, z=height
                        position=Position(
                            x=cell.position.x,
                            y=0,
                            z=cell.position.z+cell.height
                        ),
                        color=self.color,
                    )
                )


class ShakerFramedPanel(FaceFrame):
    """A simple shaker style panel and frame. Used for doors and drawer faces."""

    def __init__(self,
                 opening_width: float,
                 opening_height: float,
                 width_rail: float = 2.0,
                 width_stile: float = 2.5,
                 top_bottom_overlay: float = None,
                 left_overlay: float = None,
                 right_overlay: float = None,
                 *args, **kwargs) -> 'ShakerFramedPanel':
        """Instantiate a ShakerFramedPanel

        :param opening_width: Width of opening in which the drawer will fit
        :type opening_width: float
        :param opening_height: Height of opening in which the drawer will fit
        :type opening_height: float
        :param width_rail: Width of horizontal rail bordering the inset panel, defaults to 2.0
        :type width_rail: float, optional
        :param width_stile: Height of vertical stile bordering the inset panel, defaults to 2.5
        :type width_stile: float, optional
        :return: Constructed object
        :rtype: ShakerFramedPanel
        """
        if top_bottom_overlay is None:
            self.top_bottom_overlay = (
                0.5 * (Config.FACE_FRAME_MEMBER_WIDTH - Config.OVERLAY_GAP))
        else:
            self.top_bottom_overlay = top_bottom_overlay
        
        if left_overlay is None:
            self.left_overlay = Config.FACE_FRAME_MEMBER_WIDTH - 0.5*Config.OVERLAY_GAP
        else:
            self.left_overlay = left_overlay

        if right_overlay is None:
            self.right_overlay = self.left_overlay
        else:
            self.right_overlay = right_overlay
        
        super().__init__(box_width=0, box_height=0, box_material=Material.PLY_1_2,
                         width_rail=width_rail, width_stile=width_stile,
                         width=(opening_width+(self.left_overlay + self.right_overlay)),
                         height=opening_height+2*self.top_bottom_overlay,
                         *args, **kwargs)
        self.inset_thickness = Config.FRAMED_PANEL_INSET_MATERIAL.thickness
        self.inset_depth = Config.FACE_FRAME_MATERIAL.thickness - 2*self.inset_thickness

        if ('position' in kwargs.keys()
                or any(isinstance(arg, Position) for arg in args)):
            warn('position argument is overridden in ShakerFramedPanel \
                and will have no effect')
        self.construct_components()
        self.correct_position()

    def correct_position(self):
        # Anchor such that origin is at bottom left corner of opening
        # and appropriate overlay is established
        self.position.x = -self.left_overlay
        self.position.y = -self.material.thickness
        self.position.z = -self.top_bottom_overlay

    def construct_components(self):
        """Generate renderable components for the drawer face."""
        super().construct_components()

        inset_dado_depth = self.inset_thickness

        cell = self.cells[0, 0]
        cell.add_child(
            RectangularComponent(
                name='Inset Panel (Dadoed)',
                width=cell.width + 2*inset_dado_depth,
                height=cell.height + 2*inset_dado_depth,
                material=Config.FRAMED_PANEL_INSET_MATERIAL,
                color=Config.FRAMED_PANEL_INSET_COLOR,
                position=Position(
                    x=-self.inset_thickness,
                    y=self.inset_depth,
                    z=-self.inset_depth,
                )
            )
        )
