import pygame

class Window:

    DEFAULT_WIDTH = 0
    DEFAULT_HEIGHT = 0

    def __init__(self, title, size = [DEFAULT_WIDTH, DEFAULT_HEIGHT]):
        """ Initialize the Window Size and Title """
        
        self.size = size
        self.title = title
        self.screen = pygame.display.set_mode(size) # Accept default flags:
        # Flags (second argument, multiple separated by | ):
            # pygame.FULLSCREEN    create a fullscreen display
            # pygame.DOUBLEBUF     recommended for HWSURFACE or OPENGL
            # pygame.HWSURFACE     hardware accelerated, only in FULLSCREEN
            # pygame.OPENGL        create an opengl renderable display
            # pygame.RESIZABLE     display window should be sizeable
            # pygame.NOFRAME       display window will have no border or controls
        pygame.display.set_caption(self.title)