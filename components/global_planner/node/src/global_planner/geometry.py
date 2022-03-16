"""A module providing vector and bounding box functionality"""

from typing import Tuple, List
from math import sin, cos, pi, sqrt, atan2


def points_to_vector(p_1: Tuple[float, float], p_2: Tuple[float, float]) -> Tuple[float, float]:
    """Create the vector starting at p1 and ending at p2"""
    return p_2[0] - p_1[0], p_2[1] - p_1[1]


def vector_len(vec: Tuple[float, float]) -> float:
    """Compute the given vector's length"""
    return sqrt(vec[0]**2 + vec[1]**2)


def add_vector(v_1: Tuple[float, float], v_2: Tuple[float, float]) -> Tuple[float, float]:
    """Add the given vectors"""
    return v_1[0] + v_2[0], v_1[1] + v_2[1]


def sub_vector(v_1: Tuple[float, float], v_2: Tuple[float, float]) -> Tuple[float, float]:
    """Subtract the second vector from the first vector"""
    return v_1[0] - v_2[0], v_1[1] - v_2[1]


def rotate_vector(vector: Tuple[float, float], angle_rad: float) -> Tuple[float, float]:
    """Rotate the given vector by an angle"""
    return (cos(angle_rad) * vector[0] - sin(angle_rad) * vector[1],
            sin(angle_rad) * vector[0] + cos(angle_rad) * vector[1])


def scale_vector(vector: Tuple[float, float], new_len: float) -> Tuple[float, float]:
    """Amplify the length of the given vector"""
    old_len = vector_len(vector)
    if old_len == 0:
        return (0, 0)
    scaled_vector = (vector[0] * new_len / old_len,
                     vector[1] * new_len / old_len)
    return scaled_vector


def unit_vector(angle_rad: float) -> Tuple[float, float]:
    """Retrieve the unit vector representing the given direction."""
    return (cos(angle_rad), sin(angle_rad))


def vec2dir(start: Tuple[float, float], end: Tuple[float, float]) -> float:
    """Retrieve the given vector's direction in radians."""
    vec_dir = sub_vector(end, start)
    return atan2(vec_dir[1], vec_dir[0])


def norm_angle(angle_rad: float) -> float:
    """Normalize the given angle within [-pi, +pi)"""
    while angle_rad > pi:
        angle_rad -= 2.0 * pi
    while angle_rad < -pi:
        angle_rad += 2.0 * pi
    if angle_rad == pi:
        angle_rad = -pi

    if angle_rad < -pi or angle_rad >= pi:
        print('norm angle failed! this should never happen')

    return angle_rad


def orth_offset_right(start_point: Tuple[float, float], end_point: Tuple[float, float],
                      offset: float) -> Tuple[float, float]:
    """Calculate the orthogonal offset according the road width in right direction"""
    vector = points_to_vector(start_point, end_point)
    scaled_vector = scale_vector(vector, offset)
    return rotate_vector(scaled_vector, -pi / 2)


def orth_offset_left(start_point: Tuple[float, float], end_point: Tuple[float, float],
                      offset: float) -> Tuple[float, float]:
    """Calculate the orthogonal offset according the road width in left direction"""
    return sub_vector((0, 0), orth_offset_right(start_point, end_point, offset))


def bounding_box(start_point: Tuple[float, float], end_point: Tuple[float, float],
                 road_width: float) -> List[Tuple[float, float]]:
    """Calculate a bounding box around the start and end point with a given offset to the side."""

    # TODO: replace rectangular bounding boxes with polygons to handle curves currectly

    offset = orth_offset_right(start_point, end_point, road_width)

    # using the point symmetry (relative to origin) to build the points in 180 degree offset
    return [add_vector(start_point, offset),
            sub_vector(start_point, offset),
            sub_vector(end_point, offset),
            add_vector(end_point, offset)]


def is_below_line(l_1: Tuple[float, float], l_2: Tuple[float, float],
                  point: Tuple[float, float]) -> bool:
    """Determine whether the point p lies below
    a line defined by the points l1 and l2"""

    # normalize the points such that the leftmost
    # point of l1 and l2 is the coord system origin
    l_1, l_2 = (l_1, l_2) if l_1[0] < l_2[0] else (l_2, l_1)
    l_1, l_2, point = (0.0, 0.0), sub_vector(l_2, l_1), sub_vector(point, l_1)

    # determine the point l3 that lies on the linear
    # and has same the x coord as point p
    steem = l_2[1] / l_2[0]
    l_3 = (point[0], point[0] * steem)

    return point[1] < l_3[1]
