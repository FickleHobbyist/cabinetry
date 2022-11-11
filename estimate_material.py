from cabinetry.components.lowers import LowerCabinetCase
from cabinetry.components.shelves import BandedShelf, StandardShelf
from cabinetry.components.uppers import UpperCabinetCase
from kitchen import construct_kitchen
from cabinetry.components import FaceFrame, RectangularComponent
from cabinetry.materials import Material
import collections
import itertools
import math


def find_instances(node, cls):
    # Implements DFS to find all instances of a given class on a node tree
    stack = collections.deque([node])
    instances = collections.deque()
    while stack:  # not empty
        item = stack.pop()
        if item.children:
            stack.extend(item.children)
        if isinstance(item, cls) and item not in instances:
            instances.append(item)
    return instances


def component_keyfunc(cmp):
    return cmp.material.name


def main():
    base_frame = construct_kitchen()
    all_cmp = find_instances(base_frame, RectangularComponent)
    all_cmp_sorted = sorted(all_cmp, key=component_keyfunc)
    material_grps = itertools.groupby(all_cmp_sorted, key=component_keyfunc)
    for material_name, grp in material_grps:
        total = {'area': 0, 'volume': 0}
        material = Material[material_name]
        for component in grp:
            total['area'] += component.area
            total['volume'] += component.volume

        qty = math.ceil(total[material.unit_type] /
                        (material.unit_size * material.unit_efficiency))

        print(
            f"material={material_name}, "
            + f"total {material.unit_type}={total[material.unit_type]:.0f}, "
            + f"requires {qty:d} {material.unit_descriptor} assuming "
            + f"{100*material.unit_efficiency:.0f}% efficiency per unit")

    base_frame.render()


if __name__ == "__main__":
    main()
