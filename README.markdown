# Jetpack-Man #

## Requirements ##
 - Python 3.2
 - Pygame (1.9.2a0 or higher)

## How to run ##

    usage: python src/main.py [options]

    Runs the game Jetpack-Man

    optional arguments:
      -h, --help           show this help message and exit
      -d, --debug          turn debug mode on
      -g, --draw_outlines  draw outlines of images instead of the actual images
      --fps FPS            Change max drawing FPS
      --speed SPEED        Change the speed multiplier

## Controls ##
Most of the control scheme and game is not yet implemented.

    q or Escape: Quit the game
    r:           While held, randomly re-generate the ground terrain every frame.
    p:           While held, the game will stay paused.

## About ##
Jetpack-Man is a game created as a learning exercise.  The intent of this learning exercise is to create an efficient physics engine.

The physics engine uses line segments to represent all objects -- including the level.  It uses a priori/continuous form of collision detection, allowing the precise collision time to be calculated.  All object collisions are then stored into a minheap, and evaluated in the order they occur, when they occur.

When objects are moved, or have their acceleration, velocity, or position changed (not as a result of acceleration or velocity), such as via collision, all of their current collisions are invalidated, and new ones are recalculated.

In addition to creating an efficient physics engine, the game code is 'pythonic', should follow good coding practices, and the game itself should be fun to play.