from codrone_edu.drone import *

drone = Drone()
drone.pair()
drone.reset_sensor()
drone.takeoff()
print(f"Now at {drone.get_position_data()}, facing {drone.get_yaw()}")
drone.move_forward(1)
print(f"Now at {drone.get_position_data()}, facing {drone.get_yaw()}")
drone.turn_degree(90)
print(f"Now at {drone.get_position_data()}, facing {drone.get_yaw()}")
drone.move_forward(1)
print(f"Now at {drone.get_position_data()}, facing {drone.get_yaw()}")
