"""

Base class for RSVP stimuli

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numbers
import numpy as np

from expyriment.misc.geometry import XYPoint

import trajtracker
import trajtracker._utils as _u
import trajtracker.utils as u
from trajtracker.events import Event
from trajtracker.events import TRIAL_INITIALIZED, TRIAL_ENDED


class BaseRSVPStim(trajtracker._TTrkObject):


    def __init__(self, onset_time=None, duration=None, last_stimulus_remains=False):

        super(BaseRSVPStim, self).__init__()

        self._event_manager = None
        self.trial_configured_event = TRIAL_INITIALIZED
        self.start_rsvp_event = None
        self.terminate_rsvp_event = TRIAL_ENDED

        self.onset_time = onset_time
        self.duration = duration
        self.last_stimulus_remains = last_stimulus_remains


    #----------------------------------------------------
    def on_registered(self, event_manager):
        self._event_manager = event_manager

        #-- Whenever the trial starts: register specifc events
        event_manager.register_operation(event=self._trial_configured_event,
                                         operation=lambda t1, t2: self._init_trial_events(),
                                         recurring=True,
                                         description="Setup the trial's RSVP")


    #==============================================================================
    #   Configuration
    #==============================================================================

    #----------------------------------------------------
    @property
    def trial_configured_event(self):
        """
        An event indicating the time when the per-trial RSVP information was configured.
        By default, this is the TRIAL_INIITALIZED event.

        **Note:**

        - This property is relevant only when working with events (and with an :class:`~trajtracker.events.EventManager`)
        - The property cannot be changed after the object was registered to an :class:`~trajtracker.events.EventManager`
        """
        return self._trial_configured_event

    @trial_configured_event.setter
    def trial_configured_event(self, event):
        _u.validate_attr_type(self, "registration_event", event, Event)
        if self._event_manager is not None:
            raise trajtracker.InvalidStateError(("{:}.trial_configured_event cannot be changed after " +
                                                 "registering to the event manager".format(
                                                     type(self).__name__)))
        self._trial_configured_event = event
        self._log_property_changed("trial_configured_event")


    #----------------------------------------------------
    @property
    def start_rsvp_event(self):
        """
        The event on which the RSVP should start appearing. The onset times are indicated relatively to this event.

        **Note:** This property is relevant only when working with events (and with an
        :class:`~trajtracker.events.EventManager`)
        """
        return self._start_rsvp_event

    @start_rsvp_event.setter
    def start_rsvp_event(self, event):
        _u.validate_attr_type(self, "start_rsvp_event", event, Event, none_allowed=True)
        self._start_rsvp_event = event
        self._log_property_changed("start_rsvp_event")


    #----------------------------------------------------
    @property
    def terminate_rsvp_event(self):
        """
        An event that terminates the RSVP, even if it's already started. Default: TRIAL_ENDED.

        You can set to None to disable termination; however, note that in this case you might get strange
        behavior if the next trial starts while the RSVP is still playing. To prevent this, you'll have to
        take care yourself of cleaning up pending operations from the event manager.

        **Note:** This property is relevant only when working with events (and with an
        :class:`~trajtracker.events.EventManager`)
        """
        return self._terminate_rsvp_event

    @terminate_rsvp_event.setter
    def terminate_rsvp_event(self, event):
        _u.validate_attr_type(self, "cancel_rsvp_event", event, Event, none_allowed=True)
        self._terminate_rsvp_event = event
        self._log_property_changed("terminate_rsvp_event")


    #----------------------------------------------------
    @property
    def onset_time(self):
        return self._onset_time

    @onset_time.setter
    def onset_time(self, value):

        if value is not None:
            _u.validate_attr_anylist(self, "onset_time", value, min_length=1)
            for i in range(len(value)):
                _u.validate_attr_numeric(self, "onset_time[%d]" % i, value[i])
                _u.validate_attr_not_negative(self, "onset_time[%d]" % i, value[i])

        self._onset_time = value
        self._onset_time_multiple = True
        self._log_property_changed("onset_time")


    #----------------------------------------------------
    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):

        is_multiple = False

        if isinstance(value, numbers.Number):
            _u.validate_attr_positive(self, "duration", value)

        elif value is not None:
            is_multiple = True
            _u.validate_attr_anylist(self, "duration", value, min_length=1)
            for i in range(len(value)):
                _u.validate_attr_numeric(self, "duration[%d]" % i, value[i])
                _u.validate_attr_positive(self, "duration[%d]" % i, value[i])

        self._duration = value
        self._duration_multiple = is_multiple
        self._log_property_changed("duration")


    #----------------------------------------------------
    @property
    def last_stimulus_remains(self):
        return self._last_stimulus_remains

    @last_stimulus_remains.setter
    def last_stimulus_remains(self, value):
        _u.validate_attr_type(self, "last_stimulus_remains", value, bool)
        self._last_stimulus_remains = value
        self._log_property_changed("last_stimulus_remains")


    #==============================================================================
    #   Misc.
    #==============================================================================

    #-----------------------------------------------------------------
    def _is_multiple_values(self, value, prop_type):

        if type(prop_type) == type:
            return isinstance(value, (tuple, list, np.ndarray))
        elif prop_type == "RGB":
            return isinstance(value, (tuple, list, np.ndarray)) and \
                    (len(value) == 0 or u.is_rgb(value[0]))
        elif prop_type == "coord":
            return isinstance(value, (tuple, list, np.ndarray)) and \
                    (len(value) == 0 or isinstance(value[0], (tuple, list, XYPoint, np.ndarray)))
        else:
            raise Exception("Trajtracker internal error: {:}._validate_attr_type() does not support type={:}".format(
                type(self).__name__, prop_type))


    #-----------------------------------------------------------------
    def _set_property(self, prop_name, value, prop_type, allow_single_value=True, allow_none=True):

        multiple_values = False

        if value is None and not allow_none:
                raise TypeError("trajtracker error: {:}.{:} cannot be set to None".format(
                        type(self).__name__, prop_name))

        if value is not None:

            multiple_values = self._is_multiple_values(value, prop_type)
            if multiple_values:
                if len(value) == 0:
                    raise TypeError("trajtracker error: {:}.{:} cannot be set to an empty list".format(
                            type(self).__name__, prop_name))
                for v in value:
                    _u.validate_attr_type(self, prop_name, v, prop_type)
                value = list(value)
            elif allow_single_value:
                _u.validate_attr_type(self, prop_name, value, prop_type, none_allowed=True)
            else:
                raise TypeError("trajtracker error: {:}.{:} must be set to a list of values; a single {:} is invalid".format(
                    type(self).__name__, prop_name, prop_type.__name__ if isinstance(prop_type, type) else prop_type))

        setattr(self, "_" + prop_name, value)
        setattr(self, "_" + prop_name + "_multiple", multiple_values)

