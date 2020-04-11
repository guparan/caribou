#pragma once

#include <functional>
#include <array>

#include <Eigen/Sparse>
#include <Eigen/Dense>

#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/topology/BaseMeshTopology.h>

#include <Caribou/config.h>
#include <Caribou/Constants.h>
#include <Caribou/Geometry/Element.h>

#include <SofaCaribou/Material/HyperelasticMaterial.h>

namespace SofaCaribou::forcefield {

using namespace sofa::core;
using namespace sofa::core::objectmodel;
using namespace sofa::core::behavior;

// Traits to get the Sofa vector type from the dimension
template <std::size_t Dim> struct SofaVecType {};
template <> struct SofaVecType<1> { using Type = sofa::defaulttype::Vec1Types; };
template <> struct SofaVecType<2> { using Type = sofa::defaulttype::Vec2Types; };
template <> struct SofaVecType<3> { using Type = sofa::defaulttype::Vec3Types; };

template <typename GaussNode, INTEGER_TYPE NumberOfGaussNodesAtCompileTime>
struct GaussContainer {
    using Type = std::array<GaussNode, static_cast<std::size_t>(NumberOfGaussNodesAtCompileTime)>;
};

template <typename GaussNode>
struct GaussContainer<GaussNode, caribou::Dynamic> {
    using Type = std::vector<GaussNode>;
};

template <typename Element>
class HyperelasticForcefield : public ForceField<typename SofaVecType<caribou::geometry::traits<Element>::Dimension>::Type> {
public:
    SOFA_CLASS(SOFA_TEMPLATE(HyperelasticForcefield, Element), SOFA_TEMPLATE(ForceField, typename SofaVecType<caribou::geometry::traits<Element>::Dimension>::Type));

    // Type definitions
    using DataTypes = typename SofaVecType<caribou::geometry::traits<Element>::Dimension>::Type;
    using Inherit  = ForceField<DataTypes>;
    using VecCoord = typename DataTypes::VecCoord;
    using VecDeriv = typename DataTypes::VecDeriv;
    using Coord    = typename DataTypes::Coord;
    using Deriv    = typename DataTypes::Deriv;
    using Real     = typename Coord::value_type;
    using Index    = sofa::core::topology::BaseMeshTopology::index_type;

    using LocalCoordinates = typename caribou::geometry::Element<Element>::LocalCoordinates;
    using WorldCoordinates = typename caribou::geometry::Element<Element>::WorldCoordinates;

    static constexpr INTEGER_TYPE Dimension = caribou::geometry::traits<Element>::Dimension;
    static constexpr INTEGER_TYPE NumberOfNodes = caribou::geometry::traits<Element>::NumberOfNodesAtCompileTime;
    static constexpr INTEGER_TYPE NumberOfGaussNodes = caribou::geometry::traits<Element>::NumberOfGaussNodesAtCompileTime;

    template<int nRows, int nColumns>
    using Matrix = typename caribou::geometry::Element<Element>::template Matrix<nRows, nColumns>;

    template<int nRows, int nColumns, int Options=0>
    using MatrixI = typename caribou::geometry::Element<Element>::template MatrixI<nRows, nColumns>;

    template<int nRows, int nColumns>
    using Map = Eigen::Map<const Matrix<nRows, nColumns>>;

    template<int nRows>
    using Vector = typename caribou::geometry::Element<Element>::template Vector<nRows>;

    template<int nRows>
    using MapVector = Eigen::Map<const Vector<nRows>>;

    using Mat33   = Matrix<3, 3>;
    using Vec3   = Vector<3>;

    template <typename ObjectType>
    using Link = SingleLink<HyperelasticForcefield<Element>, ObjectType, BaseLink::FLAG_STRONGLINK>;

    // Data structures
    struct GaussNode {
        Real weight;
        Real jacobian_determinant;
        Matrix<NumberOfNodes, Dimension> dN_dx;
        Mat33 F = Mat33::Identity(); // Deformation gradient
    };

    // Container of Gauss integration nodes for one Element
    using GaussContainer = typename GaussContainer<GaussNode, NumberOfGaussNodes>::Type;

    // Public methods

