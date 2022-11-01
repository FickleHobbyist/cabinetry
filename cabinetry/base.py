"""Module containing infrastructure to support component trees"""
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from math import pi
import transforms3d as tform
import pyvista as pv
import numpy as np
import copy


pv.global_theme.axes.show = True


class TreeNode(ABC):
    name: str
    parent = None
    children = None

    "Generic tree node."

    def __init__(self, name='root', children=None, *args, **kwargs):
        super(TreeNode, self).__init__(*args, **kwargs)
        self.name = name
        self.parent = None
        self.children = []
        if children is not None:
            for child in children:
                self.add_child(child)

    def add_child(self, node):
        assert isinstance(node, TreeNode)
        self.children.append(node)
        node.parent = self

    def find_root_node(self) -> tuple['TreeNode', list['TreeNode']]:
        """Traverse the Tree to find the root node. Return path root node handle and path from root to self."""
        node = self
        route = []
        while node.parent is not None:
            route.insert(0, node)  # prepend list so we end at root node
            node = node.parent
        return node, route

    def __repr__(self) -> str:
        parentName = self.parent.name if self.parent is not None else "None"
        childNames = [
            c.name for c in self.children] if self.children else ["None"]
        return f"{self.__class__.__name__}(name={self.name:s}, parent={parentName:s}, children=[{', '.join(childNames):s}])"


@dataclass
class Position:
    x: float = 0
    y: float = 0
    z: float = 0

    def to_nparray(self):
        return np.array([self.x, self.y, self.z])


@dataclass(init=True, repr=True)
class Orientation:
    rx: float = 0
    ry: float = 0
    rz: float = 0
    units: str = 'deg'
    _units: str = field(init=False, repr=False, default='deg')

    @property
    def units(self) -> str:
        return self._units

    @units.setter
    def units(self, value):
        valid_units = ['rad', 'deg']
        if type(value) is property:
            value = Orientation._units
        if value in valid_units:
            self._units = value
        else:
            raise ValueError(
                f"Unsupported unit {value}. Units must be one of: {valid_units}")

    def to_nparray(self, order='xyz'):
        return np.array(list(getattr(self, f"r{ax}") for ax in order))

    def to_tuple(self, order='xyz'):
        return tuple(getattr(self, f"r{ax}") for ax in order)

    def in_radians(self):
        if self.units == 'deg':
            return Orientation(*tuple(self.to_nparray() * pi/180))
        else:
            return copy.deepcopy(self)

    def in_degrees(self):
        if self.units == 'rad':
            return Orientation(*tuple(self.to_nparray() * 180/pi))
        else:
            return copy.deepcopy(self)


class Poseable(TreeNode, ABC):
    """Defines an object that has both position and orientation.

    Provides methods for obtaining 4x4 homogenous transformation matrices (frames)
    which locate the object relative to its parent and some base frame.
    """

    def __init__(self, position=None, orientation=None, *args, **kwargs):
        super(Poseable, self).__init__(*args, **kwargs)
        self.position = position if position is not None else Position()
        self.orientation = orientation if orientation is not None else Orientation()

    def get_frame(self):
        # no zoom or shear
        Z = np.ones(3)
        S = np.zeros(3)
        # translate in parent frame
        T = self.position.to_nparray()
        # intrinsic rotation
        R = tform.euler.euler2mat(
            *self.orientation.in_radians().to_tuple(order='zyx'),
            axes='rzyx')
        # Construct 4x4 homogenous transformation
        return tform.affines.compose(T, R, Z, S)

    def get_frame_to_base(self):
        """Return a 4x4 homogenous transform representing the pose in
         the base coordinate frame (the most senior node in the tree)"""
        rootNode, route = self.find_root_node()
        M = rootNode.get_frame()
        for node in route:
            Mi = node.get_frame()
            M = np.matmul(M, Mi)
        return M


_PT_LIST = []


class _PointGetter():

    @staticmethod
    def get_point_list():
        return _PT_LIST

    @staticmethod
    def reset_point_list():
        _PT_LIST.clear()


def _point_click_callback(point):
    PT_LIST = _PointGetter.get_point_list()
    distMsg = ''
    PT_LIST.append(point)
    print(f"len pt list = {len(PT_LIST)}")
    if len(PT_LIST) == 2:
        dist = np.linalg.norm(PT_LIST[1] - PT_LIST[0])
        distMsg = f", dist to prev pt = {dist}"
        _PointGetter.reset_point_list()
    print(f"picked point: {point}{distMsg}")


class RenderTree(TreeNode):
    color: pv.color_like

    def __init__(self, color: pv.color_like, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.color = color

    def add_child(self, node: 'RenderTree') -> None:
        assert isinstance(node, RenderTree)
        super().add_child(node)

    def render(self, show_edges: bool = True) -> None:
        """Render all items in the RenderTree at or below the level
        of the node on which render() is called.
        """
        p = pv.Plotter()
        p.add_axes()
        p.add_axes_at_origin(x_color='red', y_color='green', z_color='blue',
                             labels_off=True)

        # Render via Breadth-First Search of TreeNode Children
        Q = self.children
        Q.insert(0, self)  # Ensure self is rendered 1st
        visited = []  # list to mark nodes as visited
        while Q:  # not empty
            node: RenderTree = Q.pop()
            if node not in visited:
                mesh = node.get_pv_mesh()
                if mesh is not None:
                    p.add_mesh(mesh, color=node.color, show_edges=show_edges)
                Q.extend(node.children)
                visited.append(node)

        p.enable_point_picking(
            callback=_point_click_callback, left_clicking=True, pickable_window=False)
        p.show()

    def get_pv_mesh(self):
        """Return pyvista mesh object or None.

        Subclasses should override this method to return appropriate geometry
        for rendering. Return value will be supplied as the first argument to
        pyvista.Plotter.add_mesh()
        """
        return None
