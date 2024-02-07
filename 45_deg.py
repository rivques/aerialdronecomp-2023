from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, WaitAction, RotateAction
import logging
logging.basicConfig(level=logging.DEBUG)
if __name__ == "__main__":
    drone_manager = DroneManager(drone_type=DroneType.REAL, show_error_graph=False)
    # wait for signal to take off
    input("Drone ready, press enter to start!")
    drone_manager.ignore_next_loop_warning()

    SequentialAction(drone_manager, [
        TakeoffAction(),
        GoToAction(1, 0, None),
        RotateAction(45),
        GoToAction(2, -1, None),
        WaitAction(2),
        LandAction()
    ], ErrorHandlingStrategy.LAND).run_sequence()