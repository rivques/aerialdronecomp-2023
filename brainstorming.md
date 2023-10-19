One-offs (should get these)
TO: 10
ICM x2: 30
Land: 25
Total: 65
-----
Hard to miss if doing one-offs:
AG x2: 10
----
Loop totals:
Arch: 15
Keyhole: 25
----
Rough mission order:
1. pair, set to white, wait for input.
2. Color sense mat 1 and set color. 15 pts
3. Path through red, yellow, green, blue arch/KHs. Throw in loops if time. 30+ pts
4. Color sense mat 2 from air if possible or land if not. 15 pts.
5. Land appropriately. 25 pts.
Total (no loops): 85 pts
----
Code architecture:
Build PID over the existing control system. OR use send_absolute_position and get_flight_state if that's good enough
Use async.
API: Most general user-facing function is `async DroneManager.lerp_to(x, y, z, heading)` where None means don't touch it
DroneManager class:
has property raw_drone
has a flight state var
has a THRESHOLD var that determines how close you need to be to target to complete move
uses get_position_data (need accuracy test, esp above 1.5m)

---
Hardware:
Not a removeable laptop. Raspi or similar with direct cable interface to controller on plywood or smth. NO CABLE DCs.
----
Time estimation: 2.0m/s max speed, 1 m/s more realistic.

----