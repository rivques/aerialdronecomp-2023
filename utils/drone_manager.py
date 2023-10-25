from codrone_edu.drone import *
import asyncio
import logging
from typing import Optional
from matplotlib.axes import Axes
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
    control_frequency = 50 # Hz
    graph_update_frequency = 10 # Hz
    gain_history_length = 5 # seconds
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
            # a 3d array of [time, error, target, current, output] for each axis with room for gain_history_length seconds of data with axes as first dimension
            self.error_history = np.zeros((4, 5, self.gain_history_length * self.control_frequency))
            print
        
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
            await asyncio.sleep(1/self.control_frequency)
            self.poll_drone()
    
    def poll_drone(self):
        # drone state docs at https://docs.robolink.com/docs/codrone-edu/python/Sensors/24-get_sensor_data
        if self.drone_type in [DroneType.FULL_SIM]:
            self.drone_pose = self.target_pose
        else:
            drone_state = self.raw_drone.get_sensor_data()
            self.drone_pose = np.array([drone_state[16], drone_state[17], drone_state[18], drone_state[14]])

        # calculate gains
        for i, disabled in enumerate(self.disabled_control_axes):
            if disabled:
                self.current_output[i] = 0
            else:
                self.current_output[i] = self.pid_controllers[i](self.drone_pose[i])

        if self.drone_type in [DroneType.REAL]:
            # set gains
            self.raw_drone.set_pitch(self.current_output[0])
            self.raw_drone.set_roll(-self.current_output[1]) # roll is negative for some reason
            self.raw_drone.set_throttle(self.current_output[2])
            self.raw_drone.set_yaw(self.current_output[3])
            self.raw_drone.move()
        logging.debug(f"Drone polled, pose now {np.array2string(self.drone_pose, precision=3)} (target {np.array2string(self.target_pose)}, error {np.linalg.norm(self.drone_pose[:3] - self.target_pose[:3])})")
        logging.debug(f"Drone gains: x {self.current_output[0]}, y {self.current_output[1]}, z {self.current_output[2]}, yaw {self.current_output[3]}")

    def render_plot(self, ax: Axes, axis_index, title):
        target = self.target_pose[axis_index]
        current = self.drone_pose[axis_index]
        output = self.current_output[axis_index]
        controller = self.pid_controllers[axis_index]
        error = target - current
        time_now = time.monotonic()
        
        history = np.roll(self.error_history[axis_index], -1, axis=1)
        history[0, -1] = time_now
        history[1, -1] = error
        history[2, -1] = target
        history[3, -1] = current
        history[4, -1] = output
        ax.clear()
        ax.plot(time_now - history[0], history[1], label='error')
        ax.plot(time_now - history[0], history[2], label='target')
        ax.plot(time_now - history[0], history[3], label='current')
        ax.plot(time_now - history[0], history[4], label='output')
        ax.legend(loc='upper left')
        ax.set_title(title)
        
        return history

    async def animate_plot(self):
        print("animating plot...")
        style.use('fivethirtyeight')
        fig = plt.figure()
        ax1 = fig.add_subplot(2, 2, 1)
        ax2 = fig.add_subplot(2, 2, 2)
        ax3 = fig.add_subplot(2, 2, 3)
        ax4 = fig.add_subplot(2, 2, 4)

        def animate(i):
            self.error_history[0] = self.render_plot(ax1, 0, "X")
            self.error_history[1] = self.render_plot(ax2, 1, "Y")
            self.error_history[2] = self.render_plot(ax3, 2, "Z")
            self.error_history[3] = self.render_plot(ax4, 3, "Yaw")

        ani = animation.FuncAnimation(fig, animate, interval=1000/self.control_frequency) # hold on to this reference, or it will be garbage collected
        plt.show(block=False)
        print("plot shown")
        while True:
            await asyncio.sleep(1/self.graph_update_frequency)
            plt.pause(0.001) # if this doesn't work: try plt.ion, plt.show, plt.pause(0.001), or finally kicking it off into another thread
        

    async def go_to_abs(self, x: Optional[float], y: Optional[float], z: Optional[float], yaw: Optional[float] = None):
        # None means don't change that value
        target_x = x if x is not None else self.target_pose[0]
        target_y = y if y is not None else self.target_pose[1]
        target_z = z if z is not None else self.target_pose[2]
        target_yaw = yaw if yaw is not None else self.target_pose[3]
        self.target_pose = np.array([target_x, target_y, target_z, target_yaw])

        self.managed_flight_state = ManagedFlightState.MOVING
        while True:
            await asyncio.sleep(1/self.control_frequency)
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