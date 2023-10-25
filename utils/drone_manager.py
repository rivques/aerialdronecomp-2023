from codrone_edu.drone import *
import asyncio
import logging
from typing import Optional
from matplotlib.figure import Figure
import numpy as np
import socket
from simple_pid import PID
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style, widgets

# enum for managed flight state
class ManagedFlightState(Enum):
    IDLE = 0
    MOVING = 2
    LANDED = 4

class DroneType(Enum):
    REAL = 0
    PROPS_OFF = 1
    FULL_SIM = 2

def yaw_clip(angle):
    # deal with wrapping yaw angle around 360˚
    if angle > 0:
        if angle > 180:
            return angle - 360
    else:
        if angle < -180:
            return angle + 360
    return angle

class DroneManager:
    update_frequency = 10 # Hz
    lerp_threshold = 0.15 # m
    pid_controllers = [
        PID(30, 0, 0, setpoint=0, output_limits=(-100, 100)), # x
        PID(30, 0, 0, setpoint=0, output_limits=(-100, 100)), # y
        PID(30, 0, 0, setpoint=0, output_limits=(-100, 100)), # z
        PID(30, 0, 0, setpoint=0, output_limits=(-100, 100), error_map=yaw_clip) # yaw
    ]

    _target_pose = np.array([0, 0, 0, 0])
    @property
    def target_pose(self):
        return self._target_pose
    @target_pose.setter
    def target_pose(self, value):
        self._target_pose = value
        for i in range(4):
            self.pid_controllers[i].setpoint = value[i]

    _disabled_control_axes = [False, False, False, False]
    @property
    def disabled_control_axes(self):
        return self._disabled_control_axes
    @disabled_control_axes.setter
    def disabled_control_axes(self, value):
        self._disabled_control_axes = value
        for i, disabled in enumerate(self._disabled_control_axes):
            if disabled:
                self.pid_controllers[i].set_auto_mode(False, last_output=0)
                self.current_output[i] = 0

    def __init__(self, event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(), drone_type = DroneType.REAL, show_error_graph = False, disabled_control_axes = [False, False, False, False]):
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
            # self.raw_drone.controller_draw_string(3, 3, hostname)
        # set up drone state
        self.drone_pose: np.ndarray = np.array([0, 0, 0, 0]) # x, y, z, yaw
        self.target_pose: np.ndarray = np.array([0, 0, 0, 0])
        self.current_output: np.ndarray = np.array([0, 0, 0, 0])
        self.managed_flight_state: ManagedFlightState = ManagedFlightState.LANDED
        # set up update loop
        self.event_loop = event_loop
        asyncio.ensure_future(self.start_update_loop(),loop=self.event_loop)
        if show_error_graph:
            asyncio.ensure_future(self.animate_plot(), loop=self.event_loop)
        
        self.disabled_control_axes = disabled_control_axes 

    async def takeoff(self, altitude=1):
        self.raw_drone.takeoff() # blocks
        self.target_pose = np.array([0, 0, 1, 0])
    
    async def land(self):
        self.raw_drone.land() # blocks
        self.target_pose[2] = 0
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
        if self.drone_type in [DroneType.REAL]:
            # calculate gains
            self.current_output = np.array([self.pid_controllers[i](self.drone_pose[i]) for i in range(4)])
            # set gains
            self.raw_drone.set_pitch(self.current_output[0])
            self.raw_drone.set_roll(-self.current_output[1]) # roll is negative for some reason
            self.raw_drone.set_throttle(self.current_output[2])
            self.raw_drone.set_yaw(self.current_output[3])
            self.raw_drone.move()
            logging.debug(f"Drone polled, pose now {np.array2string(self.drone_pose, precision=3)} (target {np.array2string(self.target_pose)}, error {np.linalg.norm(self.drone_pose[:3] - self.target_pose[:3])})")
            logging.debug(f"Drone gains: x {self.current_output[0]}, y {self.current_output[1]}, z {self.current_output[2]}, yaw {self.current_output[3]}")

    def render_plot(self, ax, target, current, output, title):
        error = target - current
        ax.clear()
        ax.plot(error, 'r', label='Error')
        ax.plot(target, 'g', label='Target')
        ax.plot(current, 'b', label='Current')
        ax.plot(output, 'y', label='Output')
        ax.legend(loc='upper left')
        ax.set_title(title)

    async def animate_plot(self):
        style.use('fivethirtyeight')
        fig = plt.figure()
        ax1 = fig.add_subplot(2, 2, 1)
        ax2 = fig.add_subplot(2, 2, 2)
        ax3 = fig.add_subplot(2, 2, 3)
        ax4 = fig.add_subplot(2, 2, 4)

        def animate(i):
            self.render_plot(ax1, self.target_pose[0], self.drone_pose[0], self.current_output[0], 'X')
            self.render_plot(ax2, self.target_pose[1], self.drone_pose[1], self.current_output[1], 'Y')
            self.render_plot(ax3, self.target_pose[2], self.drone_pose[2], self.current_output[2], 'Z')
            self.render_plot(ax4, self.target_pose[3], self.drone_pose[3], self.current_output[3], 'Yaw')

        ani = animation.FuncAnimation(fig, animate, interval=1000/self.update_frequency) # hold on to this reference, or it will be garbage collected
        plt.show(block=False)

        while True:
            await asyncio.sleep(1/self.update_frequency)
            fig.canvas.draw() # if this doesn't work: try plt.ion, plt.show, plt.pause(0.001), or finally kicking it off into another thread
        

    async def go_to_abs(self, x: Optional[float], y: Optional[float], z: Optional[float], yaw: Optional[float] = None):
        # None means don't change that value
        target_x = x if x is not None else self.target_pose[0]
        target_y = y if y is not None else self.target_pose[1]
        target_z = z if z is not None else self.target_pose[2]
        target_yaw = yaw if yaw is not None else self.target_pose[3]
        self.target_pose = np.array([target_x, target_y, target_z, target_yaw])

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