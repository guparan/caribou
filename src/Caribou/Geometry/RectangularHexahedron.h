#ifndef CARIBOU_GEOMETRY_RECTANGULARHEXAHEDRON_H
#define CARIBOU_GEOMETRY_RECTANGULARHEXAHEDRON_H

#include <Caribou/config.h>
#include <Caribou/Geometry/Quad.h>
#include <Caribou/Geometry/Segment.h>
#include <Caribou/Geometry/Interpolation/Hexahedron.h>
#include <Caribou/Geometry/Internal/BaseHexahedron.h>

namespace caribou::geometry {

template <typename CanonicalElementType = interpolation::Hexahedron8>
struct RectangularHexahedron : public internal::BaseHexahedron<CanonicalElementType, RectangularHexahedron<CanonicalElementType>>
{
    static constexpr INTEGER_TYPE NumberOfNodes = CanonicalElementType::NumberOfNodes;

    using Base = internal::BaseHexahedron<CanonicalElementType, RectangularHexahedron<CanonicalElementType>>;

    using LocalCoordinates = typename Base::LocalCoordinates;
    using WorldCoordinates = typename Base::WorldCoordinates;

    using QuadType = Quad<3, typename CanonicalElementType::QuadType>;

    template<int nRows, int nColumns, int Options=0>
    using Matrix = Eigen::Matrix<FLOATING_POINT_TYPE, nRows, nColumns, Options>;

    template<int nRows, int nColumns>
    using Map = Eigen::Map<const Matrix<nRows, nColumns, Eigen::RowMajor>>;

    template<int nRows, int Options=0>
    using Vector = Eigen::Matrix<FLOATING_POINT_TYPE, nRows, 1, Options>;

    template<int nRows>
    using MapVector = Eigen::Map<const Vector<nRows, Eigen::ColMajor>>;

    using Mat33 = Matrix<3, 3>;
    using Size = Vector<3>;

    constexpr
    RectangularHexahedron()
            : p_center {0, 0, 0}, p_H {2, 2, 2}, p_R (Mat33::Identity())
    {}

    constexpr
    RectangularHexahedron(const WorldCoordinates & center, const Size & dimensions, const Mat33 & rotation)
            : p_center (center), p_H (dimensions), p_R (rotation)
    {}

    constexpr
    RectangularHexahedron(const WorldCoordinates & center, const Size & dimensions)
            : p_center (center), p_H (dimensions), p_R (Mat33::Identity())
    {}

    constexpr
    RectangularHexahedron(const WorldCoordinates & center)
        : p_center (center), p_H  {2,2,2}, p_R (Mat33::Identity())
    {}

    /** Get the Node at given index */
    inline
    auto
    node(UNSIGNED_INTEGER_TYPE index) const
    {
        const auto local_coordinates_of_node = MapVector<3>(CanonicalElementType::nodes[index]);
        return T(local_coordinates_of_node);
    }

    /** Get the Node at given index */
    inline
    auto
    node(UNSIGNED_INTEGER_TYPE index)
    {
        const auto local_coordinates_of_node = MapVector<3>(CanonicalElementType::nodes[index]);
        return T(local_coordinates_of_node);
    }

    /** Get a reference to the set of nodes */
    inline
    Matrix<NumberOfNodes, 3>
    nodes() const
    {
        Matrix<NumberOfNodes, 3> m;
        for (size_t i = 0; i < CanonicalElementType::NumberOfNodes; ++i)
            m.row() = node(i).translate();
        return nodes;
    }

    /** Compute the volume of the hexa */
    inline
    FLOATING_POINT_TYPE
    volume() const
    {
        const auto hx = (node(0) - node(1)).length();
        const auto hy = (node(0) - node(3)).length();
        const auto hz = (node(0) - node(4)).length();
        return hx*hy*hz;
    }

    /** Get the center point position */
    inline
    WorldCoordinates
    center() const
    {
        return p_center;
    }

    /**
     * Get the local coordinates frame (a.k.a. the rotation matrix) positioned at the center of the hexahedron
     */
    inline
    Mat33
    frame() const
    {
        return p_R;
    }

    /**
     * Compute the jacobian matrix evaluated at local position {u,v,w}
     *
     * For a rectangular hexahedron, the jacobian matrix is constant and is defined as
     *
     *     1 | hx 0  0  |
     * J = - | 0  hy 0  |
     *     2 | 0  0  hz |
     *
     * where hx, hy, and hz are the dimension of the edges 0-1, 0-3 and 0-4 respectively.
     */
    inline
    Mat33
    jacobian (const LocalCoordinates & /*coordinates*/) const
    {
        return jacobian();
    }

    /**
     * Compute the jacobian matrix.
     *
     * For a rectangular hexahedron, the jacobian matrix is constant and is defined as
     *
     *     1 | hx 0  0  |
     * J = - | 0  hy 0  |
     *     2 | 0  0  hz |
     *
     * where hx, hy, and hz are the dimension of the edges 0-1, 0-3 and 0-4 respectively.
     */
    inline
    Mat33
    jacobian () const
    {
        return (1/2.*p_H).asDiagonal();
    }

    /**
     * Compute the transformation of a local position {u,v,w} to its world position {x,y,z}
     */
    inline
    WorldCoordinates
    T(const LocalCoordinates & coordinates) const
    {
        return p_center + ((p_R * coordinates).array()*(p_H/2.).array()).matrix();
    }

    /**
     * Compute the inverse transformation of a world position {x,y,z} to its local position {u,v,w}
     */
    inline
    LocalCoordinates
    Tinv(const WorldCoordinates & coordinates) const
    {
        return p_R.transpose() * ((coordinates - p_center).array() / (p_H/2.).array()).matrix();
    }

