from ..config import Config
from ..base import Position, Orientation
from ..materials import Material
from . import ComponentContainer, RectangularComponent, ShakerFramedPanel
from typing import Union

class Qtr3DrawerBox(ComponentContainer):
    def __init__(self,
                 width: float,
                 height: float,
                 length: float,
                 box_material: Material,
                 bottom_material: Material,
                 **kwargs):
        self.width = width
        self.height = height
        self.length = length
        self.box_material = box_material
        self.bottom_material = bottom_material
        # TODO: Assert bottom material thickness is ~ half box material thickness (within some tolerance?)
        super().__init__(**kwargs)

        L_Side = self.make_side()
        self.add_child(L_Side)
        R_Side = self.make_side()
        R_Side.position.x = self.width
        self.add_child(R_Side)

        front_end = self.make_end()
        self.add_child(front_end)
        back_end = self.make_end()
        back_end.position.y = self.length - self.box_material.thickness
        self.add_child(back_end)

        self.add_child(self.make_bottom())

    def make_side(self) -> RectangularComponent:
        side = RectangularComponent(
            name='Qtr3DrawerBox Side',
            width=self.length,
            height=self.height,
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
        return side

    def make_end(self) -> RectangularComponent:
        end = RectangularComponent(
            name='Qtr3DrawerBox End',
            width=self.width - self.box_material.thickness,
            height=self.height,
            material=self.box_material,
            color=Config.DRAWER_BOX_COLOR,
            position=Position(
                x=0.5*self.box_material.thickness,
                y=0,
                z=0,
            ),
            orientation=Orientation(
                rx=0,
                ry=0,
                rz=0,
            ),
        )
        return end

    def make_bottom(self) -> RectangularComponent:
        bottom = RectangularComponent(
            name='Qtr3DrawerBox Bottom',
            width=self.width - self.box_material.thickness,
            height=self.length - self.box_material.thickness,
            material=self.bottom_material,
            color=Config.DRAWER_BOX_COLOR,
            position=Position(
                x=0.5*self.box_material.thickness,
                y=0.5*self.box_material.thickness,
                z=self.bottom_material.thickness + 0.5*self.box_material.thickness,
            ),
            orientation=Orientation(
                rx=-90,
                ry=0,
                rz=0,
            ),
        )
        return bottom


class SimpleInsetDrawer(ComponentContainer):
    def __init__(self,
                 opening_width: float,
                 opening_height: float,
                 length: float,
                 face_material: Material,
                 box_material: Material,
                 bottom_material: Material,
                 reveal: Union[float, tuple[float]],
                 drawer_slide_thickness: float = 0.5,
                 vertical_box_clearance: float = 0.5,
                 max_box_height: float = 4,
                 face_color=Config.DRAWER_BOX_COLOR,
                 **kwargs):
        self.opening_width = opening_width
        self.opening_height = opening_height
        self.length = length
        self.face_material = face_material
        self.reveal = reveal
        self.drawer_slide_thickness = drawer_slide_thickness
        self.vertical_box_clearance = vertical_box_clearance
        super().__init__(**kwargs)
        if isinstance(reveal, float):
            reveal = (reveal,)*4
        elif isinstance(reveal, tuple) and len(reveal) == 1:
            reveal = reveal*4
        else:
            # TODO: Assert len(reveal) == 4
            # Reveal is (left, bottom, right, top)
            ...

        face_width = opening_width - (reveal[0] + reveal[2])
        face_height = opening_height - (reveal[1] + reveal[3])
        
        self.face = RectangularComponent(
            name='inset drawer face',
            width=face_width,
            height=face_height,
            material=self.face_material,
            color=face_color,
            position=Position(
                x=reveal[0],
                y=0,
                z=reveal[1],
            ),
            orientation=Orientation(
                rx=0,
                ry=0,
                rz=0,
            ),
        )
        self.add_child(self.face)
        box_width = opening_width - 2*drawer_slide_thickness
        box_height = min(opening_height - 2*vertical_box_clearance, max_box_height)
        self.box = Qtr3DrawerBox(
            width=box_width,
            height=box_height,
            length=length,
            box_material=box_material,
            bottom_material=bottom_material,
            position=Position(
                x=drawer_slide_thickness,
                y=face_material.thickness,
                z=vertical_box_clearance,
            ),
        )
        self.add_child(self.box)




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

        if opening_width >= 24:
            default_box_material = Material.PLY_3_4_4x8
            default_bottom_material = Material.PLY_1_2_4x8
        else:
            default_box_material = Material.PLY_1_2_4x8
            default_bottom_material = Material.PLY_1_4_LITERAL_4x8

        self.box_material = box_material if box_material is not None else default_box_material
        self.bottom_material = bottom_material if bottom_material is not None else default_bottom_material
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
