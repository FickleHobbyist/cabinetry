# Cabinetry
This repository contains geometric representations of household cabinetry, which can be utilized to estimate material quantities. It was created as an exercise in learning python in support of estimating material cost for an upcoming kitchen renovation. It is absolutely not a representation of the most efficient means of generating parametric cabinet geometry. Nevertheless, we press on...

# To-Do
- [x] Create DrawerFace component.
- [x] Create DrawerBox component.
- [x] Create Door component (probably reuse DrawerFace, consider abstracting).
- [x] Establish method for connecting DrawerBox, DrawerFace, Door to GridCells in each FaceFrame.
- [x] Create config class for common.
- [x] Create upper cabinet box.
- [ ] Fine tune material selection for drawer boxes based on drawer size. Larger drawers need thicker material for the box.
- [ ] Establish method for generating a bill of materials
    - For rough estimating, compute total area and volume in each material category.
    - Use fudge factor on total ply area / (48x96) for number of sheets required.
    - Use total volume to estimate board feet of hardwood type materials required plus fudge factor for waste.
- [x] Adjust drawer box components to account for length increment due to rabbets & dadoes.
- [ ] Refactor color selections to be based on Material class
- [ ] Create Materials for specific wood species
- [ ] Associate unit with material
- [ ] Associate minimum unit size with material
    - For example, plywood would be 48x96 = 4608 sq in
- [ ] Establish method for adding shelves
    - Probably make use of ComponentGrid and some of the specialized FaceFrame code for creating items in between GridCells
- [ ] Make & implement a factory function for drawers
- [ ] Improve API documentation
