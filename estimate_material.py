from cabinetry.components.uppers import UpperCabinet
from cabinetry.components.lowers import LowerCabinet
from cabinetry.components.shelves import StandardShelf
from cabinetry.components.drawers import BlumDrawer
from cabinetry.components.doors import ShakerDoor
from cabinetry.components import RectangularComponent
from cabinetry.materials import Material
from kitchen import construct_kitchen
import pandas as pd
import collections
import itertools
import math
import sqlite3


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

def component_dict_serializer(cmp):
    long_dim = max(cmp.width, cmp.height)
    short_dim = min(cmp.width, cmp.height)
    return {
        'name': cmp.name,
        'width': long_dim,
        'height': short_dim,
        'thickness': cmp.material.thickness,
        'area': cmp.area,
        'volume': cmp.volume,
        'material_name': cmp.material.name
    }

def main():
    base_frame = construct_kitchen()
    items_to_count = [
        BlumDrawer,
        ShakerDoor,
        StandardShelf,
        LowerCabinet,
        UpperCabinet,
        RectangularComponent,
    ]
    print("-"*10 + "Component Summary" + "-"*10)
    counts = {}
    instances = {}
    for item in items_to_count:
        instances[item] = find_instances(base_frame, item)
        counts[item] = len(instances[item])
        print(f"Found {counts[item]} instances of {item.__name__}")

    print("-"*10 + "Material Summary" + "-"*10)
    all_cmp = instances[RectangularComponent]
    all_cmp_sorted = sorted(all_cmp, key=component_keyfunc)

    cmp_df = pd.DataFrame.from_dict(list(map(component_dict_serializer, all_cmp_sorted)))

    with sqlite3.connect('components.db') as conn:
        cmp_df.to_sql('components', conn, method='multi', if_exists='replace')


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

    base_frame.render()


if __name__ == "__main__":
    main()
