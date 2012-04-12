"""
The Debug module provides some basic information on managing the debugging
state of the game.

globals:
  Debug                         An object used to determining debugging state.
                                Returns a truthy value in a boolean context.

"""
_DebugMode = False

class _Debug:
    """
    Represents the debugging state of the game.
    
    properties:
      DrawOutlines              If in a debugging state, returns whether the game
                                should draw outlines of Drawables instead of
                                blitting them to the screen.
    
    """
    
    def __bool__(self):
        return _DebugMode
    
    def __getattribute__(self, name):
        return object.__getattribute__(self, name) and _DebugMode

    def __init__(self):
        self.DrawOutlines = True

Debug = _Debug()