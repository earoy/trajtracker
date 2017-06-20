"""

A simple version of the number-to-position experiment:
- 0-100 number line
- Each target appears twice

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy
import trajtracker as ttrk
from trajtracker.paradigms import num2pos


if not xpy.misc.is_android_running():
    xpy.control.defaults.window_mode = True
    ttrk.log_to_console = True


config = num2pos.Config("Num2Pos(0-100*2)", max_trial_duration=2, max_numberline_value=100,
                        speed_guide_enabled=True, data_source=range(101) * 2,
                        sounds_dir="../sounds")


#-- Initialize Expyriment

exp = ttrk.initialize()
xpy.control.start(exp)

if not xpy.misc.is_android_running():
    exp.mouse.show_cursor()

#-- Get subject info
(subj_id, subj_name) = ttrk.paradigms.common.get_subject_name_id()

#-- Run the experiment
num2pos.run_full_experiment(config, exp, subj_id, subj_name)

#-- Shutdown Expyriment
xpy.control.end()
