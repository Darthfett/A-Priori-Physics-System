# TO DO #
 * Have Shape objects' shape attribute indicate objects' current positions
 * Move mapping of keyboard keys to controls into a config file
 * Move level definition into a file
 * Center the screen on the player
 * Investigate different cases for collision
    - Multiple collisions
    - Movement up a ramp
    - Standing on ground
    - Worst case scenarios

## Working Demo 1 ##
 * Evented/Observer API for entities and their mixin classes
    - Player movement
    - Player jumping
 * Levels loaded in as a file
    - Need a good format for this (PyON? JSON?)
 * Center the screen at Window.center_box.center
    - Scroll the screen center with the player
 * Collision resolution
