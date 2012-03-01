# Jetpack-Man #

## Requirements ##
 - Python 3.2
 - Pygame (1.9.2a0 or higher)

## How to run ##
```python src/main.py```

## About ##
Jetpack-Man is a game created as a learning exercise.  The intent of this learning exercise is to create an efficient physics engine.

The physics engine uses line segments to represent all objects -- including the level.  It uses a priori/continuous form of collision detection, allowing the precise collision time to be calculated.  All object collisions are then stored into a minheap, and evaluated in the order they occur, when they occur.

When objects are moved, or have their acceleration, velocity, or position changed (not as a result of acceleration or velocity), such as via collision, all of their current collisions are invalidated, and new ones are recalculated.

In addition to creating an efficient physics engine, the game code is 'pythonic', should follow good coding practices, and the game itself should be fun to play.

## Controls ##
Most of the control scheme and game is not yet implemented.

You can currently press 'r' to randomly regenerate the ground terrain.