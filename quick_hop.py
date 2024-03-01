from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import SequentialAction, FastTakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, EmergencyStopAction
import logging, time
import utils.field_locations as fl
logging.basicConfig(level=logging.INFO)
if __name__ == "__main__":
    drone_manager = DroneManager(drone_type=DroneType.REAL, show_error_graph=False)
    start_time = time.time()
    landing_loc = fl.blue_landing_pad
    SequentialAction(drone_manager, [
            FastTakeoffAction(0.25),
            GoToAction(landing_loc[0], landing_loc[1], None, "GoToLanding", 4),
            EmergencyStopAction(),
            EmergencyStopAction(),
            EmergencyStopAction(),
            EmergencyStopAction()
        ], ErrorHandlingStrategy.LAND).run_sequence()
    logging.info(f"Time taken: {time.time() - start_time}")