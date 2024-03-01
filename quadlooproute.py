from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import ReadColorAndSetLEDAction, SequentialAction, TakeoffAction, FastTakeoffAction, EmergencyStopAction, GoToAction, LandAction, ErrorHandlingStrategy, ArbitraryCodeAction
import utils.field_locations as fl
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

# goal: 175 points
# doubleloop benchmarks to beat:
# total time 50 seconds
# double loop 20 seconds
# "Landing" 10 seconds

if __name__ == "__main__":
    drone_manager = DroneManager(drone_type=DroneType.REAL, show_error_graph=False,  calibrate_sensors=False)

    # wait for signal to take off
    # input("Drone ready, press enter to start!")
    drone_manager.ignore_next_loop_warning()

    first_color = ""
    def set_first_color(dm: DroneManager): # this is a bit ugly, but it works
        global first_color
        first_color = dm.last_color
    greenovershootoffset = 0.25
    SequentialAction(drone_manager, [
        ReadColorAndSetLEDAction(),
        ArbitraryCodeAction(set_first_color),
        #FastTakeoffAction(0.25, 0.5),
        TakeoffAction(),
        #GoToAction(0, 0, fl.yellow_keyhole[2]-fl.in_to_m(5), "ArchPrepareAlt", 4), # get to good altitude for arch
        #WaitAction(1), # settle a bit
        #GoToAction(fl.in_to_m(48), fl.yellow_keyhole[1]-0.1, None, "GoThroughArch", 2), # go through arch and align for keyhole on xy plane
        # ------ BEGIN LOOPS 1 AND 2 ------
        #GoToAction(fl.in_to_m(48), fl.yellow_keyhole[1], fl.yellow_keyhole[2]-fl.in_to_m(0),"YKeyholePrepareHeight", 3), #  get to right height for keyhole
        #WaitAction(1), # settle a bit
        GoToAction(fl.yellow_keyhole[0]+fl.in_to_m(10), None, fl.yellow_keyhole[2]-fl.in_to_m(5),"GoThroughYKeyhole", 2), # go through keyhole and align for next keyhole
        GoToAction(fl.in_to_m(49), fl.yellow_keyhole[1]+0.5, fl.yellow_keyhole[2]-fl.keyhole_outer_dia*0.7, "YKeyholeLoopDown", 3), #  get above yellow keyhole 
        GoToAction(fl.in_to_m(48), 0, fl.yellow_keyhole[2]-fl.in_to_m(5),"YKeyholeLoopUp", 3), #  get to right height for keyhole
        GoToAction(fl.green_keyhole[0]-greenovershootoffset,None, None, "YKeyholeLoopThrough", 2), # go through keyhole and align for next keyhole
        GoToAction(None, fl.green_keyhole[1]-0.30, fl.green_keyhole[2],"GKeyholePrepareHeight",4), # get to correct height for yellow keyhole and get a bit closer
        #WaitAction(1), # settle a bit
        GoToAction(None, fl.green_keyhole[1]+0.20, None, "GoThroughGKeyhole",2),
        GoToAction(fl.green_keyhole[0]-0.6-greenovershootoffset, fl.green_keyhole[1]-0.3, fl.green_keyhole[2]-fl.keyhole_outer_dia*0.65,"GKeyholeLoopDown",3.5), # get below green keyhole
        GoToAction(fl.green_keyhole[0]-greenovershootoffset, fl.green_keyhole[1]-0.9, fl.green_keyhole[2],"GKeyholeLoopUp",3), # get to right height for green keyhole
        GoToAction(fl.green_keyhole[0]-greenovershootoffset-fl.in_to_m(5),fl.green_keyhole[1]+0.2,None,"GKeyholeLoopThrough",2), # go through keyhole and align for next keyhole
        # ------ BEGIN LOOPS 3 AND 4 ------
        GoToAction(fl.green_keyhole[0]-0.6-greenovershootoffset, fl.green_keyhole[1]-0.3, fl.green_keyhole[2]-fl.keyhole_outer_dia*0.65,"GKeyholeLoopDown",3.5), 
        GoToAction(fl.in_to_m(49), fl.yellow_keyhole[1]+0.2, fl.yellow_keyhole[2]-fl.keyhole_outer_dia*0.6, "YKeyholePrepare", 5), #  get above yellow keyhole 
        GoToAction(fl.in_to_m(48), 0, fl.yellow_keyhole[2]-fl.in_to_m(5),"YKeyholeLoopUp", 3), #  get to right height for keyhole
        GoToAction(fl.yellow_keyhole[0]+fl.in_to_m(10), 0, fl.yellow_keyhole[2],"GoThroughYKeyhole", 2), # go through keyhole and align for next keyhole
        GoToAction(fl.in_to_m(49), fl.yellow_keyhole[1]+0.5, fl.yellow_keyhole[2]-fl.keyhole_outer_dia*0.7, "YKeyholeLoopDown", 3), #  get above yellow keyhole
        GoToAction(fl.in_to_m(48), 0, fl.yellow_keyhole[2]-fl.in_to_m(5),"YKeyholeLoopUp", 3), #  get to right height for keyhole
        GoToAction(fl.green_keyhole[0]-greenovershootoffset,None, None, "YKeyholeLoopThrough", 2), # go through keyhole and align for next keyhole
        GoToAction(None, fl.green_keyhole[1]-0.30, fl.green_keyhole[2],"GKeyholePrepareHeight",4), # get to correct height for yellow keyhole and get a bit closer
        #WaitAction(1), # settle a bit
        GoToAction(None, fl.green_keyhole[1]+0.20, None, "GoThroughGKeyhole",2),
        GoToAction(fl.green_keyhole[0]-0.6-greenovershootoffset, fl.green_keyhole[1]-0.3, fl.green_keyhole[2]-fl.keyhole_outer_dia*0.65,"GKeyholeLoopDown",3.5), # get below green keyhole
        GoToAction(fl.green_keyhole[0]-greenovershootoffset, fl.green_keyhole[1]-0.9, fl.green_keyhole[2],"GKeyholeLoopUp",3), # get to right height for green keyhole
        GoToAction(fl.green_keyhole[0]-greenovershootoffset,fl.green_keyhole[1]+0.25,None,"GKeyholeLoopThrough",2), # go through keyhole and align for next keyhole
        # ------ BEGIN ARCH/LANDING ------
        GoToAction(None, None, fl.blue_arch[2], "BArchPrepareHeight",3), # prepare to go through blue arch
        #WaitAction(1), # settle a bit
        GoToAction(fl.mat_2[0], fl.mat_2[1], None, "GoThroughBlueArch",2), # go through blue arch 
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
    
    logging.info(f"Drone now at: {np.array2string(drone_manager.drone_pose, 3)}" )
    
    SequentialAction(drone_manager, [
        FastTakeoffAction(0.25),
        ArbitraryCodeAction(lambda dm: logging.info(f"Drone now at: {np.array2string(dm.drone_pose, 3)}")),
        GoToAction(landing_loc[0], landing_loc[1], None, "GoToLanding", 4),
        EmergencyStopAction(),
        EmergencyStopAction(),
        EmergencyStopAction(),
        EmergencyStopAction()
    ], ErrorHandlingStrategy.LAND).run_sequence()