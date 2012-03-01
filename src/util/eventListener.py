"""

"""

def _setattr_wrapper(cls):
    """Creates a wrapper around the __setattr__ for the class cls."""
    def watcher_setattr(self, attr, val):
        """A wrapper around __setattr__ to run any methods watching attributes."""
        #getattr(self, attr)
        watched = cls.__dict__["_watched"]
        if attr in watched:
            for method in watched[attr]:
                getattr(self, method)(val)
        super(cls, self).__setattr__(attr, val)
    return watcher_setattr

class EventListener(type):
    """Classes that extend the EventListener class can have methods that watch
    attributes for changes using the @watch(attribute) decorator."""
    def __new__(metacls, name, bases, dct):
        """Create a _watched dict to map watched attributes to their watching methods."""
        dct["_watched"] = {}
        for key, value in dct.items():
            if hasattr(value, "_watched"):
                attr = getattr(value, "_watched")
                if not attr in dct["_watched"]:
                    dct["_watched"][attr] = set()
                dct["_watched"][attr].add(key)
        cls = type.__new__(metacls, name, bases, dct)
        cls.__setattr__ = _setattr_wrapper(cls)
        return cls


def watch(attr):
    """Use @watch(attribute) to have a method called whenever any attribute shall change."""
    def decorator(meth):
        """Adds an attribute to the list of watched attributes."""
        setattr(meth, "_watched", attr)
        return meth
    return decorator


if __name__ == "__main__":
    import unittest

    class BaconTest:
        def __init__(self, bacon = None, **kwargs):
            self.bacon = bacon

    class WatchTest(BaconTest, metaclass=EventListener):
        @watch("bacon")
        def set_bacon(self, bacon):
            self.received = bacon
        
        def __init__(self, **kwargs):
            self.received = None
            super().__init__(**kwargs)            
    
    class TestEventListener(unittest.TestCase):
        
        def setUp(self):
            self.watch = WatchTest()
        
        def test_set(self):
            self.watch.bacon = 5
            self.assertTrue(self.watch.bacon == 5)
        
        def test_watch(self):
            self.watch.bacon = 23
            self.assertTrue(self.watch.received == 23)
            
            
    unittest.main()