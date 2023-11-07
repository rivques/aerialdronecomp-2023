from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, WaitAction
import logging
logging.basicConfig(level=logging.DEBUG)

drone_manager = DroneManager(drone_type=DroneType.REAL, show_error_graph=True)
SequentialAction(drone_manager, [TakeoffAction()]).run_sequence()
while True:
    SequentialAction(drone_manager, [WaitAction(100)], ErrorHandlingStrategy.LAND).run_sequence()