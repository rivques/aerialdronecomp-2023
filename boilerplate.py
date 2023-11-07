from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, WaitAction
import logging
logging.basicConfig(level=logging.DEBUG)
if __name__ == "__main__":
    drone_manager = DroneManager(drone_type=DroneType.REAL, show_error_graph=False)

    SequentialAction(drone_manager, [

    ], ErrorHandlingStrategy.LAND).run_sequence()