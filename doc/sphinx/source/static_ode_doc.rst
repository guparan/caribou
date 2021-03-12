 .. _static_ode_doc:
 .. role:: important

<StaticODESolver />
===================

.. rst-class:: doxy-label
.. rubric:: Doxygen:
    :cpp:class:`SofaCaribou::ode::StaticODESolver`

Implementation of a Newton-Raphson static ODE solver.

The solver does a serie of Newton-Raphson iterations where at each iteration :math:`k`, the following linear system is solved:

.. math::
    \boldsymbol{K}(\boldsymbol{u}^k) \cdot \delta \boldsymbol{u}^{k+1} = \boldsymbol{R}(\boldsymbol{u}^k)

where :math:`\boldsymbol{u}^k = \boldsymbol{u}^0 + \delta \boldsymbol{u}^{k}` is the displacement vector
from the rest state at the beginning of the simulation. The stiffness matrix :math:`\boldsymbol{K}`
is the derivative of the residual with respect to the displacement, i.e.
:math:`\boldsymbol{K} = \frac{\partial \boldsymbol{R}}{\partial \boldsymbol{u}}` and is typically accumulated by
the `addKtoMatrix` method of forcefields. If an iterative linear solver is used, it is possible that the stiffness
matrix is never accumulated, instead the operation :math:`\boldsymbol{K}(\boldsymbol{u}^k) \cdot \delta \boldsymbol{u}^{k+1}`
is done through the `addDForce` method of forcefields. The residual vector :math:`\boldsymbol{R}(\boldsymbol{u}^k)`
is accumulated by the `addForce` method of forcefields.


.. list-table::
    :widths: 1 1 1 100
    :header-rows: 1
    :stub-columns: 0

    * - Attribute
      - Format
      - Default
      - Description
    * - printLog
      - bool
      - false
      - Output informative messages at the initialization and during the simulation.
    * - newton_iterations
      - int
      - 1
      - Number of newton iterations between each load increments (normally, one load increment per simulation time-step).
    * - correction_tolerance_threshold
      - float
      - 1e-5
      - Convergence criterion: The newton iterations will stop when the norm of correction \|du| reach this threshold.
    * - residual_tolerance_threshold
      - float
      - 1e-5
      - Convergence criterion: The newton iterations will stop when the relative norm of the residual
        :math:`\frac{|R_k|}{|R_0|} = \frac{|f_k - Ku_k|}{|f_0 - Ku_0|}` at iteration k is lower than this threshold.
        Use a negative value to disable this
    * - linear_solver
      - LinearSolver
      - None
      - Linear solver used for the resolution of the system. Will be automatically found in the current context node if
        none is supplied.
    * - converged
      - bool
      - N/A
      - Whether or not the last call to solve converged.

Quick example
*************
.. content-tabs::

    .. tab-container:: tab1
        :title: XML

        .. code-block:: xml

            <Node>
                <StaticODESolver newton_iterations="10" correction_tolerance_threshold="1e-8" residual_tolerance_threshold="1e-8" printLog="1" />
                <ConjugateGradientSolver maximum_number_of_iterations="2500" residual_tolerance_threshold="1e-12" preconditioning_method="Diagonal" printLog="0" />
            </Node>

    .. tab-container:: tab2
        :title: Python

        .. code-block:: python

            node.addObject('StaticODESolver', newton_iterations=10, correction_tolerance_threshold=1e-8, residual_tolerance_threshold=1e-8, printLog=True)
            node.addObject('ConjugateGradientSolver', maximum_number_of_iterations=2500, residual_tolerance_threshold=1e-12, preconditioning_method="Diagonal", printLog=False)


Available python bindings
*************************

.. py:class:: StaticODESolver

    :var iteration_times: List of times (in nanoseconds) that each Newton-Raphson iteration took to compute in the last call to Solve().
    :vartype iteration_times: list [int]

    :var squared_residuals: The list of squared residual norms (:math:`|r|^2`) of every newton iterations of the last solve call.
    :vartype squared_residuals: list [:class:`numpy.double`]

    :var squared_initial_residual: The initial squared residual (:math:`|r_0|^2`) of the last solve call.
    :vartype squared_initial_residual: :class:`numpy.double`

