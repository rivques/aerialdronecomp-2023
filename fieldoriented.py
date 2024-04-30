import math
from pygame import joystick
import pygame
from codrone_edu.drone import * 
import time

drone = Drone()
drone.pair()

pygame.init()
joystick.init()
print(f"Number of joysticks: {joystick.get_count()}")

joy = joystick.Joystick(0)

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

joy.init()
print(f"Joystick name: {joy.get_name()}")
print(f"Joystick ID: {joy.get_id()}")
print(f"Joystick number of axes: {joy.get_numaxes()}")
print(f"Joystick number of balls: {joy.get_numballs()}")
print(f"Joystick number of buttons: {joy.get_numbuttons()}")
print(f"Joystick number of hats: {joy.get_numhats()}")
last_update = time.time()
time.sleep(0.1)
angle_offset = 0
last_angle = 0
last_angle_update = time.time()
while True:
    for event in pygame.event.get(): # this is needed for some reason
        pass
    joy=joystick.Joystick(0)
    joy.init()
    now = time.time()
    throttle = -joy.get_axis(1)*100
    yaw = -joy.get_axis(0)*100
    pitch = -joy.get_axis(3)*100
    roll = joy.get_axis(2)*100
    orientation = drone.get_sensor_data()[14] - angle_offset
    if orientation != last_angle:
        last_angle_update = last_update
    last_angle = orientation
    print(f"angle update: {1/(now-last_angle_update):.1f} Hz Speed: {1/(now-last_update):.1f} Hz Axis values: {[joy.get_axis(i) for i in range(joy.get_numaxes())]}, button values: {[joy.get_button(i) for i in range(joy.get_numbuttons())]}, hat values: {[joy.get_hat(i) for i in range(joy.get_numhats())]}")
    last_update = now
    # field-oriented control
    new_pitch = pitch * math.cos(math.radians(orientation)) - roll * math.sin(math.radians(orientation))
    new_roll = pitch * math.sin(math.radians(orientation)) + roll * math.cos(math.radians(orientation))
    drone.set_throttle(clamp(int(-joy.get_axis(1)*100), -99, 99))
    drone.set_yaw(clamp(int(-joy.get_axis(0)*100), -99, 99))
    drone.set_pitch(clamp(new_pitch, -99, 99))
    drone.set_roll(clamp(new_roll, -99, 99))
    drone.move()
    # takeoffs
    if joy.get_button(0):
        drone.reset_move()
        drone.sendTakeOff()
    # resets
    if joy.get_button(1):
        angle_offset = drone.get_z_angle()
    # drone speed
    if joy.get_button(2):
        drone.set_motor_speed(3)
