import pygame
import game
import event

class Quit(Exception):
    """An Exception that is raised when the player quits."""
    def __init__(self, key):
        if key == pygame.K_q or key == pygame.K_ESCAPE:
            raise Quit

class RegenerateGround:
    def __init__(self, key):
        if key == pygame.K_r:
            game.Game.CurrentLevel.regenerate_ground()
            
class Pause:
    def __init__(self, key):
        if key == pygame.K_p:
            game.Game().pause()
            
class ResetPlayer:
    def __init__(self, key):
        if key == pygame.K_SPACE:
            game.Game.CurrentLevel.reset_player()
            
event.KeyPressEvent.register(Quit)
event.KeyPressEvent.register(RegenerateGround)
event.KeyPressEvent.register(Pause)
event.KeyPressEvent.register(ResetPlayer)