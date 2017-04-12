"""
Functions to support the number-to-position paradigm

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import time
from numbers import Number
from operator import itemgetter

import expyriment as xpy

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u

from trajtracker.paradigms import num2pos

#----------------------------------------------------------------
def create_experiment_objects(exp_info, config):
    """
    Create the full default configuration for the experiment.

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type config: trajtracker.paradigms.num2pos.Config
    """

    create_numberline(exp_info, config)
    create_start_point(exp_info, config)
    create_textbox_target(exp_info)
    create_errmsg_textbox(exp_info)
    create_validators(exp_info, direction_validator=True, global_speed_validator=True,
                      inst_speed_validator=True, zigzag_validator=True, config=config)
    create_sounds(exp_info, config)

    exp_info.trials = load_data_file(config)

    #-- Initialize experiment-level data

    exp_info.exp_data['WindowWidth'] = exp_info.screen_size[0]
    exp_info.exp_data['WindowHeight'] = exp_info.screen_size[1]
    exp_info.exp_data['nExpectedTrials'] = len(exp_info.trals)
    exp_info.exp_data['nExpectedGoodTrials'] = len(exp_info.trals)
    exp_info.exp_data['nTrialsCompleted'] = 0
    exp_info.exp_data['nTrialsFailed'] = 0
    exp_info.exp_data['nTrialsSucceeded'] = 0


#----------------------------------------------------------------
def create_numberline(exp_info, config):
    """
    Create a :class:`~trajtracker.stimuli.NumberLine` object with default configuration

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type config: trajtracker.paradigms.num2pos.Config
    """

    _u.validate_func_arg_type(None, "create_numberline", "max_value", config.max_numberline_value, Number)

    numberline = ttrk.stimuli.NumberLine(
        position=(0, screen_size[1] / 2 - 80),
        line_length=int(screen_size[0] * 0.85),
        min_value=0,
        max_value=max_value)

    # -- Graphical properties of the number line
    numberline.position = screen_size[1] / 2 - 80
    numberline.line_length = screen_size[0] * 0.85
    numberline.line_width = 2
    numberline.end_tick_height = 5
    numberline.line_colour = xpy.misc.constants.C_WHITE

    # -- The labels at the end of the line
    numberline.labels_visible = True
    numberline.labels_font_name = "Arial"
    numberline.labels_font_size = 26
    numberline.labels_font_colour = xpy.misc.constants.C_GREY
    numberline.labels_box_size = (100, 30)
    numberline.labels_offset = (0, 20)

    exp_info.numberline = numberline

    #-- Feedback arrow/line

    numberline.feedback_stim_hide_event = ttrk.paradigms.num2pos.FINGER_STARTED_MOVING

    if config.nl_feedback_type == num2pos.FeedbackType.Arrow:
        numberline.feedback_stim = num2pos.FeedbackArrow()
    elif config.nl_feedback_type == num2pos.FeedbackType.Line:
        numberline.feedback_stim = xpy.stimuli.Line(start_point=(0, 0), end_point=(0, 20), line_width=2,
                                                    colour=xpy.misc.constants.C_WHITE)

    if config.nl_feedback_type != num2pos.FeedbackType.none:
        exp_info.stimuli.add("feedback", numberline.feedback_stim, False)

#----------------------------------------------------------------
def create_start_point(exp_info, config):
    """
    Create the "start" area, with default configuration

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type config: trajtracker.paradigms.num2pos.Config
    """

    #todo: create a control that takes care of everything, and can also tilt

    start_area = xpy.stimuli.Rectangle(size=(40, 30))
    start_area.position = (0, - (screen_size[1] / 2 - start_area.size[1] / 2))

    exp_info.start_point = StartPoint(start_area)

    exp_info.exp_data['TrajZeroCoordX'] = None  # todo
    exp_info.exp_data['TrajZeroCoordY'] = None
    exp_info.exp_data['TrajPixelsPerUnit'] = 1


#----------------------------------------------------------------
def create_traj_tracker(exp_info, config):
    """
    Create the object that tracks the trajectory
    
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type config: trajtracker.paradigms.num2pos.Config
    """

    if not config.save_results:
        return

    curr_time = time.strftime("%Y-%m-%d_%H-%M", time.localtime())
    exp_info.trials_out_filename = "trials_{:}_{:}.csv".format(exp_info.xpy_exp.subject, curr_time)
    exp_info.traj_out_filename = "trajectory_{:}_{:}.csv".format(exp_info.xpy_exp.subject, curr_time)

    traj_file_path = xpy.io.defaults.datafile_directory + "/" + exp_info.traj_out_filename
    exp_info.trajtracker = ttrk.movement.TrajectoryTracker(traj_file_path)


#----------------------------------------------------------------
def create_validators(exp_info, direction_validator, global_speed_validator, inst_speed_validator, zigzag_validator,
                      config):
    """
    Create movement validators, with default configuration.

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo

    :param direction_validator: Whether to include the validator that enforces upward-only movement
    :type direction_validator: bool

    :param global_speed_validator: Whether to validate that the finger reaches each y coordinate in time
    :type global_speed_validator: bool

    :param inst_speed_validator: Whether to validate the finger's instantaneous speed
    :type inst_speed_validator: bool

    :param zigzag_validator: Whether to prohibit zigzag movement
    :type zigzag_validator: bool

    :type config: trajtracker.paradigms.num2pos.Config

    :return: tuple: (list_of_validators, dict_of_validators)
    """

    _u.validate_func_arg_type(None, "create_validators", "direction_validator", direction_validator, bool)
    _u.validate_func_arg_type(None, "create_validators", "global_speed_validator", global_speed_validator, bool)
    _u.validate_func_arg_type(None, "create_validators", "speed_guide_enabled", speed_guide_enabled, bool)
    _u.validate_func_arg_type(None, "create_validators", "inst_speed_validator", inst_speed_validator, bool)
    _u.validate_func_arg_type(None, "create_validators", "config", config, ttrk.paradigms.num2pos.Config)


    if direction_validator:
        v = ttrk.validators.MovementAngleValidator(
            min_angle=-90,
            max_angle=90,
            calc_angle_interval=20,
            enabled=True)
        exp_info.add_validator(v, 'direction')


    if global_speed_validator:
        v = ttrk.validators.GlobalSpeedValidator(
            origin_coord=exp_info.start_area.position[1] + self.start_area.size[1] / 2,
            end_coord=exp_info.numberline.position[1],
            grace_period=config.grace_period,
            max_trial_duration=config.max_trial_duration,
            milestones=[(.5, .33), (.5, .67)],
            show_guide=config.speed_guide_enabled)
        v.do_present_guide = False
        exp_info.add_validator(v, 'global_speed')
    #todo: global_speed_validator.finger_started_moving() should be called. Do this with an event.


    if inst_speed_validator:
        v = ttrk.validators.InstantaneousSpeedValidator(
            min_speed=config.min_inst_speed,
            grace_period=config.grace_period,
            calculation_interval=0.05)
        exp_info.add_validator(v, 'inst_speed')


    if zigzag_validator:
        v = ttrk.validators.NCurvesValidator(max_curves_per_trial=config.max_zigzags)
        exp_info.add_validator(v, 'zigzag')


#----------------------------------------------------------------
def create_textbox_target(exp_info):
    """
    Create a textbox to serve as the target. This text box supports multiple texts (so it can be used
    for RSVP, priming, etc.)

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    target = ttrk.stimuli.MultiTextBox()

    target.text_font = "Arial"
    target.position = (0, screen_size[1] / 2 - 50)
    target.size = (300, 80)
    target.text_size = 50
    target.text_colour = xpy.misc.constants.C_WHITE

    target.onset_event = TRIAL_STARTED if stimulus_then_move else ttrk.paradigms.num2pos.FINGER_STARTED_MOVING

    exp_info.set_target(targe, target.stimulus)


