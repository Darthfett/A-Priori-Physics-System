# TO DO #
 * Shape class
    - Should indicate current position
    - Store ordered list of points (not lines)
       . bool 'open' to indicate last point connected to first
    - Support find intersections with another object
    - Color?
    
 * Move mapping of keyboard keys to controls into a config file
 * Move level definition into a file
 * Investigate different cases for collision
    - Multiple collisions
    - Movement up a ramp
    - Standing on ground
    - Worst case scenarios

## Working Demo 1 ##
 * Player jumping
 * Levels loaded in as a file
    - Need a good format for this (PyON? JSON?)
 * Center the screen at Window.center_box.center
    - Scroll the screen center with the player
 * Collision resolution
