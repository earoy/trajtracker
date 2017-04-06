"""
Non-visual sector of a circle

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numpy as np

import trajtracker._utils as _u
import trajtracker.utils as u


class Sector(object):
    """
    A sector of a circle
    """

    def __init__(self, x, y, radius, from_angle, to_angle):
        """
        Constructor - invoked when you create a new object by writing Sector()

        :param x: the circle's center
        :param y: the circle's center
        :param radius:
        :param from_angle: Left end of the sector (degrees)
        :param to_angle: Right end of the sector (degrees)
        """

        _u.validate_func_arg_type(self, "__init__", "x", x, int)
        _u.validate_func_arg_type(self, "__init__", "y", y, int)
        _u.validate_func_arg_type(self, "__init__", "radius", radius, int)
        _u.validate_func_arg_type(self, "__init__", "from_angle", from_angle, int)
        _u.validate_func_arg_type(self, "__init__", "to_angle", to_angle, int)
        _u.validate_func_arg_positive(self, "__init__", "radius", radius)

        self.x = x
        self.y = y
        self.radius = radius
        self.from_angle = from_angle % 360
        self.to_angle = to_angle % 360


    def overlapping_with_position(self, pos):
        x, y = pos
        distance_from_center = np.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        if distance_from_center > self.radius:
            return False

        angle = u.get_angle((self.x, self.y), (x, y), as_degrees=True) % 360
        if self.from_angle < self.to_angle:
            return self.from_angle <= angle <= self.to_angle
        else:
            return not (self.to_angle <= angle <= self.from_angle)


    @property
    def position(self):
        return self.x, self.y