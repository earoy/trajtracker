"""

A text box that changes in RSVP

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

import numbers
import numpy as np
from operator import itemgetter

import expyriment as xpy

import trajtracker
# noinspection PyProtectedMember
import trajtracker._utils as _u
from trajtracker.data import fromXML
from trajtracker.stimuli import BaseRSVPStim, StimulusContainer


# noinspection PyProtectedMember
class RSVPText(BaseRSVPStim):


    #----------------------------------------------------
    def __init__(self, text=None, text_font=None, text_size=None, text_bold=False, text_italic=False, text_underline=False,
                 text_justification=None, text_colour=None, background_colour=None, size=None, position=None,
                 onset_time=None, duration=None, last_stimulus_remains=False,
                 start_rsvp_event=None, terminate_rsvp_event=None):

        super(RSVPText, self).__init__(onset_time=onset_time, duration=duration, last_stimulus_remains=last_stimulus_remains)

        self._stimuli = []
        self._container = StimulusContainer()
        self._event_manager = None

        self.text = text
        self.text_font = text_font
        self.text_size = text_size
        self.text_bold = text_bold
        self.text_italic = text_italic
        self.text_underline = text_underline
        self.text_justification = text_justification
        self.text_colour = text_colour
        self.background_colour = background_colour
        self.size = size
        self.position = position

        if start_rsvp_event is not None:
            self.start_rsvp_event = start_rsvp_event
        if terminate_rsvp_event is not None:
            self.terminate_rsvp_event = terminate_rsvp_event


    #----------------------------------------
    @property
    def stimulus(self):
        """
        A single stimulus that represents all the stimuli in this RSVP
        :type: StimulusContainer
        """
        return self._container

    #----------------------------------------
    @property
    def stim_visibility(self):
        """
        Return an array of booleans, indicating whether each stimulus is presently visible or not.
        The array has as many elements as :attr:`~trajtracker.stimuli.RSVPText.text`
        """
        n_stim = len(self._text)
        self._create_stimuli(n_stim)
        return [self._stimuli[i].visible for i in range(n_stim)]


    #----------------------------------------
    # If not enough TextBoxes exist - create additional
    #
    def _create_stimuli(self, n_stim):

        for i in range(len(self._stimuli), n_stim+1):
            is_multiple = self._is_multiple_values(self._size, "coord")
            stim = xpy.stimuli.TextBox("", self._size[i] if is_multiple else self._size)
            self._stimuli.append(stim)
            self._container.add(stim, visible=False)


    #----------------------------------------------------
    # Update the RSVP stimuli (before actually showing them)
    #
    def _configure_stimuli(self):
        self._log_func_enters("_configure_stimuli")
        self._validate()

        n_stim = len(self._text)
        self._create_stimuli(n_stim)

        self._set_stimuli_property("text", str, n_stim)
        self._set_stimuli_property("text_font", str, n_stim)
        self._set_stimuli_property("text_bold", bool, n_stim)
        self._set_stimuli_property("text_italic", bool, n_stim)
        self._set_stimuli_property("text_underline", bool, n_stim)
        self._set_stimuli_property("text_justification", str, n_stim)
        self._set_stimuli_property("text_colour", "RGB", n_stim)
        self._set_stimuli_property("background_colour", "RGB", n_stim)
        self._set_stimuli_property("size", "coord", n_stim)
        self._set_stimuli_property("position", "coord", n_stim)

    #----------------------------------------------------
    # Validate that this RSVP object is ready to go
    #
    def _validate(self):

        n_stim = len(self._text)
        self._validate_property("text")
        self._validate_property("text_font", n_stim)
        self._validate_property("text_size", n_stim)
        self._validate_property("text_bold", n_stim)
        self._validate_property("text_italic", n_stim)
        self._validate_property("text_underline", n_stim)
        self._validate_property("text_justification", n_stim)
        self._validate_property("text_colour", n_stim)
        self._validate_property("background_colour", n_stim)
        self._validate_property("size", n_stim)
        self._validate_property("position", n_stim)
        self._validate_property("onset_time", n_stim)
        self._validate_property("duration", n_stim)

        if self._start_rsvp_event is None:
            raise ValueError('trajtracker error: {:}._start_rsvp_event was not set'.format(type(self).__name__))


    #----------------------------------------------------
    # Validate that one property is defined OK
    #
    def _validate_property(self, prop_name, n_stim=0):

        value = getattr(self, prop_name)
        if value is None:
            raise ValueError('trajtracker error: {:}.{:} was not set'.format(type(self).__name__, prop_name))

        is_multiple_values = getattr(self, "_" + prop_name + "_multiple")
        if is_multiple_values and len(value) < n_stim:
            raise ValueError('trajtracker error: {:}.{:} has {:} values, but there are {:} RSVP stimuli'.format(
                type(self).__name__, prop_name, len(value), n_stim))

    #----------------------------------------------------
    # Set a single property of all self._stimuli
    #
    def _set_stimuli_property(self, prop_name, prop_type, n_stim):

        values = getattr(self, prop_name)
        if not self._is_multiple_values(values, prop_type):
            values = [values] * n_stim

        for i in range(n_stim):
            setattr(self._stimuli[i], prop_name, values[i])

    #==============================================================================
    #  For working with events: no public API
    #==============================================================================

    #----------------------------------------------------
    # Initialize everything for a specific trial
    #
    def _init_trial_events(self):
        self._log_func_enters("_init_trial_events")

        self._configure_stimuli()

        n_stim = len(self._text)

        duration = self._duration if self._duration_multiple else ([self._duration] * n_stim)

        op_ids = set()

        for i in range(n_stim):
            onset_event = self._start_rsvp_event + self._onset_time[i]
            id1 = self._event_manager.register_operation(event=onset_event,
                                                         recurring=False,
                                                         description="Show RSVP[{:}]({:})".format(i, self._text[i]),
                                                         operation=TextboxEnablerDisabler(self._stimuli[i], True, i),
                                                         cancel_pending_operation_on=self.terminate_rsvp_event)
            op_ids.add(id1)

            if i == n_stim - 1 and self._last_stimulus_remains:
                break

            offset_event = self._start_rsvp_event + self._onset_time[i] + duration[i]
            id2 = self._event_manager.register_operation(event=offset_event,
                                                         recurring=False,
                                                         description="Hide RSVP[{:}]({:})".format(i, self._text[i]),
                                                         operation=TextboxEnablerDisabler(self._stimuli[i], False, i),
                                                         cancel_pending_operation_on=self.terminate_rsvp_event)
            op_ids.add(id2)

        self._registered_ops = op_ids

        if self.terminate_rsvp_event is not None:
            self._event_manager.register_operation(event=self.terminate_rsvp_event,
                                                   recurring=False,
                                                   description="Terminate RSVP",
                                                   operation=lambda t1, t2: self._terminate_rsvp())


    #----------------------------------------------------
    # (when the event ends) if the RSVP was not yet presented fully, terminate whatever remained
    #
    def _terminate_rsvp(self):
        self._log_func_enters("_terminate_rsvp")
        self._event_manager.unregister_operation(self._registered_ops)
        for stim in self._stimuli:
            stim.visible = False


    #==============================================================================
    #   API for working without events
    #==============================================================================

    #----------------------------------------------------
    def init_for_trial(self):

        self._log_func_enters("init_for_trial")
        if self._event_manager is not None:
            self._log_write_if(self.log_warn, "init_for_trial() was called although the RSVP was registered to an event manager")

        self._configure_stimuli()

        n_stim = len(self._text)

        show_ops = zip(self._onset_time[:n_stim], [True] * n_stim, range(n_stim))

        duration = self._duration if self._duration_multiple else ([self._duration] * n_stim)
        offset_times = [self._onset_time[i] + duration[i] for i in range(n_stim)]
        hide_ops = zip(offset_times, [False] * n_stim, range(n_stim))
        if self._last_stimulus_remains:
            hide_ops = hide_ops[:-1]  # don't hide the last one

        self._show_hide_operations = sorted(show_ops + hide_ops, key=itemgetter(0))
        self._start_showing_time = None


    #----------------------------------------------------
    def start_showing(self, time):
        """
        *When working without events:* set time=0 for the RSVP sequence

        This function will also invoke :func:`~trajtracker.stimuli.RSVPText.update_rsvp`.

        :param time: The time in the current session/trial. This must be synchronized with the "time"
                     argument of :func:`~trajtracker.stimuli.RSVPText.update_rsvp`
        """

        self._log_func_enters("start_showing", (time))
        if self._event_manager is not None:
            self._log_write_if(self.log_warn, "start_showing() was called although the RSVP was registered to an event manager")

        self._start_showing_time = time
        self.update_rsvp(time)


    #----------------------------------------------------
    def update_rsvp(self, time):
        """
        *When working without events:* set relevant stimuli as visible/invisible.

        :param time: The time in the current session/trial. This must be synchronized with the "time"
                     argument of :func:`~trajtracker.stimuli.RSVPText.start_showing`
        """

        while (len(self._show_hide_operations) > 0 and
               time >= self._start_showing_time + self._show_hide_operations[0][0]):

            operation = self._show_hide_operations.pop(0)
            stim_num = operation[2]
            visible = operation[1]

            if self._should_log(self.log_trace):
                self._log_write("{:} stimulus #{:} ({:})".format(
                    "showing" if visible else "hiding", stim_num, self._text[stim_num]))
            self._stimuli[stim_num].visible = visible


    #==============================================================================
    #   Configure properties of Expyriment's TextBox
    #==============================================================================

    #-----------------------------------------------------------------
    @property
    def text(self):
        return self._text

    @text.setter
    @fromXML(_u.parse_scalar_or_list(str))
    def text(self, value):
        self._set_property("text", value, str, allow_single_value=False)
        self._log_property_changed("text")

    #-----------------------------------------------------------------
    @property
    def text_font(self):
        return self._text_font

    @text_font.setter
    @fromXML(_u.parse_scalar_or_list(str))
    def text_font(self, value):
        self._set_property("text_font", value, str)
        self._log_property_changed("text_font")

    #-----------------------------------------------------------------
    @property
    def text_size(self):
        return self._text_size

    @text_size.setter
    @fromXML(_u.parse_scalar_or_list(int))
    def text_size(self, value):
        self._set_property("text_size", value, int)
        self._log_property_changed("text_size")

    #-----------------------------------------------------------------
    @property
    def text_bold(self):
        return self._text_bold

    @text_bold.setter
    @fromXML(_u.parse_scalar_or_list(bool))
    def text_bold(self, value):
        self._set_property("text_bold", value, bool, allow_none=False)
        self._log_property_changed("text_bold")

    #-----------------------------------------------------------------
    @property
    def text_italic(self):
        return self._text_italic

    @text_italic.setter
    @fromXML(_u.parse_scalar_or_list(bool))
    def text_italic(self, value):
        self._set_property("text_italic", value, bool, allow_none=False)
        self._log_property_changed("text_italic")

    #-----------------------------------------------------------------
    @property
    def text_underline(self):
        return self._text_underline

    @text_underline.setter
    @fromXML(_u.parse_scalar_or_list(bool))
    def text_underline(self, value):
        self._set_property("text_underline", value, bool, allow_none=False)
        self._log_property_changed("text_underline")

    #-----------------------------------------------------------------
    @property
    def text_justification(self):
        return self._text_justification

    @text_justification.setter
    def text_justification(self, value):
        self._set_property("text_justification", value, str)
        self._log_property_changed("text_justification")

    #-----------------------------------------------------------------
    @property
    def text_colour(self):
        return self._text_colour

    @text_colour.setter
    @fromXML(_u.parse_scalar_or_list(_u.parse_rgb))
    def text_colour(self, value):
        self._set_property("text_colour", value, "RGB")
        self._log_property_changed("text_colour")

    #-----------------------------------------------------------------
    @property
    def background_colour(self):
        return self._background_colour

    @background_colour.setter
    @fromXML(_u.parse_scalar_or_list(_u.parse_rgb))
    def background_colour(self, value):
        self._set_property("background_colour", value, "RGB")
        self._log_property_changed("background_colour")

    #-----------------------------------------------------------------
    @property
    def size(self):
        return self._size

    @size.setter
    @fromXML(_u.parse_scalar_or_list(int))
    def size(self, value):
        self._set_property("size", value, "coord")
        self._log_property_changed("size")

    #-----------------------------------------------------------------
    @property
    def position(self):
        return self._position

    @position.setter
    @fromXML(_u.parse_scalar_or_list(int))
    def position(self, value):
        self._set_property("position", value, "coord")
        self._log_property_changed("position")


    #-----------------------------------------------------------------
    def _update_stimuli(self, prop_name, value):

        if multiple_values:
            value_per_stim = value
        else:
            value_per_stim = [value] * len(self._stimuli)

        for i in range(len(self._stimuli)):
            setattr(self._stimuli[i], prop_name, value_per_stim[i])



#=====================================================================
class TextboxEnablerDisabler(object):

    def __init__(self, stimulus, visible, stimulus_num):
        self._stimulus = stimulus
        self._visible = visible
        self._stimulus_num = stimulus_num

    def __call__(self, *args, **kwargs):
        self._stimulus.visible = self._visible

    def __str__(self):
        return "RSVP #{:} ({:})".format(self._stimulus_num, self._stimulus.text)
