from enum import Enum
from drone_manager import DroneManager
from action import Action
from typing import List

class ErrorHandlingStrategy(Enum):
    RAISE = 0
    LAND = 1
    ESTOP = 2
    NEXT_ACTION = 3
    BREAK = 4

class DroneTrajectory:
    def __init__(self, drone_manager: DroneManager, actions: List[Action], ehs: ErrorHandlingStrategy = ErrorHandlingStrategy.BREAK):
        self.drone_manager = drone_manager
        self.actions = actions
    async def follow(self):
        for action in self.actions:
            try:
                await action.setup(self.drone_manager)
                while True:
                    if await action.loop(self.drone_manager):
                        break
            except Exception as e:
                if self.ehs == ErrorHandlingStrategy.RAISE:
                    raise e
                elif self.ehs == ErrorHandlingStrategy.LAND:
                    await self.drone_manager.land()
                    return
                elif self.ehs == ErrorHandlingStrategy.ESTOP:
                    await self.drone_manager.raw_drone.emergency_stop()
                    return
                elif self.ehs == ErrorHandlingStrategy.NEXT_ACTION:
                    continue
                elif self.ehs == ErrorHandlingStrategy.BREAK:
                    return
                else:
                    raise Exception("Invalid ErrorHandlingStrategy")