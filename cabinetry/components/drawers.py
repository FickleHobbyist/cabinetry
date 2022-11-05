from ..base import Position, Orientation
from . import ComponentContainer, FaceFrame, RectangularComponent, get_faceframe_factory
from ..materials import Material
from ..config import Config
import pyvista as pv
import numpy as np


class ShakerDrawerFace(FaceFrame):
    """A simple shaker style drawer face

    :param FaceFrame: _description_
    :type FaceFrame: _type_
    """

    def __init__(self,
                 opening_width: float,
                 opening_height: float,
                 width_rail: float = 2.0,
                 width_stile: float = 2.0,
                 *args, **kwargs) -> 'ShakerDrawerFace':
        """Instantiate a ShakerDrawerFace

        :param opening_width: Width of opening in which the drawer will fit
        :type opening_width: float
        :param opening_height: Height of opening in which the drawer will fit
        :type opening_height: float
        :param width_rail: Width of horizontal rail bordering the inset panel, defaults to 2.0
        :type width_rail: float, optional
        :param width_stile: Height of vertical stile bordering the inset panel, defaults to 2.0
        :type width_stile: float, optional
        :return: Constructed object
        :rtype: ShakerDrawerFace
        """        

        self.top_bottom_overlay = (
            0.5 * (Config.FACE_FRAME_MEMBER_WIDTH - Config.OVERLAY_GAP))
        self.side_overlay = Config.FACE_FRAME_MEMBER_WIDTH - 0.5*Config.OVERLAY_GAP
        super().__init__(box_width=0, box_height=0, box_material=Material.PLY_1_2,
                         width_rail=width_rail, width_stile=width_stile,
                         width=(opening_width+2*self.side_overlay),
                         height=opening_height+2*self.top_bottom_overlay,
                         *args, **kwargs)

        self.construct_components()

    def construct_components(self):
        """Generate renderable components for the drawer face."""
        super().construct_components()
        inset_thickness = Config.DRAWER_FACE_INSET_MATERIAL.thickness
        inset_dado_depth = inset_thickness
        inset_depth = Config.FACE_FRAME_MATERIAL.thickness - 2*inset_thickness
        cell = self.cells[0, 0]
        cell.add_child(
            RectangularComponent(
                name='Drawer Face Inset (Dadoed)',
                width=cell.width + 2*inset_dado_depth,
                height=cell.height + 2*inset_dado_depth,
                material=Config.DRAWER_FACE_INSET_MATERIAL,
                color=Config.DRAWER_FACE_INSET_COLOR,
                position=Position(
                    x=-inset_thickness,
                    y=inset_depth,
                    z=-inset_depth,
                )
            )
        )
        cell.add_child(
            RectangularComponent(
                name='Drawer Face Inset (Glue-on)',
                width=cell.width,
                height=cell.height,
                material=Config.DRAWER_FACE_INSET_MATERIAL,
                color=Config.DRAWER_FACE_INSET_COLOR,
                position=Position(
                    x=0,
                    y=inset_depth+inset_thickness,
                    z=0,
                )
            )
        )


