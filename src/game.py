import pygame
from window import Window
from util import *

Screen = None
NAME = "Jetpack Man"
Gravity = Vector(0, -9.81)

def run():
    Screen = Window(NAME) # Accept default size