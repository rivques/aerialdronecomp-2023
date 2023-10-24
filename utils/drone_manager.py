from codrone_edu.drone import *
import asyncio
import logging
from typing import Optional
import numpy as np
import socket

# enum for managed flight state
class ManagedFlightState(Enum):
    IDLE = 0
    MOVING = 2
    LANDED = 4

class DroneType(Enum):
    REAL = 0
    PROPS_OFF = 1
    FULL_SIM = 2

class DroneManager:
    update_frequency = 10 # Hz
    lerp_threshold = 0.1 # m

    def __init__(self, event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(), drone_type = DroneType.REAL):
        # set up drone
        self.raw_drone: Drone = Drone()
        self.drone_type = drone_type
        if drone_type in [DroneType.REAL, DroneType.PROPS_OFF]:
            self.raw_drone.pair()
            self.raw_drone.set_drone_LED(255, 255, 255, 255)
            # calibrate sensors
            self.raw_drone.set_initial_pressure()
            self.raw_drone.reset_sensor()
            # display ip address on controller screen:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            self.raw_drone.controller_draw_string(3, 3, ip_address)
        # set up drone state
        self.drone_pose: np.ndarray = np.array([0, 0, 0, 0]) # x, y, z, yaw
        self.target_pose: np.ndarray = np.array([0, 0, 0, 0])
        self.managed_flight_state: ManagedFlightState = ManagedFlightState.LANDED
        # set up update loop
        self.event_loop = event_loop
        self.event_loop.create_task(self.start_update_loop())

    async def takeoff(self, altitude=1):
        await self.go_to_abs(None, None, altitude)
    
    async def land(self):
        await self.go_to_abs(None, None, 0)
        self.managed_flight_state = ManagedFlightState.LANDED
    
    async def start_update_loop(self):
        while True:
            await asyncio.sleep(1/self.update_frequency)
            self.poll_drone()
    
    def poll_drone(self):
        # drone state docs at https://docs.robolink.com/docs/codrone-edu/python/Sensors/24-get_sensor_data
        if self.drone_type in [DroneType.FULL_SIM]:
            self.drone_pose = self.target_pose
        else:
            drone_state = self.raw_drone.get_sensor_data()
            self.drone_pose = np.array([drone_state[16], drone_state[17], drone_state[18], drone_state[14]])
        logging.debug(f"Drone polled, pose now {np.array2string(self.drone_pose)}")
        # TODO: Constantly set absolute location to target if needed

    async def go_to_abs(self, x: Optional[float], y: Optional[float], z: Optional[float]):
        # None means don't change that value
        target_x = x if x is not None else self.drone_pose[0]
        target_y = y if y is not None else self.drone_pose[1]
        target_z = z if z is not None else self.drone_pose[2]
        self.target_pose = np.array([target_x, target_y, target_z, self.drone_pose[3]])

        if self.drone_type in [DroneType.REAL]:
            self.raw_drone.send_absolute_position(target_x, target_y, target_z, 0, self.drone_pose[3], 0)

        self.managed_flight_state = ManagedFlightState.MOVING
        while True:
            await asyncio.sleep(1/self.update_frequency)
            # check if we're close enough to the target
            if np.linalg.norm(self.drone_pose[:3] - np.array([target_x, target_y, target_z])) < self.lerp_threshold:
                break
        self.managed_flight_state = ManagedFlightState.IDLE
    
    async def go_to_rel(self, x: float, y: float, z: float):
        target_x = self.drone_pose[0] + x
        target_y = self.drone_pose[1] + y
        target_z = self.drone_pose[2] + z

        await self.go_to_abs(target_x, target_y, target_z)

    def get_colors(self):
        return self.raw_drone.get_colors()