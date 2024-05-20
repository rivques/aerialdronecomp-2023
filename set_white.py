from utils.drone_manager import DroneManager, DroneType
from codrone_edu.drone import Drone
from utils.basic_actions import ReadColorAndSetLEDAction, SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, WaitAction
import utils.field_locations as fl
import logging
logging.basicConfig(level=logging.INFO)
if __name__ == "__main__":
    drone = Drone()
    drone.pair()
    drone.set_drone_LED(255,255,255,255)
    drone.reset_sensor()