    HyperelasticForcefield();

    [[nodiscard]] auto
    getTemplateName() const -> std::string override {
        return templateName(this);
    }

    static auto templateName(const HyperelasticForcefield<Element>* = nullptr) -> std::string {
        return "Unknown";
    }
    static auto canCreate(HyperelasticForcefield<Element>* o, BaseContext* context, BaseObjectDescription* arg) -> bool;

    void init() override;

    void addForce(
        const MechanicalParams* mparams,
        Data<VecDeriv>& d_f,
        const Data<VecCoord>& d_x,
        const Data<VecDeriv>& d_v) override;

    void addDForce(
        const MechanicalParams* /*mparams*/,
        Data<VecDeriv>& /*d_df*/,
        const Data<VecDeriv>& /*d_dx*/) override;

    SReal getPotentialEnergy(
        const MechanicalParams* /* mparams */,
        const Data<VecCoord>& /* d_x */) const override;

    void addKToMatrix(sofa::defaulttype::BaseMatrix * /*matrix*/, SReal /*kFact*/, unsigned int & /*offset*/) override;

    void computeBBox(const sofa::core::ExecParams* params, bool onlyVisible) override;

    void draw(const sofa::core::visual::VisualParams* vparams) override;

    /** Get the number of elements contained in this field **/
    [[nodiscard]] inline
    virtual auto number_of_elements() const -> std::size_t {
        return 0;
    }

    /** Get the set of Gauss integration nodes of an element */
    auto gauss_nodes_of(std::size_t element_id) const -> const auto & {
        return p_elements_quadrature_nodes[element_id];
    }

    /** Get the elemental stiffness matrix of an element */
    auto stiffness_matrix_of(std::size_t hexahedron_id) const -> const auto & {
        return p_elements_stiffness_matrices[hexahedron_id];
    }

    /** Get the complete tangent stiffness matrix as a compressed sparse matrix */
    auto K() -> const Eigen::SparseMatrix<Real> &;

    /** Get the eigen values of the tangent stiffness matrix */
    auto eigenvalues() -> const Vector<Eigen::Dynamic> &;

    /** Get the condition number of the tangent stiffness matrix */
    auto cond() -> Real;

protected:
    // These protected methods are implemented but can be overridden
    /**
     * Return true if the mesh topology is compatible with the type Element.
     *
     * This internal function is used when the scene graph is created and no template is specified to this component.
     * When a MeshTopology is found in the context node, this function will return true if the MeshTopology is a good
     * hint of the element type that should be used. For example, if a TetrahedronSetTopologyContainer passed as
     * parameter, than HyperelasticForcefield<Tetrahedron>::mesh_is_compatible(topology) will return true.
     */
    inline
    static auto mesh_is_compatible(const sofa::core::topology::BaseMeshTopology *) -> bool {
        return false;
    }

private:

    // These private methods are implemented but can be overridden

    /** Get the element nodes indices relative to the state vector */
    virtual auto get_element_nodes_indices(const std::size_t &) const -> const Index * {
        return nullptr;
    }

    /** Compute and store the shape functions and their derivatives for every integration points */
    virtual void initialize_elements();

    /** Update the stiffness matrix for every elements */
    virtual void update_stiffness();

    /** Get the set of Gauss integration nodes of the given element */
    virtual auto get_gauss_nodes(const std::size_t & element_id, const Element & element) const -> GaussContainer;

    // Data members
    Link<sofa::core::topology::BaseMeshTopology> d_topology_container;
    Link<material::HyperelasticMaterial<DataTypes>> d_material;

    // Private variables
    std::vector<Matrix<NumberOfNodes*Dimension, NumberOfNodes*Dimension>> p_elements_stiffness_matrices;
    std::vector<GaussContainer> p_elements_quadrature_nodes;
    Eigen::SparseMatrix<Real> p_sparse_K;
    Eigen::Matrix<Real, Eigen::Dynamic, 1> p_eigenvalues;
    bool elements_stiffness_matrices_are_up_to_date = false;
    bool sparse_K_is_up_to_date = false;
    bool eigenvalues_are_up_to_date = false;
};

} // namespace SofaCaribou::forcefield
