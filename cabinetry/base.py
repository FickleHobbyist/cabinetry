"""Module containing infrastructure to support component trees"""
from dataclasses import dataclass, field
from abc import ABC
from math import pi
from warnings import warn
import transforms3d as tform
import pyvista as pv
import numpy as np
import copy


class TreeNode(ABC):
    """Generic tree node."""
    name: str
    parent = None
    children = None

    def __init__(self, name: str = 'root', children: list['TreeNode'] = None, *args, **kwargs):
        super(TreeNode, self).__init__(*args, **kwargs)
        self.name: str = name
        self.parent: 'TreeNode' = None
        self.children: list['TreeNode'] = []
        if children is not None:
            for child in children:
                self.add_child(child)

    def clear_children(self):
        """Remove all children"""
        self.children.clear()

    def add_child(self, node: 'TreeNode'):
        """Add a child to the parent object

        :param node: Child node
        :type node: TreeNode
        """
        assert isinstance(node, TreeNode)
        if node.parent is not None:
            warn("Child node was added but the provided node already had a parent. \
                This could be a sign of poorly configured object trees. \
                The child will be removed from prior parent.")
            node.parent.remove_child(node)
        self.children.append(node)
        node.parent = self

    def remove_child(self, node: 'TreeNode'):
        """Remove a child from the parent object

        :param node: Child node
        :type node: TreeNode
        """
        self.children.remove(node)

    def find_root_node(self) -> tuple['TreeNode', list['TreeNode']]:
        """Traverse the Tree to find the root node. Return path root node handle
        and path from root+1 to self.

        For nodes in order of ROOT -> N1 -> N2 -> N3, "node" is a handle to ROOT,
        and "route" is a list [N1, N2, N3]

        :return: node, most senior element on the object tree
        :rtype: TreeNode

        :return: route from root+1 to self
        :rtype: list[TreeNode]
        """
        node = self
        route = []
        while node.parent is not None:
            # prepend list so list is ordered [root+1 -> self]
            route.insert(0, node)
            node = node.parent
        return node, route

    def __repr__(self) -> str:
        parentName = self.parent.name if self.parent is not None else "None"
        childNames = [
            c.name for c in self.children] if self.children else ["None"]
        return f"{self.__class__.__name__}(name={self.name:s}, parent={parentName:s}, children=[{', '.join(childNames):s}])"


@dataclass
class Position:
    """Component position relative to parent frame. x=width, y=thickness, z=height"""
    x: float = 0
    y: float = 0
    z: float = 0

    def to_nparray(self) -> np.ndarray:
        """Convert to numpy ndarray

        :return: (3,) numpy ndarray object
        :rtype: np.ndarray
        """
        return np.array([self.x, self.y, self.z])


@dataclass(init=True, repr=True)
class Orientation:
    """Component orientation relative to parent frame. Default units are degrees."""
    rx: float = 0
    ry: float = 0
    rz: float = 0
    units: str = 'deg'
    _units: str = field(init=False, repr=False, default='deg')

    @property
    def units(self) -> str:
        """'deg' or 'rad'

        :return: Current units
        :rtype: str
        """
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

    def __init__(self, position=None, orientation=None, *args, **kwargs) -> 'Poseable':
        super(Poseable, self).__init__(*args, **kwargs)
        self.position = position if position is not None else Position()
        self.orientation = orientation if orientation is not None else Orientation()

    def get_frame(self) -> np.ndarray:
        """Return a 4x4 homogenous transform representing the pose in
         the parent coordinate frame

        :return: 4x4 homogenous transformation matrix
        :rtype: np.ndarray
        """
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

    def get_frame_to_base(self) -> np.ndarray:
        """Return a 4x4 homogenous transform representing the pose in
         the base coordinate frame (the most senior node in the tree)

         For a sample tree of [N0, N1, N2, N3] with homogenous transformation
         matrices [M0, M1, M2, M3], the final matrix representing the pose of
         N3 in the frame of N0 is M = M0 x M1 x M2 x M3.

         The last few slides of the following PDF provide reasonable visualization.
         https://www.cs.cmu.edu/~16311/current/schedule/ppp/Lec17-FK.pdf 

        :return: 4x4 homogenous transformation matrix
        :rtype: np.ndarray
        """
        rootNode, route = self.find_root_node()
        M = rootNode.get_frame()
        for node in route:
            Mi = node.get_frame()
            M = np.matmul(M, Mi)
        return M


_PT_LIST = []


class _PointGetter():
    """Utility class for point click callback on pv.Renderer"""

    @staticmethod
    def get_point_list():
        return _PT_LIST

    @staticmethod
    def reset_point_list():
        _PT_LIST.clear()


def _point_click_callback(point):
    """Simple callback to print point coordinates and distance between last 2 points

    The PyVista renderer does not seem to have access to module scoped variables, so
    a simple _PointGetter class is utilized to retrieve a handle to a module scope list.
    """
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
    """Superclass providing default functionality for rendering all items on a TreeNode object tree"""
    color: pv.color_like

    def __init__(self, color: pv.color_like = 'white', *args, **kwargs) -> 'RenderTree':
        super().__init__(*args, **kwargs)
        self.color = color

    def add_child(self, node: 'RenderTree') -> None:
        assert isinstance(node, RenderTree)
        super().add_child(node)

    def render(self, show_edges: bool = True, opacity=1) -> None:
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
                    p.add_mesh(
                        mesh,
                        color=node.color,
                        show_edges=show_edges,
                        opacity=opacity,
                    )
                Q.extend(node.children)
                visited.append(node)

        p.enable_point_picking(
            callback=_point_click_callback, left_clicking=False, pickable_window=False)
        p.show()

    def get_pv_mesh(self):
        """Return pyvista mesh object or None.

        Subclasses should override this method to return appropriate geometry
        for rendering. Return value will be supplied as the first argument to
        pyvista.Plotter.add_mesh()
        """
        return None
