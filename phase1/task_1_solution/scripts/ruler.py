"""Local library containing metrics algorithms used to measure the environment and
determine the best course of action based on these metrics.
"""

import numpy as np

from constants import (
    FRONT_VISION_LEFT_POINT,
    FRONT_VISION_RIGHT_POINT,
    CROPPED_LATERAL_LEFT_VISION_POINT,
    CROPPED_LATERAL_RIGHT_VISION_POINT,
    LASER_INTERESTING_RANGE,
    LASER_RHO_THRESH
)


def line_dist_to_point(line, point):
    x1, y1, x2, y2 = line
    x0, y0 = point
    mod = np.abs((x2 - x1) * (y1 - y0) - (x1 - x0) * (y2 - y1))
    ro = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return mod / ro


def point_distance(x0, y0, x1, y1):
    return np.sqrt((x1 - x0)**2 + (y1 - y0)**2)


def closest_point(point, other_points):
    x0, y0 = point
    result = None
    for other_point in other_points:
        x1, y1 = other_point
        d = point_distance(x0, y0, x1, y1)
        if result is None or d < result[-1]:
            result = (np.array((x1, y1)), d)
    return result


def weighted_line_dist_to_point(line, point):
    line_dist = line_dist_to_point(line, point)
    _, inverse_weight = closest_point(point, line.reshape(2, 2))
    return line_dist / inverse_weight


def define_line_reducer_on_point(point):
    def reducer(a, b):
        _, dist_a = closest_point(point, a.reshape(2, 2))
        _, dist_b = closest_point(point, b.reshape(2, 2))
        return a if dist_a < dist_b else b
    return reducer


def front_shift_transfer_function(closest_front_left_line, closest_front_right_line, hidden = 1.5):
        (xl, yl), dl = (None, None), None
        (xr, yr), dr = (None, None), None

        if closest_front_left_line is not None:
            (xl, yl), dl = closest_point(FRONT_VISION_LEFT_POINT, closest_front_left_line.reshape(2, 2))
        else:
            xl, yl = FRONT_VISION_LEFT_POINT - (160, 0)
            dl = hidden * point_distance(xl, yl, *FRONT_VISION_LEFT_POINT)

        if closest_front_right_line is not None:
            (xr, yr), dr = closest_point(FRONT_VISION_RIGHT_POINT, closest_front_right_line.reshape(2, 2))
        else:
            xr, yr = FRONT_VISION_RIGHT_POINT + (160, 0)
            dr = hidden * point_distance(xr, yr, *FRONT_VISION_RIGHT_POINT)

        denum = point_distance(xl, yl, xr, yr)
        denum = np.log(denum) if denum > np.e else denum

        if np.abs(num := dl - dr) > 1 and denum != 0:
            return (np.pi / 2) * np.tanh((num / denum ** 2))
        return 0


def lateral_shift_transfer_function(closest_left_line, closest_right_line, hidden=1.35):
    (xl, yl), dl = (None, None), None
    (xr, yr), dr = (None, None), None

    if closest_left_line is not None:
        (xl, yl), dl = closest_point(CROPPED_LATERAL_LEFT_VISION_POINT, closest_left_line.reshape(2, 2))
    else:
        dl = hidden * point_distance(CROPPED_LATERAL_LEFT_VISION_POINT[0], 0, *CROPPED_LATERAL_LEFT_VISION_POINT)

    if closest_right_line is not None:
        (xr, yr), dr = closest_point(CROPPED_LATERAL_RIGHT_VISION_POINT, closest_right_line.reshape(2, 2))
    else:
        dr = hidden * point_distance(CROPPED_LATERAL_RIGHT_VISION_POINT[0], 480, *CROPPED_LATERAL_RIGHT_VISION_POINT)

    result = 0
    if  np.abs(d := dl - dr) > 1:
        result = (np.pi / 2) * np.tanh(np.sign(d) * 0.1 * np.log10(np.abs(d)))

    #if (closest_left_line is None and xr is not None and xr < CROPPED_LATERAL_RIGHT_VISION_POINT[0] - 80) or \
    #        (closest_right_line is None and xl is not None and xl < CROPPED_LATERAL_LEFT_VISION_POINT[0] - 80):
    #    result /= 4

    return result


def theta_weighted_sum(*, lateral_theta, front_theta, lateral_weight = 0.65, front_weight = 0.35, last_theta=None):
    """Sums the different theta values according to a given weight for each theta"""
    theta = 0

    if lateral_theta != 0 and front_theta != 0:
        theta = lateral_theta * lateral_weight + front_theta * front_weight
    else:
        theta = lateral_theta + front_theta

    if last_theta is not None:
        #theta -= last_theta / (12 * np.e)
        pass

    return theta


def alpha_theta(theta, last_theta=None):
    """Returns the angle in the oposite direction of theta that will be used
    to adjust the route after applying a theta angular rotation."""
    trace = 0
    if last_theta is not None:
        trace = last_theta / (12 * np.e)
    return -theta / 16 + trace 


def mask_laser_scan(value, lower=LASER_INTERESTING_RANGE[0], upper=LASER_INTERESTING_RANGE[1]):
    if value is not None:
        mask = np.ones_like(value)
        mask[:lower] = float('inf')
        mask[upper:] = float('inf')
        return mask * value
    return None


def laser_front_fillup_rate(values, mask_values=True, distance = LASER_RHO_THRESH):
    if not mask_values:
        values = mask_laser_scan(values)

    poi = values[LASER_INTERESTING_RANGE[0]:LASER_INTERESTING_RANGE[1]].copy()
    poi[poi > distance] = 0
    poi[poi != 0] = 1

    return np.mean(poi)

def laser_angles(laser_state):
    if laser_state is not None:
        min_angle = laser_state.angle_min
        max_angle = laser_state.angle_max
        step = (max_angle - min_angle) / len(laser_state.ranges)
        return np.arange(min_angle, max_angle, step)
    return None
