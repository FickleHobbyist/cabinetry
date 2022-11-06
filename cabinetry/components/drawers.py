from ..config import Config
from ..base import Position, Orientation
from ..materials import Material
from . import ComponentContainer, RectangularComponent, ShakerFramedPanel


class ShakerDrawerFace(ShakerFramedPanel):
    """A simple shaker style drawer face."""

    def __init__(self, *args, **kwargs) -> 'ShakerDrawerFace':
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
        super().__init__(*args, **kwargs)

        self.construct_components()

    def construct_components(self):
        """Generate renderable components for the drawer face."""
        super().construct_components()
        cell = self.cells[0, 0]
        cell.add_child(
            RectangularComponent(
                name='Flush Rear Panel (Glue-on)',
                width=cell.width,
                height=cell.height,
                material=Config.FRAMED_PANEL_INSET_MATERIAL,
                color=Config.FRAMED_PANEL_INSET_COLOR,
                position=Position(
                    x=0,
                    y=self.inset_depth+self.inset_thickness,
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
        side_dado_depth = 0.5 * self.box_material.thickness
        drawer_inside_width = self.opening_width - (1+15/16)
        drawer_outside_width = drawer_inside_width + 2*self.box_material.thickness
        drawer_length = self.get_drawer_length()
        bottom_width = drawer_inside_width + 2*bottom_dado_depth
        side_length = drawer_length

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
                    y=0,
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
                    y=0,
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
                height=side_length-2*bottom_dado_depth,
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
                width=drawer_inside_width + 2*side_dado_depth,
                height=self.box_height,
                material=self.box_material,
                color=Config.DRAWER_BOX_COLOR,
                position=Position(
                    x=self.box_material.thickness-side_dado_depth,
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
                width=drawer_inside_width + 2*side_dado_depth,
                height=self.box_height,
                material=self.box_material,
                color=Config.DRAWER_BOX_COLOR,
                position=Position(
                    x=self.box_material.thickness-side_dado_depth,
                    y=side_length-self.box_material.thickness,
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
        )
        self.add_child(face)
