import time
start_time = time.time()
from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import ArbitraryCodeAction, EmergencyStopAction, FastTakeoffAction, ReadColorAndSetLEDAction, SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, WaitAction
import logging
logging.basicConfig(level=logging.INFO)
import utils.field_locations as fl

CHEESE_FRONT_POS = [fl.green_keyhole[0], fl.green_keyhole[1]-0.40, fl.green_keyhole[2]-0.1]
CHEESE_BACK_POS = [fl.green_keyhole[0], fl.blue_arch[1]+0.2, fl.green_keyhole[2]-0.1]
TIME_PER_FULL_CYCLE = 6
TIME_NEEDED_POST_CHEESE = 8
TOTAL_TIME = 60
HALF_CYCLE_TIMEOUT = 3
Y_DRIFT_PER_CYCLE = 0.1

cycle_times = []
current_y_drift = 0

if __name__ == "__main__":
    drone_manager = DroneManager(drone_type=DroneType.REAL, show_error_graph=True, calibrate_sensors=False)

    first_color = ""
    def set_first_color(dm: DroneManager): # this is a bit ugly, but it works
        global first_color
        first_color = dm.last_color

    # get to cheesing position
    SequentialAction(drone_manager, [
        ReadColorAndSetLEDAction(),
        ArbitraryCodeAction(set_first_color),
        FastTakeoffAction(fl.red_arch[2]),
        GoToAction(0, 0, fl.red_arch[2], "ArchPrepareAlt", 5), # get to good altitude for arch
        #WaitAction(1), # settle a bit
        GoToAction(fl.in_to_m(48), fl.yellow_keyhole[1], None, "GoThroughArch", 2), # go through arch and align for keyhole on xy plane
        GoToAction(None, None, fl.yellow_keyhole[2],"YKeyholePrepareHeight", 5), #  get to right height for keyhole
        #WaitAction(1), # settle a bit
        GoToAction(fl.green_keyhole[0], None, None,"GoThroughYKeyhole", 2), # go through keyhole and align for next keyhole
        WaitAction(2), # settle a bit
    ], ErrorHandlingStrategy.LAND).run_sequence()
    cheese_counter = 1
    # cheese first front to back
    SequentialAction(drone_manager, [
        GoToAction(CHEESE_BACK_POS[0], CHEESE_BACK_POS[1], CHEESE_BACK_POS[2], "CheeseToBack0", HALF_CYCLE_TIMEOUT),
    ], ErrorHandlingStrategy.LAND).run_sequence()
    # cheese until time runs out
    cycle_times.append(time.time() - start_time)
    try:
        while time.time() - start_time < TOTAL_TIME - TIME_NEEDED_POST_CHEESE - TIME_PER_FULL_CYCLE:
            SequentialAction(drone_manager, [
                GoToAction(CHEESE_FRONT_POS[0], CHEESE_FRONT_POS[1] - Y_DRIFT_PER_CYCLE * cheese_counter, CHEESE_FRONT_POS[2], "CheeseToFront"+str(cheese_counter), HALF_CYCLE_TIMEOUT),
                GoToAction(CHEESE_BACK_POS[0], CHEESE_BACK_POS[1]- Y_DRIFT_PER_CYCLE * cheese_counter, CHEESE_BACK_POS[2], "CheeseToBack"+str(cheese_counter), HALF_CYCLE_TIMEOUT),
            ], ErrorHandlingStrategy.LAND).run_sequence()
            cheese_counter += 1
            cycle_times.append(time.time() - start_time)
        logging.info(f"choosing to land with {TOTAL_TIME - (time.time() - start_time):.3f} seconds left")
        # land
    finally:
        logging.info(f"front to front: {cheese_counter-1}")
        logging.info(f"cycle times: {cycle_times}")
        logging.info(f"avg cycle time: {sum([cycle_times[i+1] - cycle_times[i] for i in range(len(cycle_times)-1)])/(len(cycle_times)-1):.2f}")
    SequentialAction(drone_manager, [
        GoToAction(fl.mat_2[0], fl.mat_2[1]- Y_DRIFT_PER_CYCLE/2 * cheese_counter, 0.5, "GoLand",2), # go through blue arch 
        #WaitAction(1), # settle a bit
        LandAction(),
        ReadColorAndSetLEDAction(),
    ], ErrorHandlingStrategy.LAND).run_sequence()

    logging.info(f"First color: {first_color}")
    if first_color == drone_manager.last_color:
        logging.warning(f"Drone did not change color, something went wrong!")
        # take a guess at one of the colors that's not the first color
        if first_color == "Blue":
            logging.info("Guessing red landing pad")
            landing_loc = fl.red_landing_pad
            drone_manager.raw_drone.set_drone_LED(255, 0, 0, 255)
        elif first_color == "Red":
            logging.info("Guessing green landing pad")
            landing_loc = fl.green_landing_pad
            drone_manager.raw_drone.set_drone_LED(0, 255, 0, 255)
        else:
            logging.info("Guessing blue landing pad")
            landing_loc = fl.blue_landing_pad
            drone_manager.raw_drone.set_drone_LED(0, 0, 255, 255)
    else:
        if drone_manager.last_color == "Blue":
            landing_loc = fl.blue_landing_pad
        elif drone_manager.last_color == "Red":
            landing_loc = fl.red_landing_pad
        else:
            landing_loc = fl.green_landing_pad

    # hop
    SequentialAction(drone_manager, [
            FastTakeoffAction(0.25, 3),
            GoToAction(landing_loc[0], landing_loc[1], None, "GoToLanding", 4),
            EmergencyStopAction(),
            EmergencyStopAction(),
            EmergencyStopAction(),
            EmergencyStopAction()
        ], ErrorHandlingStrategy.LAND).run_sequence()
    logging.info(f"Time taken: {time.time() - start_time}")