#todo: support image target?


#----------------------------------------------------------------
def create_errmsg_textbox(exp_info):
    """
    Create a stimulus that can show the error messages

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    exp_info.errmsg_box = xpy.stimuli.TextBox(
        text="", size=(290, 180), position=(0, 0),
        text_font="Arial", text_size=16, text_colour=xpy.misc.constants.C_RED)


#----------------------------------------------------------------
def register_to_event_manager(exp_info):
    """
    Register all relevant objects to the event manager

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    exp_info.event_manager.register(exp_info.start_point)
    exp_info.event_manager.register(exp_info.target)


#------------------------------------------------
def create_sounds(exp_info, config):
    """
    Load the sounds for the experiment
    
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type config: trajtracker.paradigms.num2pos.Config
    """

    exp_info.sounds['error'] = load_sound('error.wav')

    if config.sound_by_accuracy is None:
        # One sound, independently of accuracy
        exp_info.sounds_ok = [load_sound('click.wav')]
        exp_info.sounds_ok_max_ep_err = [1]
        return

    #-- Validate configuration
    _u.validate_attr_is_collection(config, "sound_by_accuracy", config.sound_by_accuracy, 1, allow_set=True)
    for sound_cfg in config.sound_by_accuracy:
        _u.validate_attr_is_collection(config, "sound_by_accuracy[*]", sound_cfg, 2, 2)
        _u.validate_attr_numeric(config, "sound_by_accuracy[*]", sound_cfg[0])
        if not (0 < sound_cfg[0] <= 1):
            raise ValueError("trajtracker error: invalid accuracy level ({:}) in config.sound_by_accuracy".format(
                sound_cfg[0]))
        _u.validate_attr_type(config, "sound_by_accuracy[*]", sound_cfg[0], str)

    #-- Load sounds and save configuration

    cfg = list(config.sound_by_accuracy)
    cfg.sort(key=itemgetter(0))
    cfg[-1][0] = 1

    exp_info.sounds_ok = [load_sound(x[1]) for x in cfg]
    exp_info.sounds_ok_max_ep_err = np.array([x[0] for x in cfg])


#------------------------------------------------
def load_sound(filename):
    sound = xpy.stimuli.Audio("sounds/" + filename)
    sound.preload()
    return sound
