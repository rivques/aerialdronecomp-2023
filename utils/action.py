import asyncio
from utils.drone_manager import DroneManager
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
    
    def run_sequence(self):
        event_loop = asyncio.get_event_loop()
        seqtask = event_loop.create_task(self.setup())
        event_loop.run_until_complete(seqtask)