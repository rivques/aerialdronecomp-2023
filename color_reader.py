from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, WaitAction
import logging
import time
logging.basicConfig(level=logging.DEBUG)

drone_manager = DroneManager(drone_type=DroneType.REAL, show_error_graph=False)
while True:
    try:
        colors = drone_manager.get_colors()
    except TypeError:
        pass
    else:
        print(colors)
    time.sleep(0.5)