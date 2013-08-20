"""
The entities module contains all user-defined entity objects.  They are
typically derived from classes in the entity module.

Classes:
  Player                An entity that is controlled by the player.

"""

import entity

# Resolve namespace of Player to improve the namespace access
from entities.player import Player