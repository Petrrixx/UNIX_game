import pyglet
from pyglet import resource
import player as player
import map_generator as map_gen
import sound_manager as sounds
import utils as utils
import aseprite.aseprite as aseprite


class Game:
    def __init__(self):
        self.window = pyglet.window.Window(800, 600, "Sonic Game")
        self.player = player.Player()
        self.map_generator = map_gen.MapGenerator(25, 20, 32)
        self.window.push_handlers(self)

    def on_draw(self):
        self.window.clear()
        self.map_generator.draw()
        self.player.draw()

    def update(self, dt):
        self.player.update(dt)


    def on_key_press(self, symbol, modifiers):

        if symbol == pyglet.window.key.LEFT:
            self.player.move_left()
        elif symbol == pyglet.window.key.RIGHT:
            self.player.move_right()
        elif symbol == pyglet.window.key.UP:
            self.player.jump()  # Assuming you have a jump method

    def on_key_release(self, symbol, modifiers):

        if symbol in (pyglet.window.key.LEFT, pyglet.window.key.RIGHT):
            self.player.stop_movement()

    def run(self):
        pyglet.clock.schedule_interval(self.update, 1 / 60)  # 60 FPS
        pyglet.app.run()


if __name__ == "__main__":
    game = Game()
    game.run()
