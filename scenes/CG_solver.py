#!/usr/bin/python3

import Sofa

cg_iterations = 200
newton_iterations = 20
increments=100
poissonRatio = 0
youngModulus = 3000


def createScene(root):
    root.addObject('APIVersion', level='17.06')

    root.addObject('RequiredPlugin', name='SofaComponentAll')
    root.addObject('RequiredPlugin', name='SofaOpenglVisual')
    root.addObject('RequiredPlugin', name='SofaSparseSolver')

    root.addObject('VisualStyle', displayFlags='showVisualModels showBehaviorModels showCollisionModels hideMappings showForceFields')

    root.addObject('RegularGridTopology', name='mesh', min=[-7.5, -7.5, 0], max=[7.5, 7.5, 80], n=[9, 9, 21])

    i = 0
    tx = 20*i
    meca = root.addChild("caribou_cg_solver_no_precond_no_assembly")
    meca.addObject('LegacyStaticODESolver', newton_iterations=newton_iterations, correction_tolerance_threshold=1e-8, residual_tolerance_threshold=1e-8, printLog=True)
    meca.addObject('ConjugateGradientSolver', preconditioning_method="None", maximum_number_of_iterations=cg_iterations, residual_tolerance_threshold=1e-8)
    meca.addObject('MechanicalObject', src='@../mesh', translation=[tx, 0, 0])
    meca.addObject('HexahedronSetTopologyContainer', name='topo', src='@../mesh')
    meca.addObject('SaintVenantKirchhoffMaterial', young_modulus=youngModulus, poisson_ratio=poissonRatio)
    # meca.addObject('NeoHookeanMaterial', young_modulus=youngModulus, poisson_ratio=poissonRatio)
    meca.addObject('HyperelasticForcefield', template="Hexahedron", printLog=True)

    meca.addObject('BoxROI', name='fixed_roi', box=[-7.5+tx, -7.5, -0.9, 7.5+tx, 7.5, 0.1])
    meca.addObject('FixedConstraint', indices='@fixed_roi.indices')

    meca.addObject('BoxROI', name='top_roi', box=[-7.5+tx, -7.5, 79.9, 7.5+tx, 7.5, 80.1])
    meca.addObject('QuadSetTopologyContainer', name='quad_container', quads='@top_roi.quadInROI')
    meca.addObject('TractionForce', traction=[0, -30, 0], slope=1/increments, quads='@quad_container.quads', printLog=True)

    i+=1
    tx = 20*i
    meca = root.addChild("caribou_cg_solver_no_precond")
    meca.addObject('LegacyStaticODESolver', newton_iterations=newton_iterations, correction_tolerance_threshold=1e-8, residual_tolerance_threshold=1e-8, printLog=True)
    meca.addObject('ConjugateGradientSolver', preconditioning_method="None", maximum_number_of_iterations=cg_iterations, residual_tolerance_threshold=1e-8)
    meca.addObject('MechanicalObject', src='@../mesh', translation=[tx, 0, 0])
    meca.addObject('HexahedronSetTopologyContainer', name='topo', src='@../mesh')
    meca.addObject('SaintVenantKirchhoffMaterial', young_modulus=youngModulus, poisson_ratio=poissonRatio)
    # meca.addObject('NeoHookeanMaterial', young_modulus=youngModulus, poisson_ratio=poissonRatio)
    meca.addObject('HyperelasticForcefield', template="Hexahedron", printLog=True)

    meca.addObject('BoxROI', name='fixed_roi', box=[-7.5+tx, -7.5, -0.9, 7.5+tx, 7.5, 0.1])
    meca.addObject('FixedConstraint', indices='@fixed_roi.indices')

    meca.addObject('BoxROI', name='top_roi', box=[-7.5+tx, -7.5, 79.9, 7.5+tx, 7.5, 80.1])
    meca.addObject('QuadSetTopologyContainer', name='quad_container', quads='@top_roi.quadInROI')
    meca.addObject('TractionForce', traction=[0, -30, 0], slope=1/increments, quads='@quad_container.quads', printLog=True)

    i+=1
    tx = 20*i
    meca = root.addChild("sofa_cg_solver")
    meca.addObject('LegacyStaticODESolver', newton_iterations=newton_iterations, correction_tolerance_threshold=1e-8, residual_tolerance_threshold=1e-8, printLog=True)
    meca.addObject('CGLinearSolver', tolerance=1e-8, threshold=1e-25, iterations=cg_iterations)
    meca.addObject('MechanicalObject', src='@../mesh', translation=[tx, 0, 0])
    meca.addObject('HexahedronSetTopologyContainer', name='topo', src='@../mesh')
    meca.addObject('SaintVenantKirchhoffMaterial', young_modulus=youngModulus, poisson_ratio=poissonRatio)
    # meca.addObject('NeoHookeanMaterial', young_modulus=youngModulus, poisson_ratio=poissonRatio)
    meca.addObject('HyperelasticForcefield', template="Hexahedron", printLog=True)

    meca.addObject('BoxROI', name='fixed_roi', box=[-7.5+tx, -7.5, -0.9, 7.5+tx, 7.5, 0.1])
    meca.addObject('FixedConstraint', indices='@fixed_roi.indices')

    meca.addObject('BoxROI', name='top_roi', box=[-7.5+tx, -7.5, 79.9, 7.5+tx, 7.5, 80.1])
    meca.addObject('QuadSetTopologyContainer', name='quad_container', quads='@top_roi.quadInROI')
    meca.addObject('TractionForce', traction=[0, -30, 0], slope=1/increments, quads='@quad_container.quads', printLog=True)