import argparse

import tests

parser = argparse.ArgumentParser(description='Runs the test suite', usage='python -m tests [options]')

parser.add_argument('--v', help='change the verbose-ness level', dest='v', default=1, type=int)
                        
args = parser.parse_args()
tests.run(args.v)