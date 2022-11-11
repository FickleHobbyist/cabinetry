from ..components.shelves import StandardShelf
from ..base import Position
from ..config import Config


def faceframe_with_shelves(
    face_factory: callable,
    shelf_class: callable = StandardShelf,
) -> callable:
    def add_shelves(*args, **kwargs):
        face = face_factory(*args, **kwargs)
        case = face.parent.case
        
        for row_div, i in zip(face.row_div_cells, range(0, len(face.row_div_cells))):
            row_div.add_child(
                shelf_class(
                    name=f"shelf_{i:02d}",
                    width=case.box_width_inside,
                    depth=case.box_depth,
                    position=Position(
                        x=-0.5*abs(case.box_width_inside-row_div.width),
                        y=face.material.thickness,
                        z=row_div.height - Config.SHELF_MATERIAL.thickness,
                    )
                )
            )
        return face
    return add_shelves