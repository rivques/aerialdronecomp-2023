from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, WaitAction
import logging, time
import utils.field_locations as fl
logging.basicConfig(level=logging.DEBUG)
if __name__ == "__main__":
    drone_manager = DroneManager(drone_type=DroneType.REAL, show_error_graph=False)
    start_time = time.time()
    landing_loc = fl.blue_landing_pad
    SequentialAction(drone_manager, [
            TakeoffAction(),
            GoToAction(landing_loc[0], landing_loc[1], None, "GoToLanding", 4),
            LandAction()
        ], ErrorHandlingStrategy.LAND).run_sequence()
    logging.info(f"Time taken: {time.time() - start_time}")