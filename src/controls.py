"""
The controls module maps the player's keyboard keys to their controls.

classes:
  Quit                          An Exception that is raised when the player quits
                                the game.
                                
functions:
  quit                          Quit the game.
  regenerate_ground             Randomly regenerate the ground terrain.
  flip_pause_state              Pause/unpause the game.
  reset_player                  Move the player back to starting position, and
                                reset the player's velocity.

"""

import pygame

from game import game
import event

class Quit(Exception):
    """An Exception that is raised when the player quits."""
    pass
    
def quit():
    """Quit the game."""
    raise Quit
    
def regenerate_ground():
    """Randomly regenerate the ground terrain."""
    game.current_level.regenerate_ground()
            
def flip_pause_state():
    """Pause/unpause the game."""
    game.Game().pause()
            
def reset_player():
    """
    Move the player back to starting position, and reset the player's velocity.
    
    """
    game.current_level.reset_player()
            
event.KeyPressEvent[pygame.K_q].register(quit)
event.KeyPressEvent[pygame.K_ESCAPE].register(quit)
event.KeyPressEvent[pygame.K_r].register(regenerate_ground)
event.KeyPressEvent[pygame.K_p].register(flip_pause_state)
event.KeyPressEvent[pygame.K_SPACE].register(reset_player)