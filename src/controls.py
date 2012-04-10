import pygame

import game
import event

class Quit(Exception):
    """An Exception that is raised when the player quits."""
    pass
    
def quit():
    raise Quit
    
def regenerate_ground():
    game.Game.CurrentLevel.regenerate_ground()
            
def flip_pause_state():
    game.Game().pause()
            
def reset_player():
    game.Game.CurrentLevel.reset_player()
            
event.KeyPressEvent[pygame.K_q].register(quit)
event.KeyPressEvent[pygame.K_ESCAPE].register(quit)
event.KeyPressEvent[pygame.K_r].register(regenerate_ground)
event.KeyPressEvent[pygame.K_p].register(flip_pause_state)
event.KeyPressEvent[pygame.K_SPACE].register(reset_player)