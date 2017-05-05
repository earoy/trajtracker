
Number-to-position mapping experiments
======================================

For general details about this paradigm (general information, supported features, format of results, etc.),
see `this page <https://drordotan.wixsite.com/trajtracker/supported-paradigms>`_.

Example scripts are provided as part of the TrajTracker distribution, under *samples/paradigms/number_to_position_...*

You can create your own number-to-position experiment in two ways:

* For most common features, you will only have to change the program configuration.

* If your experiment requires features that are not directly supported by the configuration offered,
  you can change the python code. To help you in that, see below the documentation of the functions
  that implement the number-to-position experiment.


Use common features by setting configuration
--------------------------------------------

Several features are already supported by the paradigm we wrote. These features can be used
with almost no programming. To use them, you should:

- Create your main program by copy one of the existing sample scripts (the simplest one is in
  *samples/paradigms/number_to_position_1* in the TrajTracker distribution).
- In your script, set the experiment's general configuration parameters.
  This is done by updating the :class:`~trajtracker.paradigms.num2pos.Config` object.
- Create a CSV file with the per-trial data. See :doc:`here <input_data_format>`
  a detailed description of this file format.


Make advanced changes by modifying the code
-------------------------------------------

If your experiment requires features that are not supported via the above configuration, you can modify
the relevant python functions. To help you on this, we describe below how the experiment
software is designed.

The simplest way to do such modifications is to copy the relevant functions into your own script
(e.g., see the script in *samples/paradigms/number_to_position_2* in the TrajTracker distribution).

*TBD overview, how-to, list of functions, events, internal data structures*
