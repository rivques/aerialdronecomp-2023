from utils.action import Action
from utils.basic_actions import GoToAction, LandAction, SequentialAction, TakeoffAction
from utils.drone_manager import DroneManager
from enum import Enum
import field_locations as fl

# here lives more complex actions, like maybe LoopKeyhole or ColorLand

# assumes we're sitting right in front of the keyhole
class KeyholeLoopAction(SequentialAction):
    def __init__(self, drone_manager: DroneManager):
        super.__init__(self, drone_manager, [
            
        ])

class ColorLandState(Enum):
    READING_COLOR = 0
    TAKING_OFF = 1
    MOVING_TO_COLOR = 2
    LANDING = 3

class ColorLandAction(Action):
    landing_locations = {
        "red": fl.red_landing_pad,
        "green": fl.green_landing_pad,
        "blue": fl.blue_landing_pad,
    }
    def __init__(self) -> None:
        self.state = ColorLandState.READING_COLOR
        self.landing_target = None
        self.current_action = None
        super().__init__()
    async def loop(self, drone_manager: DroneManager) -> bool:
        if self.state == ColorLandState.READING_COLOR:
            colors = drone_manager.get_colors()
            if "unknown" in colors:
                return False
            self.landing_target = self.landing_locations[colors[0]]
            # TODO: set top LED to color
            self.state = ColorLandState.MOVING_TO_COLOR
            self.current_action = TakeoffAction()
            self.current_action.setup(drone_manager)
            return False
        elif self.state == ColorLandState.TAKING_OFF:
            if self.current_action.loop(drone_manager):
                # we've taken off
                self.current_action = GoToAction(self.landing_target[0], self.landing_target[1], None)
                self.current_action.setup(drone_manager)
                self.state = ColorLandState.MOVING_TO_COLOR
                return False
            return False
        elif self.state == ColorLandState.MOVING_TO_COLOR:
            if self.current_action.loop(drone_manager):
                # we have arrived! land
                # might need to wait here longer
                self.current_action = LandAction()
                self.current_action.setup(drone_manager)
                self.state = ColorLandState.LANDING
            return False
        elif self.state == ColorLandState.LANDING:
            if self.current_action.loop(drone_manager):
                # we have landed!
                return True
            return False