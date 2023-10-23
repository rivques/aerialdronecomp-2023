from drone_manager import DroneManager
# abstract class
class Action:
    # runs once
    async def setup(self, drone_manager: DroneManager):
        pass

    # runs frequently, returns true to stop
    async def loop(self, drone_manager: DroneManager) -> bool:
        return True
    
    def __str__(self):
        return self.__class__.__name__
