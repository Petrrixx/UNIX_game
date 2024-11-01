import pyglet
import random
from pyglet import gl

class MapGenerator:
    def __init__(self, width, height, tile_size):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.map = self.generate_map()

    def generate_map(self):
        return [[random.choice([0, 1]) for _ in range(self.width)] for _ in range(self.height)]