class BlumDrawer(ComponentContainer):
    """Drawer based on instructions for Blum TANDEM Plus BLUMOTION Drawer Slides

    See https://www.blum.com/file/tdm563f_ma_dok_bus?country=us&language=en

    :param ComponentContainer: _description_
    :type ComponentContainer: _type_
    :raises ValueError: Box height may be no larger than (opening height - 25/32)
    :return: Constructed drawer object.
    :rtype: BlumDrawer
    """    
    DRAWER_BOTTOM_RECESS = 0.5
    DRAWER_HEIGHT_ABOVE_OPENING = 9/16

    def __init__(self,
                 opening_width: float,
                 opening_height: float,
                 box_height: float = None,
                 box_material: Material = None,
                 bottom_material: Material = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.opening_width = opening_width
        self.opening_height = opening_height
        self.box_material = box_material if box_material is not None else Material.PLY_1_2
        self.bottom_material = bottom_material if bottom_material is not None else Material.PLY_1_4
        self.box_height = box_height if box_height is not None else (
            opening_height - 25/32)
        if self.box_height > (opening_height - 25/32):
            raise ValueError(
                f"box_height of {self.box_height} too large. Value must be <= (opening_height - 25/32)")
        else:
            self.box_height = min(
                Config.MAX_DRAWER_BOX_HEIGHT, self.box_height)

        self.construct_components()

    def get_drawer_length(self) -> float:
        # Refer to table on pg 3 of document in class docstring
        inside_cabinet_depth = Config.LOWERS_DEPTH - \
            Config.LOWERS_CASE_MATERIAL.thickness
        if (21+15/16) <= inside_cabinet_depth <= (23+19/32):
            return 21
        elif (18+29/32) <= inside_cabinet_depth <= (20+9/16):
            return 18
        elif (15+29/32) <= inside_cabinet_depth <= (17+9/16):
            return 15
        elif (12+29/32) <= inside_cabinet_depth <= (14+9/16):
            return 12
        elif (10+15/32) <= inside_cabinet_depth <= (11+25/32):
            return 9

    def construct_components(self):
        bottom_dado_depth = 0.5 * self.box_material.thickness
        drawer_inside_width = self.opening_width - (1+15/16)
        drawer_outside_width = drawer_inside_width + 2*self.box_material.thickness
        drawer_length = self.get_drawer_length()
        bottom_width = drawer_inside_width + 2*bottom_dado_depth
        side_length = drawer_length - 2*self.box_material.thickness

        box = ComponentContainer(
            position=Position(
                # Center within opening
                x=0.5*(self.opening_width - drawer_outside_width),
                y=0,
                # Bottom clearance
                z=self.DRAWER_HEIGHT_ABOVE_OPENING,
            )
        )
        self.add_child(box)

        box.add_child(
            RectangularComponent(
                name='Drawer Left Side',
                width=side_length,
                height=self.box_height,
                material=self.box_material,
                color=Config.DRAWER_BOX_COLOR,
                position=Position(
                    x=self.box_material.thickness,
                    y=self.box_material.thickness,
                    z=0,
                ),
                orientation=Orientation(
                    rx=0,
                    ry=0,
                    rz=90,
                ),
            )
        )
        box.add_child(
            RectangularComponent(
                name='Drawer Right Side',
                width=side_length,
                height=self.box_height,
                material=self.box_material,
                color=Config.DRAWER_BOX_COLOR,
                position=Position(
                    x=2*self.box_material.thickness + drawer_inside_width,
                    y=self.box_material.thickness,
                    z=0,
                ),
                orientation=Orientation(
                    rx=0,
                    ry=0,
                    rz=90,
                ),
            )
        )
        box.add_child(
            RectangularComponent(
                name='Drawer Bottom',
                width=bottom_width,
                height=side_length+2*bottom_dado_depth,
                material=self.bottom_material,
                color=Config.DRAWER_BOX_COLOR,
                position=Position(
                    x=self.box_material.thickness - bottom_dado_depth,
                    y=self.box_material.thickness - bottom_dado_depth,
                    z=self.bottom_material.thickness + self.DRAWER_BOTTOM_RECESS,
                ),
                orientation=Orientation(
                    rx=-90,
                    ry=0,
                    rz=0,
                ),
            )
        )
        box.add_child(
            RectangularComponent(
                name='Drawer False Front',
                width=drawer_inside_width + 2*self.box_material.thickness,
                height=self.box_height,
                material=self.box_material,
                color=Config.DRAWER_BOX_COLOR,
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
        box.add_child(
            RectangularComponent(
                name='Drawer Back',
                width=drawer_inside_width + 2*self.box_material.thickness,
                height=self.box_height,
                material=self.box_material,
                color=Config.DRAWER_BOX_COLOR,
                position=Position(
                    x=0,
                    y=side_length+self.box_material.thickness,
                    z=0,
                ),
                orientation=Orientation(
                    rx=0,
                    ry=0,
                    rz=0,
                ),
            )
        )
        face = ShakerDrawerFace(
            name='Drawer Face',
            opening_width=self.opening_width,
            opening_height=self.opening_height,
            row_dist=np.array([1]),
            row_type=['weighted'],
            col_dist=np.array([1]),
            col_type=['weighted'],
            position=Position(
                x=0,
                y=-Config.FACE_FRAME_MATERIAL.thickness,
                z=0,
            )
        )
        face.position.x = -face.side_overlay
        face.position.z = -face.top_bottom_overlay
        self.add_child(face)
