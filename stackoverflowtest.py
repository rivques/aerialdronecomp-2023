import pygame

pygame.init()
clock = pygame.time.Clock()

class JoyStick():

    def __init__(self):
        pass

    def update(self):
        joystickOne = pygame.joystick.Joystick(0)
        joystickOne.init()
        self.axisOne = joystickOne.get_axis(1)

OP = JoyStick()

done = False

while done==False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done=True
    OP.update()
    print(OP.axisOne)
    clock.tick(50)