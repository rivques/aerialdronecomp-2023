from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import ArbitraryCodeAction, ReadColorAndSetLEDAction, SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, WaitAction
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
        GoToAction(0, 0, fl.red_arch[2], "ArchPrepareAlt", 5), # get to good altitude for arch
        #WaitAction(1), # settle a bit
        GoToAction(fl.in_to_m(48), fl.yellow_keyhole[1], None, "GoThroughArch", 2), # go through arch and align for keyhole on xy plane
        GoToAction(None, None, fl.yellow_keyhole[2],"YKeyholePrepareHeight", 5), #  get to right height for keyhole
        #WaitAction(1), # settle a bit
        GoToAction(fl.green_keyhole[0], None, None,"GoThroughYKeyhole", 2), # go through keyhole and align for next keyhole
        GoToAction(None, fl.green_keyhole[1]-0.30, fl.green_keyhole[2],"GKeyholePrepareHeight",5), # get to correct height for yellow keyhole and get a bit closer
        #WaitAction(1), # settle a bit
        GoToAction(None, fl.green_keyhole[1]+0.30, None, "GoThroughGKeyhole",2),
        GoToAction(None, None, fl.blue_arch[2], "BArchPrepareHeight",5), # prepare to go through blue arch
        #WaitAction(1), # settle a bit
        GoToAction(fl.mat_2[0], fl.mat_2[1], None, "GoThroughBlueArch",2), # go through blue arch 
        #WaitAction(1), # settle a bit
        LandAction(),
        ReadColorAndSetLEDAction(),
    ], ErrorHandlingStrategy.LAND).run_sequence()