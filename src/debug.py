
_DebugMode = False

class _Debug:

    def __bool__(self):
        return _DebugMode
    
    def __getattribute__(self, name):
        return object.__getattribute__(self, name) and _DebugMode

    def __init__(self):
        self.DrawOutlines = True

Debug = _Debug()