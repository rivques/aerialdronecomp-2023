from utils.drone_manager import DroneManager
from utils.basic_actions import SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy

drone_manager = DroneManager()

SequentialAction(drone_manager, [
    TakeoffAction(),
    GoToAction(0.5, 0),
    GoToAction(0.5, 0.5),
    GoToAction(0, 0.5),
    GoToAction(0, 0),
    LandAction()
], ErrorHandlingStrategy.LAND).run_sequence()