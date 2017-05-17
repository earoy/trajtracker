.. TrajTracker documentation master file, created by
   sphinx-quickstart on Mon Feb 20 15:35:23 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

TrajTracker documentation
=========================

Expyriment-based tools for psychology experiments, focusing on finger/mouse tracking


General
-------

.. toctree::
   :maxdepth: 1
   :glob:

   TrajTracker general functions <trajtracker>
   Environment
   General utilities <utils>




trajtracker.stimuli
-------------------

Visual objects.

.. toctree::
   :maxdepth: 1
   :glob:

   MultiStimulus: controls the presentation of a sequence of stimuli <stimuli/MultiStimulus>
   MultiTextBox: controls the presentation of a sequence of texts <stimuli/MultiTextBox>
   NumberLine: show a number line, detect when it's touched <stimuli/NumberLine>
   StimulusContainer: present several stimuli, easily toggle them on/off <stimuli/StimulusContainer>
   StimulusSelector: create a "virtual stimulus" that can present one of several underlying stimuli <stimuli/StimulusSelector>

trajtracker.validators
----------------------

Perform various validations on mouse/finger movement during the trial.

.. toctree::
   :maxdepth: 1
   :glob:

   GlobalSpeedValidator: enforce minimal speed by defining milestones <validators/GlobalSpeedValidator>
   InstantaneousSpeedValidator: enforce minimal/maximal momentary speed <validators/InstantaneousSpeedValidator>
   LocationsValidator: allow touching only predefined screen locations <validators/LocationsValidator>
   MoveByGradientValidator: restrict movement to predefined paths <validators/MoveByGradientValidator>
   MovementAngleValidator: restrict movement direction <validators/MovementAngleValidator>
   NCurvesValidator: prevent "zigzag" movement <validators/NCurvesValidator>

trajtracker.movement
--------------------

Classes that handle various aspects of finger/mouse movement.


**Animate a visual object along a given path:**

.. toctree::
   :maxdepth: 1
   :glob:

   StimulusAnimator: move a stimulus along a path defined by a trajectory-generator <movement/StimulusAnimator>
   CircularTrajectoryGenerator: define a circular movement path <movement/CircularTrajectoryGenerator>
   CustomTrajectoryGenerator: load movement path from CSV <movement/CustomTrajectoryGenerator>
   LineTrajectoryGenerator: define a straight movement path <movement/LineTrajectoryGenerator>
   SegmentedTrajectoryGenerator: define a multi-segment movement path <movement/SegmentedTrajectoryGenerator>


**Monitor the finger/mouse movement:**

.. toctree::
   :maxdepth: 1
   :glob:

   DirectionMonitor: track the movement direction <movement/DirectionMonitor>
   Hotspot: detect touching certain screen locations <movement/Hotspot>
   SpeedMonitor: track the movement speed <movement/SpeedMonitor>
   StartPoint: initiate a trial <movement/StartPoint>
   RectStartPoint: a rectangle for initiating a trial <movement/RectStartPoint>
   TrajectoryTracker: track & save the movement trajectory <movement/TrajectoryTracker>


trajtracker.events
------------------

This set of classes allows defining the flow of a trial by using events.

.. toctree::
   :maxdepth: 1
   :glob:

   Overview of the events mechanism <events/events_overview>
   events/Event
   events/EventManager


trajtracker.io
--------------

.. toctree::
   :maxdepth: 1
   :glob:

   io/*


trajtracker.misc
----------------

.. toctree::
   :maxdepth: 1
   :glob:

   misc/*



Off-the-shelf paradigms
=======================

TrajTracker also offers ready-to-use experimental paradigms: sets of functions that allow
creating your own experiment with almost no programming:

**Number-to-position mapping experiments**

For an overview of this paradigm under TrajTracker, see
`here <https://drordotan.wixsite.com/trajtracker/ttrk-exp-num2pos>`_.

.. toctree::
   :maxdepth: 1
   :glob:

   Overview <paradigms/num2pos/num2pos>
   Configuration: the Config class <paradigms/num2pos/Config>
   Configuration: input CSV file format <paradigms/num2pos/input_data_format>
   The result files <paradigms/num2pos/results>
   Technical: the software design <paradigms/num2pos/num2pos_design>
   Technical: the ExperimentInfo class <paradigms/num2pos/ExperimentInfo>
   Technical: the TrialInfo class <paradigms/num2pos/TrialInfo>


**Dual-choice experiments**


Coming up soon


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

