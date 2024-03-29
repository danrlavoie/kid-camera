import pygame

class Window():
    def __init__(self):
        print("Done")
    def render(self):
        print("Render")

if __name__==("__main__"):
    pygame.init()
    canvas = pygame.display.set_mode((640, 480))
    exit = False
    while not exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit = True
        pygame.display.update()
