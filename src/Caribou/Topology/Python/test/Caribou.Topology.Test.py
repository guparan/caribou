#! python3

import sys
import unittest
import numpy as np

sys.path.insert(0, "@CARIBOU_PYTHON_LIB_PATH@")

import Caribou
from Caribou.Topology import Mesh
from Caribou.Topology import Grid3D
from Caribou.Geometry import Segment
from Caribou.Geometry import Quad
from Caribou.Geometry import Triangle
from Caribou.Geometry import Tetrahedron
from Caribou.Geometry import Hexahedron


class TestMesh(unittest.TestCase):

    def assertMatrixEqual(self, A, B):
        return self.assertTrue((A == B).all(), f"Matrices are not equal, with \nA={A} \nand\nB={B}")

    def test_constructor_1d(self):
        mesh = Mesh(Caribou._1D)
        mesh.add_node(1)
        mesh.add_nodes([2, 3, 4, 5])
        self.assertMatrixEqual([1., 2., 3., 4., 5.], mesh.positions([0, 1, 2, 3, 4]))

    def test_contructor_3d(self):
        mesh = Mesh(Caribou._3D)


class TestGrid(unittest.TestCase):
    def assertMatrixEqual(self, A, B):
        return self.assertTrue((np.asarray(A) == np.asarray(B)).all(), f"Matrices are not equal, with \nA={A} \nand\nB={B}")

    def assertMatrixAlmostEqual(self, A, B, rtol=1.e-5, atol=1.e-8, equal_nan=False):
        return self.assertTrue(np.allclose(np.asarray(A), np.asarray(B), rtol, atol, equal_nan), f"Matrices are not almost equal, with \nA={A} \nand\nB={B}")

    def test_grid(self):
        # Grid creation
        g = Grid3D(
            [0.25, 0.5, 0.75], # Anchor point (first node at the corner of the grid)
            [2, 2, 2], # Subdivisions (number of cells in the x, y and z directions respectively)
            [100, 100, 100]) # Dimensions (size of the grid in the x, y and z directions respectively)

        # General properties
        self.assertEqual(g.number_of_nodes(), 27)

        # Cell numbering test
        self.assertEqual(g.cell_index_at([1, 0, 1]), 5)
        self.assertMatrixEqual(g.cell_coordinates_at(5), [1, 0, 1])

        # Cell positioning
        self.assertFalse(g.contains([ 0.24,    0.50,   0.75]))
        self.assertFalse(g.contains([ 0.25,    0.49,   0.75]))
        self.assertFalse(g.contains([ 0.25,    0.50,   0.74]))
        self.assertTrue(g.contains([ 0.25,    0.50,   0.75]))
        self.assertTrue(g.contains([ 50.00,  50.00,  50.00]))
        self.assertTrue(g.contains([100.25, 100.50, 100.75]))
        self.assertFalse(g.contains([100.26, 100.50, 100.75]))
        self.assertFalse(g.contains([100.25, 100.51, 100.75]))

        # Cells around nodes
        self.assertTrue(0 == len(g.cells_around([-50, -50, -50])))
        self.assertMatrixEqual(g.cells_around([0.25, 0.50, 0.75]), [0])
        self.assertMatrixEqual(g.cells_around([50.25, 0.50, 0.75]), [0,1])
        self.assertMatrixEqual(g.cells_around([100.25, 0.50, 0.75]), [1])
        self.assertMatrixEqual(g.cells_around([50.25, 50.50, 50.75]), [0, 4, 2, 6, 1, 5, 3, 7])

        # Cells around faces
        self.assertMatrixEqual(g.cells_around([0.25, 25.50, 25.75]), [0])
        self.assertMatrixEqual(g.cells_around([25.25, 25.50, 0.75]), [0])
        self.assertMatrixEqual(g.cells_around([25.25, 0.50, 25.75]), [0])
        self.assertMatrixEqual(g.cells_around([50.25, 25.50, 25.75]), [0, 1])
        self.assertMatrixEqual(g.cells_around([25.25, 50.50, 25.75]), [0, 2])
        self.assertMatrixEqual(g.cells_around([25.25, 25.50, 50.75]), [0, 4])
        self.assertMatrixEqual(g.cells_around([75.25, 100.50, 75.75]), [7])
        self.assertMatrixEqual(g.cells_around([75.25, 75.50, 100.75]), [7])
        self.assertMatrixEqual(g.cells_around([100.25, 75.50, 75.75]), [7])

        # Node position queries
        self.assertMatrixAlmostEqual(g.node(0), [  0.25,   0.5, 0.75])
        self.assertMatrixAlmostEqual(g.node(2), [100.25,   0.5, 0.75])
        self.assertMatrixAlmostEqual(g.node(6), [  0.25, 100.5, 0.75])
        self.assertMatrixAlmostEqual(g.node(8), [100.25, 100.5, 0.75])

        self.assertMatrixAlmostEqual(g.node(18), [  0.25,   0.5, 100.75])
        self.assertMatrixAlmostEqual(g.node(20), [100.25,   0.5, 100.75])
        self.assertMatrixAlmostEqual(g.node(24), [  0.25, 100.5, 100.75])
        self.assertMatrixAlmostEqual(g.node(26), [100.25, 100.5, 100.75])

        # Node indexing
        for i in range(g.number_of_nodes()):
            self.assertEqual(i, g.node_index_at(g.node_coordinates_at(i)))

        # Edge queries
        # First slice (2D grid) 
        self.assertEqual(g.number_of_edges(), 3*12 + 2*9)
        self.assertMatrixEqual(g.edge(0), [0, 1])
        self.assertMatrixEqual(g.edge(0), [0, 1])
        self.assertMatrixEqual(g.edge(1), [1, 2])
        self.assertMatrixEqual(g.edge(2), [0, 3])
        self.assertMatrixEqual(g.edge(3), [1, 4])
        self.assertMatrixEqual(g.edge(4), [2, 5])
        self.assertMatrixEqual(g.edge(5), [3, 4])
        self.assertMatrixEqual(g.edge(6), [4, 5])
        self.assertMatrixEqual(g.edge(7), [3, 6])
        self.assertMatrixEqual(g.edge(8), [4, 7])
        self.assertMatrixEqual(g.edge(9), [5, 8])
        self.assertMatrixEqual(g.edge(10), [6, 7])
        self.assertMatrixEqual(g.edge(11), [7, 8])

        # Between the slice 1 and slice 2
        self.assertMatrixEqual(g.edge(12), [0, 9])
        self.assertMatrixEqual(g.edge(13), [1, 10])
        self.assertMatrixEqual(g.edge(14), [2, 11])
        self.assertMatrixEqual(g.edge(15), [3, 12])
        self.assertMatrixEqual(g.edge(16), [4, 13])
        self.assertMatrixEqual(g.edge(17), [5, 14])
        self.assertMatrixEqual(g.edge(18), [6, 15])
        self.assertMatrixEqual(g.edge(19), [7, 16])
        self.assertMatrixEqual(g.edge(20), [8, 17])

        # Face queries
        self.assertEqual(g.number_of_faces(), 36)
        # First slice (2D grid)
        self.assertMatrixEqual(g.face(0), [0, 1, 4, 3])
        self.assertMatrixEqual(g.face(1), [1, 2, 5, 4])
        self.assertMatrixEqual(g.face(2), [3, 4, 7, 6])
        self.assertMatrixEqual(g.face(3), [4, 5, 8, 7])
        # Between the slice 1 and slice 2
        # - xz axis
        self.assertMatrixEqual(g.face(4), [0, 1, 10,  9])
        self.assertMatrixEqual(g.face(5), [1, 2, 11, 10])
        self.assertMatrixEqual(g.face(6), [3, 4, 13, 12])
        self.assertMatrixEqual(g.face(7), [4, 5, 14, 13])
        self.assertMatrixEqual(g.face(8), [6, 7, 16, 15])
        self.assertMatrixEqual(g.face(9), [7, 8, 17, 16])
        # - yz axis
        self.assertMatrixEqual(g.face(10), [0, 3, 12,  9])
        self.assertMatrixEqual(g.face(11), [1, 4, 13, 10])
        self.assertMatrixEqual(g.face(12), [2, 5, 14, 11])
        self.assertMatrixEqual(g.face(13), [3, 6, 15, 12])
        self.assertMatrixEqual(g.face(14), [4, 7, 16, 13])
        self.assertMatrixEqual(g.face(15), [5, 8, 17, 14])

        # Cell Node indices
        for i in range(g.number_of_cells()):
            node_indices = g.node_indices_of(i)
            nodes = np.array([
                g.node(node_indices[0]), g.node(node_indices[1]), g.node(node_indices[2]), g.node(node_indices[3]),
                g.node(node_indices[4]), g.node(node_indices[5]), g.node(node_indices[6]), g.node(node_indices[7])
            ])
            self.assertMatrixAlmostEqual(nodes, g.cell_at(i).nodes())

        # Cell queries by position
        for i in range(g.number_of_cells()):
            cell = g.cell_at(i)
            for gauss_node in cell.gauss_nodes():
                p = cell.world_coordinates(gauss_node.position)
                self.assertEqual(g.cell_index_containing(p, False), i)


if __name__ == '__main__':
    unittest.main()
