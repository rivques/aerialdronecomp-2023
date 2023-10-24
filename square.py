from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy
import logging
logging.basicConfig(level=logging.DEBUG)

drone_manager = DroneManager(drone_type=DroneType.REAL)

SequentialAction(drone_manager, [
    TakeoffAction(),
    GoToAction(0.5, 0, None),
    GoToAction(0.5, 0.5, None),
    GoToAction(0, 0.5, None),
    GoToAction(0, 0, None),
    LandAction()
], ErrorHandlingStrategy.LAND).run_sequence()