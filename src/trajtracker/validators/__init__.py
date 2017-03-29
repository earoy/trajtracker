"""

TrajTracker - validators package

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

"""

import enum
import numbers

import trajtracker._utils as _u
from trajtracker import _TTrkObject

ValidationAxis = enum.Enum('ValidationAxis', 'x y xy')

from _ValidationFailed import ValidationFailed


#-------------------------------------------------------------------
class _BaseValidator(_TTrkObject):
    """
    Base class for validators
    """

    def __init__(self, enabled=False):
        super(_BaseValidator, self).__init__()
        self.enabled = enabled


    #--------------------------------------------------------------------
    @property
    def enabled(self):
        """Whether the validator is currently enabled (boolean)"""
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        _u.validate_attr_type(self, "enabled", value, bool)
        self._enabled = value


    #--------------------------------------------------------------------
    def _check_xyt_validate_and_log(self, x_coord, y_coord, time, time_used=True):

        _u.validate_func_arg_type(self, "check_xyt", "x_coord", x_coord, numbers.Number, type_name="numeric")
        _u.validate_func_arg_type(self, "check_xyt", "y_coord", y_coord, numbers.Number, type_name="numeric")

        if time_used:
            _u.validate_func_arg_type(self, "check_xyt", "time", time, numbers.Number, type_name="numeric")

        if self._should_log(self.log_trace):
            msg = "{0}.check_xyt,{1},{2}".format(type(self).__name__, x_coord, y_coord)
            if time_used:
                msg += ",{0}".format(time)
            self._log_write(msg)

    #--------------------------------------------------------------------
    def _create_validation_error(self, err_code, message, err_args=None):
        if self._should_log(self.log_warn):
            self._log_write("ValidationFailed,{0},{1},{2},{3}".format(type(self).__name__, err_code, message, err_args))

        return ValidationFailed(err_code, message, self, err_args)




from _GlobalSpeedValidator import GlobalSpeedValidator, GlobalSpeedGuide
from _InstantaneousSpeedValidator import InstantaneousSpeedValidator
from _LocationsValidator import LocationsValidator
from _MovementAngleValidator import MovementAngleValidator
from _MoveByGradientValidator import MoveByGradientValidator
from _NCurvesValidator import NCurvesValidator

