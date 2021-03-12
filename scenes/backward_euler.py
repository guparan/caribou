#!/usr/bin/python3

import Sofa


def createScene(root):
    root.dt = 0.01

    root.addObject('RequiredPlugin', pluginName=[
        'SofaSparseSolver', 'SofaTopologyMapping', 'SofaBoundaryCondition', 'SofaEngine', 'SofaImplicitOdeSolver'
    ])

    root.addObject('VisualStyle', displayFlags='showVisualModels showBehaviorModels showForceFields')

    root.addObject('RegularGridTopology', name='grid', min=[-7.5, -7.5, 0], max=[7.5, 7.5, 80], n=[3, 3, 9])

    meca = root.addChild("mechanical")
    meca.addObject('BackwardEulerODESolver', newton_iterations=20, rayleigh_stiffness=0.1, rayleigh_mass=0.1, printLog=True)
    meca.addObject('CaribouLDLTSolver', backend="Pardiso")
    meca.addObject('MechanicalObject', name='mo', src='@../grid')

    # Complete hexa container
    meca.addObject('HexahedronSetTopologyContainer', src='@../grid', name='mechanical_topology')

    # - Mechanics
    meca.addObject('SaintVenantKirchhoffMaterial', young_modulus=15000, poisson_ratio=0.3)
    meca.addObject('HyperelasticForcefield')

    # - Mass
    meca.addObject('HexahedronSetGeometryAlgorithms')
    meca.addObject('DiagonalMass', massDensity=0.2)

    # Fix the left side of the beam
    meca.addObject('BoxROI', name='fixed_roi', quad='@surface_topology.quad', box=[-7.5, -7.5, -0.9, 7.5, 7.5, 0.1])
    meca.addObject('FixedConstraint', indices='@fixed_roi.indices')

