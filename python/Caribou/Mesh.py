from .Utils import Struct as S
from .Utils import bbox, translate, rotate

from .Base import BaseObject

import os
import math
import pygmsh
import meshio
import numpy as np
from numpy import linalg as LA
from numpy import pi as PI


class Part(BaseObject):
    __count = 0

    def __init__(self, **kwargs):
        BaseObject.__init__(self, **kwargs)
        Part.__count += 1

        # Parameters
        self.mesh = kwargs.get('mesh', None)
        self.name = kwargs.get('name', 'unnamed_part_{}'.format(Part.__count))
        assert isinstance(self.mesh, Mesh)
        self.points = kwargs.get('points', np.array([], dtype=int))
        self.edges = kwargs.get('edges', np.array([]))
        self.triangles = kwargs.get('triangles', np.array([]))
        self.quads = kwargs.get('quads', np.array([]))
        self.tetrahedrons = kwargs.get('tetrahedrons', np.array([]))
        self.hexahedrons = kwargs.get('hexahedrons', np.array([]))

    def __eq__(self, other):
        """
        Compare the part with another one
        :param other: The other part
        :type other: Part
        :return: True if their parameters are equal, false otherwise
        ":rtype: bool
        """
        ret = BaseObject.__eq__(self, other)
        ret = ret and np.array_equal(self.points, other.points)
        ret = ret and np.array_equal(self.edges, other.edges)
        ret = ret and np.array_equal(self.triangles, other.triangles)
        ret = ret and np.array_equal(self.quads, other.quads)
        ret = ret and np.array_equal(self.tetrahedrons, other.tetrahedrons)
        ret = ret and np.array_equal(self.hexahedrons, other.hexahedrons)
        return ret


class SurfacePart(Part):
    def __init__(self, **kwargs):
        Part.__init__(self, **kwargs)

        # Parameters
        self.points = kwargs.get('points', np.array([]))
        self.edges = kwargs.get('edges', np.array([]))
        self.triangles = kwargs.get('triangles', np.array([]))
        self.quads = kwargs.get('quads', np.array([]))


class VolumePart(SurfacePart):
    def __init__(self, **kwargs):
        SurfacePart.__init__(self, **kwargs)

        # Parameters
        self.tetrahedrons = kwargs.get('tetrahedrons', np.array([]))
        self.hexahedrons = kwargs.get('hexahedrons', np.array([]))


class Mesh(BaseObject):
    __count = 0

    def __init__(self, **kwargs):
        BaseObject.__init__(self, **kwargs)
        Mesh.__count += 1
        # Parameters
        self._params = kwargs.copy()
        self.name = kwargs.get('name', 'unnamed_mesh_{}'.format(Mesh.__count))
        self.filepath = kwargs.get('filepath', None)

        if self.filepath is not None and os.path.isfile(self.filepath):
            fp = self.filepath
            self.filepath = None  # To avoid infinite recursion
            fromGmshFile(fp, self)
            self.vertices = kwargs.get('vertices', self.vertices)
            self.filepath = fp
        else:
            self.vertices = kwargs.get('vertices', np.array([]))
            self.gmsh = kwargs.get(
                'gmsh',
                {'points': None, 'cells': None, 'point_data': None, 'cell_data': None, 'field_data': None}
            )

            self.bbox = S({
                'min': [0, 0, 0],
                'max': [0, 0, 0]
            })

            self.__parts = []

        parts = kwargs.get('parts', [])
        for p in parts:
            self.add_part(p)

        if len(self.vertices):
            xmin, xmax, ymin, ymax, zmin, zmax = bbox(self.vertices)
            self.bbox = S({
                'min': [xmin, ymin, zmin],
                'max': [xmax, ymax, zmax]
            })

    def __eq__(self, other):
        """
        Compare the mesh with another one
        :param other: The other mesh
        :type other: Mesh
        :return: True if their parameters are equal, false otherwise
        ":rtype: bool
        """
        res = BaseObject.__eq__(self, other)
        res = res and (\
            (self.filepath and self.filepath == other.filepath) or \
              (np.array_equal(self.vertices, other.vertices) and self.parts == other.parts))

        return res

    def serialize(self):
        if self.filepath is not None:
            return {
                'name': self.name,
                'filepath': self.filepath
            }
        else:
            return BaseObject.serialize(self)

    @classmethod
    def deserialize(cls, **kwargs):
        filepath = kwargs.get('filepath')
        if filepath is not None:
            return cls(**kwargs)

        gmsh = kwargs.get('gmsh')
        if gmsh is not None:
            return fromGmsh(**gmsh)

        return cls()

    @property
    def parts(self):
        return self.__parts

    def add_part(self, part):
        """
        Add a part to the mesh. The part will be accessible with a dynamic attribute `mesh.part_name`.
        :param Part part: The part to add
        """
        assert isinstance(part, Part)

        names = [p.name for p in self.__parts]
        assert (part.name not in names)

        try:
            getattr(self, part.name)
        except AttributeError:
            setattr(self, part.name, part)

        self.__parts.append(part)

    def get_part(self, name):
        """
        Get the mesh part from the name
        :param str name: The name of the part
        :return: The part, or None if it doesn't exists
        :rtype: Part
        """
        for p in self.__parts:
            if p.name == name:
                return p
        return None

    def save(self, filepath):
        toVtkFile(filename=filepath, mesh=self)
        self.filepath = os.path.realpath(filepath)


