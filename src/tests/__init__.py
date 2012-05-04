import unittest
import importlib

__all__ = ["vector"]

def load_tests(loader, tests, pattern):
    modules = [importlib.import_module('.'.join(['tests', module])) for module in __all__]
    for module in modules:
        tests.addTests(loader.loadTestsFromModule(module))
    return tests

def run():
    results = []
    suite = load_tests(unittest.defaultTestLoader, unittest.TestSuite(), None)
    unittest.TextTestRunner(verbosity=1).run(suite)

if __name__ == "__main__":
    run()