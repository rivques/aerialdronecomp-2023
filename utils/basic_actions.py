from typing import Optional
from utils.action import Action
from utils.drone_manager import DroneManager, ManagedFlightState

class GoToAction(Action):
    def __init__(self, x: Optional[float], y: Optional[float], z: Optional[float]):
        self.x = x
        self.y = y
        self.z = z
    async def setup(self, drone_manager: DroneManager):
        await drone_manager.go_to(self.x, self.y, self.z)
    async def loop(self, drone_manager: DroneManager) -> bool:
        return drone_manager.managed_flight_state == ManagedFlightState.IDLE

class LandAction(Action):
    async def setup(self, drone_manager: DroneManager):
        await drone_manager.land()
    async def loop(self, drone_manager: DroneManager) -> bool:
        return drone_manager.managed_flight_state == ManagedFlightState.LANDED

class TakeoffAction(Action):
    async def setup(self, drone_manager: DroneManager):
        await drone_manager.takeoff()
    async def loop(self, drone_manager: DroneManager) -> bool:
        return drone_manager.managed_flight_state == ManagedFlightState.IDLE

