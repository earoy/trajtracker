"""

 Allow mouse to move only according to a given image - from light color to a darker color (or vice versa)

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numpy as np

import trajtracker._utils as _u
import trajtracker.utils as u
import trajtracker.validators
from trajtracker.misc import LocationColorMap
from trajtracker.validators import _BaseValidator
from trajtracker.data import fromXML



class MoveByGradientValidator(_BaseValidator):

    max_irrelevant_color_value = 10
    cyclic_ratio = 5

    err_gradient = "GradientViolation"


    def __init__(self, image, position=(0, 0), rgb_should_ascend=True, max_valid_back_movement=0,
                 cyclic=False, enabled=True):
        """
        Constructor

        :param image: Name of a BMP file, or the actual image (rectangular matrix of colors)
        :param position: See :attr:`~trajtracker.movement.MoveByGradientValidator.enabled`
        :param position: See :attr:`~trajtracker.movement.MoveByGradientValidator.position`
        :param rgb_should_ascend: See :attr:`~trajtracker.movement.MoveByGradientValidator.rgb_should_ascend`
        :param max_valid_back_movement: See :attr:`~trajtracker.movement.MoveByGradientValidator.max_valid_back_movement`
        :param cyclic: See :attr:`~trajtracker.movement.MoveByGradientValidator.cyclic`
        """
        super(MoveByGradientValidator, self).__init__(enabled=enabled)

        self._lcm = LocationColorMap(image, position=position, use_mapping=True, colormap="RGB")
        self.rgb_should_ascend = rgb_should_ascend
        self.max_valid_back_movement = max_valid_back_movement
        self.cyclic = cyclic
        self.color_filter = None
        self.reset()


    #======================================================================
    #   Properties
    #======================================================================

    #-------------------------------------------------
    @property
    def position(self):
        """
        The position of the image: (x,y) tuple/list, indicating the image center
        For even-sized images, use the Expyriment standard.
        The position is used to align the image's coordinate space with that of update_xyt()
        """
        return self._lcm.position

    @position.setter
    @fromXML(_u.parse_coord)
    def position(self, value):
        self._lcm.position = value


    #-------------------------------------------------
    @property
    def rgb_should_ascend(self):
        """
        Whether the valid movement is from lower RGB codes to higher RGB codes (True) or vice versa (False)
        """
        return self._rgb_should_ascend


    @rgb_should_ascend.setter
    @fromXML(bool)
    def rgb_should_ascend(self, value):
        _u.validate_attr_type(self, "rgb_should_ascend", value, bool)
        self._rgb_should_ascend = value
        self._log_setter("rgb_should_ascend")


    #-------------------------------------------------
    @property
    def max_valid_back_movement(self):
        """
        The maximal valid delta of color-change in the opposite direction that would still be allowed
        """
        return self._max_valid_back_movement


    @max_valid_back_movement.setter
    @fromXML(float)
    def max_valid_back_movement(self, value):
        _u.validate_attr_numeric(self, "max_valid_back_movement", value)
        _u.validate_attr_not_negative(self, "max_valid_back_movement", value)
        self._max_valid_back_movement = value
        self._log_setter("max_valid_back_movement")


    #-------------------------------------------------
    @property
    def single_color(self):
        """
        Consider only one color out of the three (red / green / blue) available in the image.
        Each pixel in the image has a value between 0 and 255 for each of the 3 colors.
        If you set a single color (by setting this attribute to "R"/"G"/"B"), the validator will consider
        only the value of the selected color. Furthermore, the validator considers only pixels that are purely of
        this color (e.g., if you select "B", it means that only pixels with blue=0-255, red=0 and green=0 are
        relevant for validation).

        To accomodate small possible mistakes in the generation of the BMP image, the validator allows for
        miniscule presence of the irrelevant colors: i.e., if you set single_color="B", the validator will
        consider only pixels with blue=0-255, red<10, and green<10 (the treshold 10 can be changed by setting
        MoveByGradientValidator.max_irrelevant_color_value); and for this pixels, the validator will consider
        only the blue value.
        """
        return self._single_color

    @single_color.setter
    def single_color(self, value):
        _u.validate_attr_type(self, "color_filter", value, str, none_allowed=True)
        if value is not None and value not in self._colormaps:
            raise ValueError("trajtracker error: invalid value for {:}.single_color ({:}) - valid values are {:}".format(
                type(self).__name__, value, ",".join(self._colormaps.keys())))

        self._single_color = value
        self._lcm.colormap = None if value is None else self._colormaps[value]
        self._calc_min_max_colors()


    def _calc_min_max_colors(self):
        if self._single_color is None:
            mapping_func = lambda color: u.color_rgb_to_num(color)
        else:
            mapping_func = self._colormaps[self._single_color]

        colors = [mapping_func(color) for color in self._lcm.available_colors]
        colors = [c for c in colors if c is not None]
        self._min_available_color = None if len(colors) == 0 else min(colors)
        self._max_available_color = None if len(colors) == 0 else max(colors)


    _colormaps = {
        'R': lambda color: None if color[1] > MoveByGradientValidator.max_irrelevant_color_value or \
                                   color[2] > MoveByGradientValidator.max_irrelevant_color_value else color[0],

        'G': lambda color: None if color[0] > MoveByGradientValidator.max_irrelevant_color_value or \
                                   color[2] > MoveByGradientValidator.max_irrelevant_color_value else color[1],

        'B': lambda color: None if color[0] > MoveByGradientValidator.max_irrelevant_color_value or \
                                   color[1] > MoveByGradientValidator.max_irrelevant_color_value else color[2],
    }

    #-------------------------------------------------
    @property
    def cyclic(self):
        """
        Whether the gradient is cyclic, i.e., allows moving between the darkest to the lightest color
        """
        return self._cyclic

    @cyclic.setter
    @fromXML(bool)
    def cyclic(self, value):
        _u.validate_attr_type(self, "cyclic", value, bool)
        self._cyclic = value


    #======================================================================
    #   Validate
    #======================================================================

    #-----------------------------------------------------------------
    def reset(self, time0=None):
        """
        Reset the movement validation
        """

        self._log_func_enters("reset", [time0])

        self._last_color = None


    #-----------------------------------------------------------------
    def update_xyt(self, x_coord, y_coord, time=None):
        """
        Validate the movement

        :return: None if all OK, ExperimentError if error
        """

        if not self._enabled:
            return None

        _u.update_xyt_validate_and_log(self, x_coord, y_coord, time, False)

        color = self._lcm.get_color_at(x_coord, y_coord)
        if color is None:  # color N/A -- can't validate
            self._last_color = None
            return None

        if self._last_color is None:
            #-- Nothing to validate
            self._last_color = color
            return None

        expected_direction = 1 if self._rgb_should_ascend else -1
        rgb_delta = (color - self._last_color) * expected_direction
        if rgb_delta >= 0:
            #-- All is OK
            self._last_color = color
            return None

        if rgb_delta >= -self._max_valid_back_movement:
            #-- The movement was in the opposite color diredction, but only slightly:
            #-- Don't issue an error, but also don't update "last_color" - remember the previous one
            return None

        if self._cyclic and self._min_available_color is not None:
            range = self._max_available_color - self._min_available_color
            if np.abs(rgb_delta) >= self.cyclic_ratio * (range - np.abs(rgb_delta)):
                # It's much more likely to interpret this movement as a "cyclic" movement - i.e., one that crossed
                # the boundary of lightest-to-darkest (or the other way around, depending on the ascend/descend direction)
                self._last_color = color
                return None

        if self._should_log(self.log_debug):
            self._log_write("InvalidDirection,last_color={:},curr_color={:}".format(self._last_color, color), True)

        return trajtracker.validators.create_experiment_error(self, self.err_gradient, "You moved in an invalid direction")


