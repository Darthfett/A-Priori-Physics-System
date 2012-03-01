"""
The main module should be run as __main__ in order to set up and start the game.
"""
import sys, os, game, pygame

if __name__ == "__main__":
    # Game being run as standalone script
    # TODO: Arguments passed to the script are currently ignored.
    script_name = sys.argv.pop(0)
    args = sys.argv
    
    # Set up an SDL environment video parameter, required for pygame.
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    # Initialize and run the game!
    pygame.init()
    game.init()
    game.run()
else:
    # Game being imported as a module
    # We don't handle this scenario.
    pass