    /**
     * Test if the cube intersects the given 3D segment (in world coordinates)
     *
     * @note  based on polygon_intersects_cube by Don Hatch (January 1994)
     */
    inline
    bool
    intersects(const Segment<3> & segment) const
    {
        return intersects_local(
            Segment<3>(
                Tinv(segment.node(0)),
                Tinv(segment.node(1))
            )
        );
    }

    /**
     * Test if the cube intersects the given 3D segment (in the hexahedron's local coordinates)
     *
     * @note  based on polygon_intersects_cube by Don Hatch (January 1994)
     */
    inline
    bool
    intersects_local(const Segment<3> & segment) const
    {
        const auto & v0 = segment.node(0) / 2.; // Shrink to a cube of size 1x1x1 centered on 0
        const auto & v1 = segment.node(1) / 2.; // Shrink to a cube of size 1x1x1 centered on 0

        const auto edge = (v1 - v0);
        INTEGER_TYPE edge_signs[3];

        for (UNSIGNED_INTEGER_TYPE i = 0; i < 3; ++i) {
            edge_signs[i] = (edge[i] < 0) ? -1 : 1;
        }

        for (UNSIGNED_INTEGER_TYPE i = 0; i < 3; ++i) {

            if (v0[i] * edge_signs[i] >  .5+EPSILON) return false;
            if (v1[i] * edge_signs[i] < -.5-EPSILON) return false;
        }


        for (UNSIGNED_INTEGER_TYPE i = 0; i < 3; ++i) {
            FLOATING_POINT_TYPE rhomb_normal_dot_v0, rhomb_normal_dot_cubedge;

            const UNSIGNED_INTEGER_TYPE iplus1 = (i + 1) % 3;
            const UNSIGNED_INTEGER_TYPE iplus2 = (i + 2) % 3;

            rhomb_normal_dot_v0 =   edge[iplus2] * v0[iplus1]
                                    - edge[iplus1] * v0[iplus2];

            rhomb_normal_dot_cubedge = .5 *
                                       (edge[iplus2] * edge_signs[iplus1] +
                                        edge[iplus1] * edge_signs[iplus2]);

            const auto r = (rhomb_normal_dot_v0*rhomb_normal_dot_v0) - (rhomb_normal_dot_cubedge*rhomb_normal_dot_cubedge);
            if (r > EPSILON)
                return false;
        }

        return true;
    }

    /**
     * Test if the cube intersects the given 3D polygon (in world coordinates).
     *
     * @note  based on polygon_intersects_cube by Don Hatch (January 1994)
     * @tparam NNodes Number of nodes in the polygon
     * @param nodes The nodes of the polygon
     * @param polynormal Vector perpendicular to the polygon.  It need not be of unit length.
     * @return True if the polygon intersects the cube, false otherwise.
     */
    template <int NNodes>
    inline
    bool
    intersects_polygon(const WorldCoordinates /*nodes*/[NNodes], const Vector<3> & /*polynormal*/)
    {
        // todo(jnbrunet2000@gmail.com): do it
        return false;
    }

    /**
     * Compute an integral approximation by gauss quadrature on the hexahedron of the given evaluation function.
     *
     * @example
     * \code{.cpp}
     * // Integrate the polynomial 1 + 2x + 2xy + 3*z on an hexahedron.
     * float result = RectangularHexahedron(x1, x2, x3, x4, x5, x6, x7, x8).gauss_integrate(
     *   [] (const RectangularHexahedron & hexa, const RectangularHexahedron::LocalCoordinates & coordinates) -> float {
     *     const auto & xi   = coordinates[0];
     *     const auto & eta  = coordinates[1];
     *     const auto & zeta = coordinates[2];
     *     return 1 + 2*xi + 2*xi*eta + 3*zeta;
     *   }
     * );
     * \endcode
     *
     * @tparam EvaluateFunctionType Callback function reference type. See f parameter.
     *
     * @param f
     * Callback function of the signature
     *
     *     ValueType f (const Hexahedron & hexa, const LocalCoordinates & coordinates);
     *
     * Where hexa is a reference to the current hexahadron on which we integrate, and the coordinates u, v and w
     * forms the local position of a sample point on which we want to get the evaluation value.
     *
     * @return The value of the integral computed on this hexahedron.
     *
     */
    template <typename EvaluateFunctor>
    inline
    auto
    gauss_quadrature(EvaluateFunctor f) const
    {
        // Constant for parallelepiped hexahedrons
        const auto detJ = jacobian().determinant();

        const auto p0 = MapVector<3>(CanonicalElementType::gauss_nodes[0]);
        const auto w0 = CanonicalElementType::gauss_weights[0];
        const auto eval0 = f(*this, p0);
        auto result = eval0 * w0 * detJ;

        for (std::size_t i = 1; i < CanonicalElementType::number_of_gauss_nodes; ++i) {
            const auto p = MapVector<3>(CanonicalElementType::gauss_nodes[i]);
            const auto w = CanonicalElementType::gauss_weights[i];
            const auto eval = f(*this, p);
            result += eval * w * detJ;
        }

        return result;
    }

private:
    WorldCoordinates p_center; ///< Position of the center point of the hexahedron
    Size p_H; ///< Size of the hexahedron {hx, hy, hz}
    Mat33 p_R; ///< Rotation matrix (a.k.a. the local coordinates frame) at the center of the hexahedron
};

RectangularHexahedron() -> RectangularHexahedron<interpolation::Hexahedron8>;

} // namespace caribou::geometry
#endif //CARIBOU_GEOMETRY_RECTANGULARHEXAHEDRON_H
