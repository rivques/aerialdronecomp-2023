from typing import Callable, Optional, List

import numpy as np
from utils.action import Action
from utils.drone_manager import DroneManager, ManagedFlightState
import asyncio
from enum import Enum
import logging

class ArbitraryCodeAction(Action):
    def __init__(self, setup: Callable[[DroneManager], None], loop: Callable[[DroneManager], bool]=lambda dm: True):
        self.setup_code = setup
        self.loop_code = loop
    async def setup(self, drone_manager: DroneManager):
        self.setup_code(drone_manager)
    async def loop(self, drone_manager: DroneManager) -> bool:
        return self.loop_code(drone_manager)

class ReadColorAndSetLEDAction(Action):
    async def setup(self, drone_manager: DroneManager):
        drone_manager.get_colors()

class ErrorHandlingStrategy(Enum):
    RAISE = 0
    LAND = 1
    ESTOP = 2
    NEXT_ACTION = 3
    BREAK = 4

class GoToAction(Action):
    def __init__(self, x: Optional[float], y: Optional[float], z: Optional[float], name=None):
        self.x = x
        self.y = y
        self.z = z
        self.name=name
    async def setup(self, drone_manager: DroneManager):
        await drone_manager.go_to_abs(self.x, self.y, self.z)
    async def loop(self, drone_manager: DroneManager) -> bool:
        return drone_manager.managed_flight_state == ManagedFlightState.IDLE
    def __str__(self):
        if self.name is not None:
            return self.name
        x_str = 'None' if self.x is None else f"{self.x:.3f}"
        y_str = 'None' if self.y is None else f"{self.y:.3f}"
        z_str = 'None' if self.z is None else f"{self.z:.3f}"
        return f"GoToAction({x_str}, {y_str}, {z_str})"

class RotateAction(Action):
    def __init__(self, angle: float):
        self.angle = angle
    async def setup(self, drone_manager: DroneManager):
        await drone_manager.go_to_abs(None, None, None, self.angle)
    async def loop(self, drone_manager: DroneManager) -> bool:
        return drone_manager.managed_flight_state == ManagedFlightState.IDLE
    def __str__(self):
        return f"RotateAction({self.angle})"

class RelativeMotionAction(Action):
    def __init__(self, x: Optional[float], y: Optional[float], z: Optional[float]):
        self.x = x
        self.y = y
        self.z = z
    async def setup(self, drone_manager: DroneManager):
        await drone_manager.go_to_rel(self.x, self.y, self.z)
    async def loop(self, drone_manager: DroneManager) -> bool:
        return drone_manager.managed_flight_state == ManagedFlightState.IDLE
    def __str__(self):
        return f"RelativeMotionAction({self.x}, {self.y}, {self.z})"

class LandAction(Action):
    async def setup(self, drone_manager: DroneManager):
        await drone_manager.land()
    async def loop(self, drone_manager: DroneManager) -> bool:
        return drone_manager.managed_flight_state == ManagedFlightState.LANDED

class TakeoffAction(Action):
    async def setup(self, drone_manager: DroneManager):
        await drone_manager.takeoff()
    async def loop(self, drone_manager: DroneManager) -> bool:
        return True

class WaitAction(Action):
    def __init__(self, wait_time=1.0) -> None:
        self.wait_time = wait_time
        super().__init__()
    async def setup(self, drone_manager: DroneManager):
        await asyncio.sleep(self.wait_time)
    async def loop(self, drone_manager: DroneManager) -> bool:
        return True

class SequentialAction(Action):
    def __init__(self, drone_manager: Optional[DroneManager], actions: List[Action], ehs: ErrorHandlingStrategy = ErrorHandlingStrategy.RAISE, event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
        self.drone_manager = drone_manager
        self.actions = actions
        self.ehs = ehs
        self.event_loop = event_loop
    
    def run_sequence(self):
        seqtask = self.event_loop.create_task(self.setup())
        try:
            self.event_loop.run_until_complete(seqtask)
        except BaseException as e:
            if self.ehs == ErrorHandlingStrategy.RAISE:
                raise e
            elif self.ehs == ErrorHandlingStrategy.LAND:
                logging.info("Error thrown, landing...")
                self.drone_manager.raw_drone.land()
                raise e
            elif self.ehs == ErrorHandlingStrategy.ESTOP:
                self.drone_manager.raw_drone.emergency_stop()
                return
            elif self.ehs == ErrorHandlingStrategy.BREAK:
                return
            else:
                raise Exception("Invalid ErrorHandlingStrategy")
    
    async def setup(self):
        for action in self.actions:
            logging.info(f"Now running {action}...")
            try:
                await action.setup(self.drone_manager)
                while True:
                    await asyncio.sleep(0)
                    if await action.loop(self.drone_manager):
                        break
            except BaseException as e:
                if self.ehs == ErrorHandlingStrategy.RAISE:
                    raise e
                elif self.ehs == ErrorHandlingStrategy.LAND:
                    logging.info("Error thrown, landing...")
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
    
    async def loop(self):
        return True # it all happens in setup
    
    def __str__(self):
        contents = ", ".join([str(action) for action in self.actions])
        return f"SequentialAction({contents})"