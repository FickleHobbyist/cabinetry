# Cabinetry
This repository contains geometric representations of household cabinetry, which can be utilized to estimate material quantities. It was created as an exercise in learning python in support of estimating material cost for an upcoming kitchen renovation. It is absolutely not a representation of the most efficient means of generating parametric cabinet geometry. Nevertheless, we press on...

# Getting Started
Clone this repository to your local drive, [create a virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment), then [install the requirements](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#using-requirements-files) using `./requirements.txt`

# Example Output

## Cabinetry Model (Python)
From `>> py .\estimate_material.py`, the following output is produced:

    ----------Component Summary----------
    Found 22 instances of BlumDrawer
    Found 28 instances of ShakerDoor
    Found 24 instances of StandardShelf
    Found 19 instances of LowerCabinet
    Found 6 instances of UpperCabinet
    Found 1087 instances of RectangularComponent
    ----------Material Summary----------
    material = HARDWOOD_BANDING_PLY_3_4, total volume = 119, requires 2 board ft assuming 80% efficiency per unit
    material = HARDWOOD_PAINT_3_4, total volume = 16847, requires 147 board ft assuming 80% efficiency per unit
    material = HARDWOOD_STAIN_3_4, total volume = 1048, requires 10 board ft assuming 80% efficiency per unit
    material = PLY_1_2, total area = 8421, requires 3 sheets assuming 80% efficiency per unit
    material = PLY_1_4, total area = 30753, requires 9 sheets assuming 80% efficiency per unit
    material = PLY_3_4, total area = 76526, requires 21 sheets assuming 80% efficiency per unit
    

![Python Cabinetry Model](doc/Kitchen%20Model%20Python%20Iso.png)

## Reference Model (Sketchup)
![Sketchup Model](doc/Kitchen%20Model%20Sketchup%20Iso.png)

# To-Do
- [x] Create DrawerFace component.
- [x] Create DrawerBox component.
- [x] Create Door component (probably reuse DrawerFace, consider abstracting).
- [x] Establish method for connecting DrawerBox, DrawerFace, Door to GridCells in each FaceFrame.
- [x] Create config class for common.
- [x] Create upper cabinet box.
- [x] Fine tune material selection for drawer boxes based on drawer size. Larger drawers need thicker material for the box.
- [x] Establish method for generating a bill of materials
    - For rough estimating, compute total area and volume in each material category.
    - Use fudge factor on total ply area / (48x96) for number of sheets required.
    - Use total volume to estimate board feet of hardwood type materials required plus fudge factor for waste.
- [x] Adjust drawer box components to account for length increment due to rabbets & dadoes.
- [ ] Refactor color selections to be based on Material class
- [ ] Create Materials for specific wood species
- [x] Associate unit with material
- [x] Associate minimum unit size with material
    - For example, plywood would be 48x96 = 4608 sq in
- [ ] Make UpperCornerCabinet class to better resemble corner cabinet geometry
- [x] Establish method for adding shelves
    - Probably make use of ComponentGrid and some of the specialized FaceFrame code for creating items in between GridCells
- [x] Make & implement a factory function for drawers
- [ ] Improve API documentation
