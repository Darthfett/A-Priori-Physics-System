import sys, os, game, pygame

if __name__ == "__main__":
    # Game being run as standalone script
    script_name = sys.argv.pop(0)
    args = sys.argv
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    game.run()
else:
    # Game being imported as a module
    # We don't handle this scenario.
    raise ImportError("main is not designed to work as a module.")