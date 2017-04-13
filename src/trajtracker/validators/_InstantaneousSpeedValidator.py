"""

  Validator for minimal/maximal instantaneous speed

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

import numbers

import trajtracker._utils as _u
import trajtracker.validators
from trajtracker.movement import SpeedMonitor
from trajtracker.data import fromXML
from trajtracker.misc import EnabledDisabledObj
from trajtracker.validators import ValidationAxis, ExperimentError


# noinspection PyAttributeOutsideInit
class InstantaneousSpeedValidator(trajtracker.TTrkObject, EnabledDisabledObj):

    err_too_slow = "TooSlowInstantaneous"
    err_too_fast = "TooFast"
    arg_speed = 'speed'  # ExperimentError argument: the speed observed

    #-----------------------------------------------------------------------------------
    def __init__(self, axis=ValidationAxis.y, enabled=True, min_speed=None, max_speed=None,
                 grace_period=0, calculation_interval=0, movement_monitor=None):
        """
        Constructor - invoked when you create a new object by writing InstantaneousSpeedValidator()

        :param axis: See :attr:`~trajtracker.validators.InstantaneousSpeedValidator.axis`
        :param enabled: See :attr:`~trajtracker.validators.InstantaneousSpeedValidator.enabled`
        :param min_speed: See :attr:`~trajtracker.validators.InstantaneousSpeedValidator.min_speed`
        :param max_speed: See :attr:`~trajtracker.validators.InstantaneousSpeedValidator.max_speed`
        :param grace_period: See :attr:`~trajtracker.validators.InstantaneousSpeedValidator.grace_period`
        :param calculation_interval: See :attr:`~trajtracker.validators.InstantaneousSpeedValidator.calculation_interval`
        """

        trajtracker.TTrkObject.__init__(self)
        EnabledDisabledObj.__init__(self, enabled=enabled)

        if movement_monitor is None:
            self._speed_monitor = SpeedMonitor(calculation_interval)
        elif isinstance(movement_monitor, SpeedMonitor):
            self._speed_monitor = movement_monitor
        else:
            raise trajtracker.ValueError(_u.ErrMsg.invalid_method_arg_type(self.__class__, "__init__", "movement_monitor", "InstMovementMonitor", movement_monitor))

        self.axis = axis
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.grace_period = grace_period
        self.calculation_interval = calculation_interval

        self.reset()


    #========================================================================
    #      Validation API
    #========================================================================


    #-----------------------------------------------------------------------------------
    def reset(self, time0=None):
        """
        Called when a trial starts - reset any previous movement

        :param time0: The time when the trial starts. The grace period will be determined according to this time.
        """

        self._log_func_enters("reset", [time0])

        self._speed_monitor.reset(time0)


    #-----------------------------------------------------------------------------------
    def update_xyt(self, x_coord, y_coord, time_in_trial):
        """
        Given a current position, check whether the movement complies with the speed limits.

        :param x_coord: Current x coordinate (in the predefined coordinate system)
        :param y_coord: Current y coordinate (in the predefined coordinate system)
        :param time_in_trial: Time, in seconds. The zero point doesn't matter, as long as you're consistent until reset() is called.
        :return: None if all OK, ExperimentError if error
        """

        if not self._enabled:
            return None

        _u.update_xyt_validate_and_log(self, x_coord, y_coord, time_in_trial)

        self._speed_monitor.update_xyt(x_coord, y_coord, time_in_trial)


        #-- Calculate speed, if possible
        if self._speed_monitor.time_in_trial is not None and \
            self._speed_monitor.time_in_trial > self._grace_period and \
                self._speed_monitor.last_calculation_interval is not None:

            if self._axis == ValidationAxis.x:
                speed = self._speed_monitor.xspeed

            elif self._axis == ValidationAxis.y:
                speed = self._speed_monitor.yspeed

            elif self._axis == ValidationAxis.xy:
                speed = self._speed_monitor.xyspeed

            else:
                return None

            if self._min_speed is not None and speed < self._min_speed:
                return trajtracker.validators.create_experiment_error(self, self.err_too_slow, "You moved too slowly", {self.arg_speed: speed})

            if self._max_speed is not None and speed > self._max_speed:
                return trajtracker.validators.create_experiment_error(self, self.err_too_fast, "You moved too fast", {self.arg_speed: speed})

        return None


    #========================================================================
    #      Config
    #========================================================================

    #-----------------------------------------------------------------------------------
    @property
    def axis(self):
        """
        The ValidationAxis on which speed is validated
        ValidationAxis.x or ValidationAxis.y: limit the speed in the relevant axis.
        ValidationAxis.xy: limit the diagonal speed
        """
        return self._axis

    @axis.setter
    @fromXML(ValidationAxis.parse)
    def axis(self, value):
        _u.validate_attr_type(self, "axis", value, ValidationAxis)
        self._axis = value
        self._log_property_changed("axis")


    #-----------------------------------------------------------------------------------
    @property
    def min_speed(self):
        """
        The minimal valid instantaneous speed (coords/sec).
        Only positive values are valid. None = minimal speed will not be enforced.
        """
        return self._min_speed

    @min_speed.setter
    @fromXML(float)
    def min_speed(self, value):
        _u.validate_attr_numeric(self, "min_speed", value, none_value=_u.NoneValues.Valid)
        _u.validate_attr_positive(self, "min_speed", value)
        self._min_speed = value
        self._log_property_changed("min_speed")

    #-----------------------------------------------------------------------------------
    @property
    def max_speed(self):
        """
        The maximal valid instantaneous speed (coords/sec).
        Only positive values are valid. None = maximal speed will not be enforced.
        """
        return self._max_speed

    @max_speed.setter
    @fromXML(float)
    def max_speed(self, value):
        _u.validate_attr_numeric(self, "max_speed", value, none_value=_u.NoneValues.Valid)
        _u.validate_attr_positive(self, "max_speed", value)
        self._max_speed = value
        self._log_property_changed("max_speed")

    #-----------------------------------------------------------------------------------
    @property
    def grace_period(self):
        """The grace period in the beginning of each trial, during which speed is not validated (in seconds)."""
        return self._grace_period

    @grace_period.setter
    @fromXML(float)
    def grace_period(self, value):
        value = _u.validate_attr_numeric(self, "grace_period", value, none_value=_u.NoneValues.ChangeTo0)
        _u.validate_attr_not_negative(self, "grace_period", value)
        self._grace_period = value
        self._log_property_changed("grace_period")

    #-----------------------------------------------------------------------------------
    @property
    def calculation_interval(self):
        """
        Time interval (in seconds) for testing speed: the speed is calculated according to the difference in
        (x,y) coordinates over a time interval at least this long.
        """
        return self._speed_monitor.calculation_interval

    @calculation_interval.setter
    @fromXML(float)
    def calculation_interval(self, value):
        self._speed_monitor.calculation_interval = value
        self._log_property_changed("calculation_interval")
