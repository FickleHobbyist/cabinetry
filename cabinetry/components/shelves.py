from ..config import Config
from ..base import Position, Orientation
from ..materials import Material
from . import ComponentContainer, RectangularComponent


class StandardShelf(ComponentContainer):
    def __init__(self,
                 width: float,
                 depth: float,
                 material: Material = Config.SHELF_MATERIAL,
                 *args, **kwargs):
        name = kwargs.pop('name', 'shelf')
        super().__init__(name=name, *args, **kwargs)
        self.shelf = RectangularComponent(
            name='Shelf Panel',
            height=depth,
            width=width,
            material=material,
            color=Config.SHELF_COLOR,
            position=Position(
                x=0,
                y=0,
                z=material.thickness,
            ),
            orientation=Orientation(
                rx=-90,
                ry=0,
                rz=0,
            ),
        )
        self.add_child(self.shelf)


class BandedShelf(StandardShelf):
    def __init__(self,
                 width: float,
                 depth: float,
                 material: Material = Config.SHELF_MATERIAL,
                 band_depth: float = Config.SHELF_BANDING_THICKNESS,
                 band_material: Material = Config.SHELF_BANDING_MATERIAL,
                 *args, **kwargs):
        my_pos = kwargs.pop('position', Position())
        super().__init__(width=width,
                         depth=(depth-band_depth),
                         material=material,
                         *args, **kwargs)
        self.shelf.position.y = band_depth
        self.position = my_pos
        self.banding = RectangularComponent(
            name='Shelf Banding',
            height=band_depth,
            width=width,
            material=band_material,
            color='red',
            position=Position(
                x=0,
                y=0,
                z=band_material.thickness,
            ),
            orientation=Orientation(
                rx=-90,
                ry=0,
                rz=0,
            ),
        )
        self.add_child(self.banding)
