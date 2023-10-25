from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy
import logging
logging.basicConfig(level=logging.DEBUG)

AXIS_TO_TUNE = 0

disabled_control_axes = [False, False, False, False]
disabled_control_axes[AXIS_TO_TUNE] = True
drone_manager = DroneManager(drone_type=DroneType.REAL, show_error_graph=True, disabled_control_axes=disabled_control_axes)
SequentialAction(drone_manager, [TakeoffAction]).run_sequence()
while True:
    start_loc = [0, 0, 0.5]
    end_loc = [0, 0, 0.5]
    start_loc[AXIS_TO_TUNE] = 1
    SequentialAction(drone_manager, [GoToAction(*start_loc), GoToAction(*end_loc)], ErrorHandlingStrategy.LAND).run_sequence()