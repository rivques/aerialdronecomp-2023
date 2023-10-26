from utils.action import Action
from utils.basic_actions import GoToAction, LandAction, SequentialAction, TakeoffAction
from utils.drone_manager import DroneManager

# here lives more complex actions, like maybe LoopKeyhole or ColorLand

# assumes we're sitting right in front of the keyhole
class KeyholeLoopAction(SequentialAction):
    def __init__(self, drone_manager: DroneManager):
        super.__init__(self, drone_manager, [
            
        ])