def fromGmsh(points, cells, point_data, cell_data, field_data, mesh=None):
    parts = []

    if mesh is None:
        mesh = Mesh(
            vertices=points,
            gmsh={'points': points, 'cells': cells, 'point_data': point_data, 'cell_data': cell_data, 'field_data': field_data}
        )
    else:
        mesh.vertices = points
        mesh.gmsh = {'points': points, 'cells': cells, 'point_data': point_data, 'cell_data': cell_data, 'field_data': field_data}

    for field_name in field_data:
        id = field_data[field_name][0]

        points = np.array([])
        edges = np.array([])
        triangles = np.array([])
        quads = np.array([])
        tetrahedrons = np.array([])
        hexahedrons = np.array([])

        if 'vertex' in cell_data:
            mask = np.array(np.ma.masked_not_equal(cell_data['vertex']['gmsh:physical'], id).mask)
            points = cells['vertex'][~mask]

        if 'line' in cell_data:
            mask = np.array(np.ma.masked_not_equal(cell_data['line']['gmsh:physical'], id).mask)
            edges = cells['line'][~mask]

        if 'triangle' in cell_data:
            mask = np.array(np.ma.masked_not_equal(cell_data['triangle']['gmsh:physical'], id).mask)
            triangles = cells['triangle'][~mask]

        if 'quad' in cell_data:
            mask = np.array(np.ma.masked_not_equal(cell_data['quad']['gmsh:physical'], id).mask)
            quads = cells['quad'][~mask]

        if 'tetra' in cell_data:
            mask = np.array(np.ma.masked_not_equal(cell_data['tetra']['gmsh:physical'], id).mask)
            tetrahedrons = cells['tetra'][~mask]
            if len(tetrahedrons.shape) > 2:
                tetrahedrons = tetrahedrons[0]

        if 'hexahedron' in cell_data:
            mask = np.array(np.ma.masked_not_equal(cell_data['hexahedron']['gmsh:physical'], id).mask)
            hexahedrons = cells['hexahedron'][~mask]
            if len(hexahedrons.shape) > 2:
                hexahedrons = hexahedrons[0]

        if not points.size:
            points = np.unique(
                np.concatenate((
                    np.unique(edges),
                    np.unique(triangles),
                    np.unique(quads),
                    np.unique(tetrahedrons),
                    np.unique(hexahedrons),
                ))
            ).astype(int)

        if tetrahedrons.size > 0 or hexahedrons.size > 0:
            part = VolumePart(name=field_name, mesh=mesh)
            part.tetrahedrons = tetrahedrons
            part.hexahedrons = hexahedrons
        else:
            part = SurfacePart(name=field_name, mesh=mesh)

        part.points = points
        part.edges = edges
        part.triangles = triangles
        part.quads = quads

        mesh.add_part(part)

    return mesh


def fromGmshFile(filename, mesh=None):
    points, cells, point_data, cell_data, field_data = meshio.read(str(filename))
    return fromGmsh(points=points, cells=cells, point_data=point_data, cell_data=cell_data, field_data=field_data, mesh=mesh)


def fromStlFile(filename):
    points, cells, point_data, cell_data, field_data = meshio.read(str(filename))
    return fromGmsh(points, cells, point_data, cell_data, field_data)


def toVtkFile(filename, mesh):
    meshio.write(
        filename,
        mesh.vertices,
        mesh.gmsh['cells'],
        point_data=mesh.gmsh['point_data'],
        cell_data=mesh.gmsh['cell_data'],
        field_data=mesh.gmsh['field_data'],
        file_format='vtk-ascii',
    )


def cylinder(center1, center2, radius, size=10, dimension=2, quads=False):
    geo = pygmsh.built_in.Geometry()
    c1 = np.asarray(center1)
    c2 = np.asarray(center2)

    r = radius
    axis = (c2 - c1)
    l = LA.norm(axis)

    # SURFACE
    n = size
    lcar = 2 * PI * r / n
    points = [[r * math.cos(t), r * math.sin(t), 0] for t in [2 * np.pi / n * a for a in range(n)]]
    polygon = geo.add_polygon(
        points,
        lcar=lcar
    )
    top, extruded, lat = geo.extrude(
        polygon.surface,
        translation_axis=[0, 0, l],
        point_on_axis=[0, 0, 0],
        recombine=quads)

    geo._GMSH_CODE.append("Reverse Surface {" + polygon.surface.id + "};")

    geo.add_physical_surface(polygon.surface, 'base')
    geo.add_physical_surface(top, 'top')
    geo.add_physical_surface(lat, 'side')
    geo.add_physical_surface([polygon.surface, top] + lat, 'surface')

    if dimension == 3:
        geo.add_physical_volume(extruded, 'volume')

    points, cells, point_data, cell_data, field_data = pygmsh.generate_mesh(geo, dim=dimension, verbose=False)

    points = rotate(points, [0, 0, l], axis / l)
    points = translate(points, c1)

    return fromGmsh(points, cells, point_data, cell_data, field_data)


def grid(corner, length, width, height, nx, ny, nz):
    print "todo"