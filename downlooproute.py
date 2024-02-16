from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import ReadColorAndSetLEDAction, SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, ArbitraryCodeAction
import utils.field_locations as fl
import numpy as np
import logging
logging.basicConfig(level=logging.INFO)
if __name__ == "__main__":
    drone_manager = DroneManager(drone_type=DroneType.REAL, show_error_graph=False)

    # wait for signal to take off
    input("Drone ready, press enter to start!")
    drone_manager.ignore_next_loop_warning()

    # route: take off, go through red arch, go through yellow keyhole, go through green keyhole, go through blue arch and land on mat 2
    SequentialAction(drone_manager, [
        ReadColorAndSetLEDAction(),
        TakeoffAction(),
        GoToAction(0, 0, fl.red_arch[2], "ArchPrepareAlt", 4), # get to good altitude for arch
        #WaitAction(1), # settle a bit
        GoToAction(fl.in_to_m(48), fl.yellow_keyhole[1], None, "GoThroughArch", 2), # go through arch and align for keyhole on xy plane
        GoToAction(None, None, fl.yellow_keyhole[2],"YKeyholePrepareHeight", 3), #  get to right height for keyhole
        #WaitAction(1), # settle a bit
        GoToAction(fl.yellow_keyhole[0]+fl.in_to_m(10), None, None,"GoThroughYKeyhole", 2), # go through keyhole and align for next keyhole
        GoToAction(fl.in_to_m(53), fl.yellow_keyhole[1]+0.5, fl.yellow_keyhole[2]-fl.keyhole_outer_dia*0.6, "YKeyholeLoopDown", 3), #  get above yellow keyhole 
        GoToAction(fl.in_to_m(48), 0, fl.yellow_keyhole[2],"YKeyholeLoopUp", 3), #  get to right height for keyhole
        GoToAction(fl.green_keyhole[0],None, None, "YKeyholeLoopThrough", 2), # go through keyhole and align for next keyhole
        GoToAction(None, fl.green_keyhole[1]-0.30, fl.green_keyhole[2],"GKeyholePrepareHeight",4), # get to correct height for yellow keyhole and get a bit closer
        #WaitAction(1), # settle a bit
        GoToAction(None, fl.green_keyhole[1]+0.30, None, "GoThroughGKeyhole",2),
        GoToAction(None, None, fl.blue_arch[2], "BArchPrepareHeight",3), # prepare to go through blue arch
        #WaitAction(1), # settle a bit
        GoToAction(fl.mat_2[0], fl.mat_2[1], None, "GoThroughBlueArch",2), # go through blue arch 
        #WaitAction(1), # settle a bit
        LandAction(),
        ReadColorAndSetLEDAction(),
    ], ErrorHandlingStrategy.LAND).run_sequence()
    if drone_manager.last_color == "Blue":
        landing_loc = fl.blue_landing_pad
    elif drone_manager.last_color == "Red":
        landing_loc = fl.red_landing_pad
    else:
        landing_loc = fl.green_landing_pad
    
    logging.info(f"Drone now at: {np.array2string(drone_manager.drone_pose, 3)}" )
    
    SequentialAction(drone_manager, [
        TakeoffAction(),
        ArbitraryCodeAction(lambda dm: logging.info(f"Drone now at: {np.array2string(dm.drone_pose, 3)}")),
        GoToAction(landing_loc[0], landing_loc[1], None, "GoToLanding", 5),
        LandAction()
    ], ErrorHandlingStrategy.LAND).run_sequence()