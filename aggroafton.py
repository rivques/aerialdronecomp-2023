import time
start_time = time.time()
from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import ArbitraryCodeAction, EmergencyStopAction, FastTakeoffAction, ReadColorAndSetLEDAction, SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, WaitAction
import logging
logging.basicConfig(level=logging.INFO)
import utils.field_locations as fl

CHEESE_FRONT_POS = [0.2,0, fl.yellow_keyhole[2]]
CHEESE_BACK_POS = [fl.yellow_keyhole[0], fl.yellow_keyhole[1], fl.yellow_keyhole[2]]
HALF_CYCLE_TIMEOUT=3
Y_DRIFT_PER_CYCLE = 0
X_DRIFT_PER_CYCLE = -0.02

cycle_times = []
current_y_drift = 0
current_x_drift = 0

if __name__ == "__main__":
    drone_manager = DroneManager(drone_type=DroneType.REAL, show_error_graph=False, calibrate_sensors=False)

    first_color = ""
    def set_first_color(dm: DroneManager): # this is a bit ugly, but it works
        global first_color
        first_color = dm.last_color

    # get to cheesing position
    SequentialAction(drone_manager, [
        ReadColorAndSetLEDAction(),
        ArbitraryCodeAction(set_first_color),
        TakeoffAction(),
        GoToAction(CHEESE_FRONT_POS[0], CHEESE_FRONT_POS[1], CHEESE_FRONT_POS[2], "TakeoffAltAction", 3),
        #FastTakeoffAction(CHEESE_FRONT_POS[2], 4),
        # GoToAction(0, 0, fl.red_arch[2], "ArchPrepareAlt", 5), # get to good altitude for arch
        # #WaitAction(1), # settle a bit
        # GoToAction(fl.in_to_m(48), fl.yellow_keyhole[1], None, "GoThroughArch", 2), # go through arch and align for keyhole on xy plane
        # GoToAction(None, None, fl.yellow_keyhole[2],"YKeyholePrepareHeight", 5), #  get to right height for keyhole
        # #WaitAction(1), # settle a bit
        # GoToAction(fl.green_keyhole[0], None, None,"GoThroughYKeyhole", 2), # go through keyhole and align for next keyhole
        WaitAction(1), # settle a bit
    ], ErrorHandlingStrategy.LAND).run_sequence()
    cheese_counter = 1
    # cheese first front to back
    SequentialAction(drone_manager, [
        GoToAction(CHEESE_BACK_POS[0], CHEESE_BACK_POS[1], CHEESE_BACK_POS[2], "CheeseToBack0", HALF_CYCLE_TIMEOUT),
    ], ErrorHandlingStrategy.LAND).run_sequence()
    # cheese until time runs out
    cycle_times.append(time.time() - start_time)
    try:
        while True:
            SequentialAction(drone_manager, [
                GoToAction(CHEESE_FRONT_POS[0] + X_DRIFT_PER_CYCLE * cheese_counter, CHEESE_FRONT_POS[1] - Y_DRIFT_PER_CYCLE * cheese_counter, CHEESE_FRONT_POS[2], "CheeseToFront"+str(cheese_counter), HALF_CYCLE_TIMEOUT),
                GoToAction(CHEESE_BACK_POS[0] + X_DRIFT_PER_CYCLE * cheese_counter, CHEESE_BACK_POS[1]- Y_DRIFT_PER_CYCLE * cheese_counter, CHEESE_BACK_POS[2], "CheeseToBack"+str(cheese_counter), HALF_CYCLE_TIMEOUT),
            ], ErrorHandlingStrategy.LAND).run_sequence()
            cheese_counter += 1
            cycle_times.append(time.time() - start_time)
        logging.info(f"choosing to land with {TOTAL_TIME - (time.time() - start_time):.3f} seconds left")
        # land
    finally:
        logging.info(f"front to front: {cheese_counter-1}")
        logging.info(f"cycle times: {cycle_times}")
        logging.info(f"avg cycle time: {sum([cycle_times[i+1] - cycle_times[i] for i in range(len(cycle_times)-1)])/(len(cycle_times)-1):.2f}")