from ..config import Config
from ..components import RectangularComponent
from ..materials import Material
from . import Position
from . import ShakerFramedPanel


class ShakerDoor(ShakerFramedPanel):
    """A simple shaker style cabinet door."""

    def __init__(self,
                 hinge_side: str = 'left',
                 hinge_stile_factor: str = 'double',
                 is_paired: bool = True,
                 *args, **kwargs) -> 'ShakerDoor':
        """Object constructor

        :param hinge_side: 'left' or 'right', indicates the hinged side of the door. Defaults to 'left'
        :type hinge_side: str, optional
        :param hinge_stile: 'single' or 'double', indicates whether the hinge-side stile is single or double width. Defaults to 'single'
        :type hinge_stile: str, optional
        :param is_paired: Indicates whether hinge-opposite side should overlay next to another door in the same FaceFrame, defaults to True
        :type is_paired: bool, optional
        :raises ValueError: arg 'hinge_stile' must be 'single' or 'double'
        :raises ValueError: arg 'hinge_side' must be 'left' or 'right'
        :return: Constructed ShakerDoor object
        :rtype: ShakerDoor
        """
        large_overlay = Config.FACE_FRAME_MEMBER_WIDTH - 0.5*Config.OVERLAY_GAP
        small_overlay = 0.5 * \
            (Config.FACE_FRAME_MEMBER_WIDTH - Config.OVERLAY_GAP)
        match hinge_stile_factor:
            case 'single':
                hinge_side_overlay = small_overlay
            case 'double':
                hinge_side_overlay = large_overlay
            case _:
                raise ValueError(
                    f"arg 'hinge_stile_factor' must be 'single' or 'double'")

        if is_paired:
            other_overlay = small_overlay
        else:
            other_overlay = large_overlay

        pull_width = 1
        pull_height = 1
        match hinge_side:
            case 'left':
                super().__init__(left_overlay=hinge_side_overlay,
                                 right_overlay=other_overlay,
                                 *args, **kwargs)
                hinge_pos = Position(
                    x=self.width - 0.5*(self.padding[2] + pull_width), # pull on right
                    y=-self.material.thickness,
                    z=0.5*(self.height - pull_height),
                )
            case 'right':
                super().__init__(left_overlay=other_overlay,
                                 right_overlay=hinge_side_overlay,
                                 *args, **kwargs)
                hinge_pos = Position(
                    x=0.5*(self.padding[0] - pull_width), # pull on left
                    y=-self.material.thickness,
                    z=0.5*(self.height - pull_height),
                )
            case _:
                raise ValueError(f"arg 'hinge_side' must be 'left' or 'right'")

        self.add_child(
            RectangularComponent(
                width=pull_width,
                height=pull_height,
                material=Material.HARDWOOD_3_4,
                position=hinge_pos,
                color='red',
            )
        )