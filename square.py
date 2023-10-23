from utils.drone_manager import DroneManager
from utils.basic_actions import SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy

drone_manager = DroneManager()

SequentialAction(drone_manager, [], ErrorHandlingStrategy.LAND).run_sequence()