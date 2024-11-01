import pyglet
from enum import Enum

class PlayerSprite(Enum):
    IDLE_LEFT = 'sprites/sonic_idle_left.aseprite'
    IDLE_RIGHT = 'sprites/sonic_idle_right.aseprite'
    RUN_LEFT = 'sprites/sonic_run_left_hold.aseprite'
    RUN_RIGHT = 'sprites/sonic_run_right_hold.aseprite'
    RUN_LEFT_START = 'sprites/sonic_run_left_click.aseprite'
    RUN_RIGHT_START = 'sprites/sonic_run_right_click.aseprite'
    CROUCH_LEFT = 'sprites/sonic_crouch_left.aseprite'
    CROUCH_RIGHT = 'sprites/sonic_crouch_right.aseprite'
    UP_LEFT = 'sprites/sonic_up_left_hold.aseprite'
    UP_RIGHT = 'sprites/sonic_up_right_hold.aseprite'
    UP_LEFT_START = 'sprites/sonic_up_left_click.aseprite'
    UP_RIGHT_START = 'sprites/sonic_up_right_click.aseprite'
    JUMP_LEFT = 'sprites/sonic_jump_left_hold.aseprite'
    JUMP_RIGHT = 'sprites/sonic_jump_right_hold.aseprite'
    JUMP_LEFT_START = 'sprites/sonic_jump_left_click.aseprite'
    JUMP_RIGHT_START = 'sprites/sonic_jump_right_click.aseprite'
    ATTACK_LEFT = 'sprites/sonic_attack_left.aseprite'    # procedurálne obrázky za sebou, útok stačí len držať a bude sa vykonávať kontinuálne, kým sa tlačítko na útok nepustí
    ATTACK_RIGHT = 'sprites/sonic_attack_right.aseprite'
    DASH_LEFT = 'sprites/sonic_dash_left.aseprite'
    DASH_RIGHT = 'sprites/sonic_dash_right.aseprite'

class Player:

    def __init__(self):
        self.image = pyglet.image.load(PlayerSprite.IDLE.value)
        self.sprite = pyglet.sprite.Sprite(self.image, x=100, y=100)

    def set_sprite(self, sprite_enum):
        self.image = pyglet.image.load(sprite_enum.value)
        self.sprite.image = self.image

    def draw(self):
        self.sprite.draw()

# Inicializácia Pygletu
player = Player()

def on_draw():
    player.draw()

# Simulácia zmeny spritu
def update(dt):
    player.set_sprite(PlayerSprite.RUNNING)

pyglet.clock.schedule_interval(update, 1/60.0)  # 60 FPS
pyglet.app.run()
