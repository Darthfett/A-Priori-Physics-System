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
    
    def write(self, text):
        self._file.write(text)
    
    def __bool__(self):
        return _DebugMode
    
    def __getattribute__(self, name):
        if isinstance(object.__getattribute__(self, name), bool):
            return object.__getattribute__(self, name) and _DebugMode
        else:
            return object.__getattribute__(self, name)

    def __init__(self):
        self.DrawOutlines = True
        self._file = open('dbg.txt', 'w')

debug = _Debug()