from utils.drone_manager import DroneManager, DroneType
from utils.basic_actions import ReadColorAndSetLEDAction, SequentialAction, TakeoffAction, GoToAction, LandAction, ErrorHandlingStrategy, WaitAction
import utils.field_locations as fl
import logging
logging.basicConfig(level=logging.INFO)
if __name__ == "__main__":
    drone_manager = DroneManager(drone_type=DroneType.REAL, show_error_graph=True)

    # wait for signal to take off
    input("Drone ready, press enter to start!")
    drone_manager.ignore_next_loop_warning()

    # route: take off, go through red arch, go through yellow keyhole, go through green keyhole, go through blue arch and land on mat 2
    SequentialAction(drone_manager, [
        # ReadColorAndSetLEDAction(),
        TakeoffAction(),
        GoToAction(0, 0, fl.red_arch[2], "ArchPrepareAlt"), # get to good altitude for arch
        WaitAction(2.5), # settle a bit
        GoToAction(fl.in_to_m(48), fl.yellow_keyhole[1], None, "GoThroughArch"), # go through arch and align for keyhole on xy plane
        GoToAction(None, None, fl.yellow_keyhole[2],"YKeyholePrepareHeight"), #  get to right height for keyhole
        WaitAction(2.5), # settle a bit
        GoToAction(fl.green_keyhole[0], None, None,"GoThroughYKeyhole"), # go through keyhole and align for next keyhole
        GoToAction(None, fl.green_keyhole[1]-0.30, fl.green_keyhole[2],"GKeyholePrepareHeight"), # get to correct height for yellow keyhole and get a bit closer
        WaitAction(2.5), # settle a bit
        GoToAction(None, fl.green_keyhole[1]+0.30, None, "GoThroughGKeyhole"),
        GoToAction(None, None, fl.blue_arch[2], "BArchPrepareHeight"), # prepare to go through blue arch
        WaitAction(2.5), # settle a bit
        GoToAction(fl.mat_2[0], fl.mat_2[1], None, "GoThroughBlueArch"), # go through blue arch 
        WaitAction(1.5), # settle a bit
        LandAction(),
        ReadColorAndSetLEDAction(),
    ], ErrorHandlingStrategy.LAND).run_sequence()