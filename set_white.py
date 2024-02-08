from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import ReadColorAndSetLEDAction, SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, WaitAction
import utils.field_locations as fl
import logging
logging.basicConfig(level=logging.INFO)
if __name__ == "__main__":
    drone_manager = DroneManager(drone_type=DroneType.REAL, show_error_graph=False)
    drone_manager.raw_drone.set_drone_LED(255,255,255,255)