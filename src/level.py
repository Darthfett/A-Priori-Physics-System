import os

import pygame
import random

from util import Vector, Shape, Rect, generate_circle
import physics
import entity
import entities

import json

DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480

class Level:
    def __init__(self, entities_=None, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
        if entities_ is None:
            entities_ = []
        self.entities = entities_
        self.width = width
        self.height = height

def load(level_path):
    with open(level_path, 'r') as level_file:
        level_json = json.load(level_file)
    width = level_json.get('width', DEFAULT_WIDTH)
    height = level_json.get('height', DEFAULT_HEIGHT)

    type_mapper = {
        'Player': entities.Player,
        'Ground': entities.Ground
    }

    entities_data = level_json.get('entities', [])
    entities_ = []
    for ent in entities_data:
        type_ = ent['type']
        if type_ not in type_mapper:
            print('Invalid type for entity in level {level_path}: {entity}'.format(level_path=level_path, entity=ent))
            continue
        del ent['type']
        entities_.append(type_mapper[type_](**ent))

    return Level(entities, width=width, height=height)

class LevelLoader:
    pass