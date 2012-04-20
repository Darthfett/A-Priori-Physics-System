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
    
    def write(self, text, file=None):
        if not self:
            return
        if file is not None:
            if file not in self._files:
                with open(file, 'w') as f:
                    f.write(text)
                self._files.add(file)
            else:
                with open(file, 'a') as f:
                    f.write(text)
        else:
            if self._file is None:
                self._file = open('dbg.txt', 'w')
            self._file.write(text)
    
    def __bool__(self):
        return _DebugMode

    def __init__(self):
        self.DrawOutlines = True
        self._files = set()

debug = _Debug()