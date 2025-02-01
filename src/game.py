import os
import pyglet
from pyglet.window import key
import aseprite.aseprite as aseprite

# Zaregistrujeme Aseprite dekóder, aby pyglet vedel spracovať .aseprite súbory.
pyglet.image.codecs.add_decoders(aseprite)


# === Resource Manager ===
class ResourceManager:
    _cache = {}

    @staticmethod
    def get_animation(file_path):
        if file_path in ResourceManager._cache:
            return ResourceManager._cache[file_path]
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            fallback_img = pyglet.image.SolidColorImagePattern(color=(255, 0, 0, 255)).create_image(64, 64)
            fallback_anim = pyglet.image.Animation([pyglet.image.AnimationFrame(fallback_img, 1.0)])
            ResourceManager._cache[file_path] = fallback_anim
            return fallback_anim
        try:
            anim = pyglet.image.load_animation(file_path)
            for frame in anim.frames:
                frame.image.get_texture().mag_filter = pyglet.gl.GL_NEAREST
            ResourceManager._cache[file_path] = anim
            print(f"Animation loaded and cached: {file_path}")
            return anim
        except Exception as e:
            print(f"Error loading animation '{file_path}': {e}")
            fallback_img = pyglet.image.SolidColorImagePattern(color=(255, 0, 0, 255)).create_image(64, 64)
            fallback_anim = pyglet.image.Animation([pyglet.image.AnimationFrame(fallback_img, 1.0)])
            ResourceManager._cache[file_path] = fallback_anim
            return fallback_anim


# === Background Class ===
class Background:
    def __init__(self, file_path, batch):
        self.file_path = file_path
        self.batch = batch
        self.sprite = None
        self.loaded = False
        display = pyglet.canvas.Display()
        screen = display.get_default_screen()
        self.placeholder = pyglet.shapes.Rectangle(0, 0, screen.width, screen.height,
                                                     color=(0, 0, 0), batch=self.batch)
        pyglet.clock.schedule_once(self.load_background, 0)

    def load_background(self, dt):
        anim = ResourceManager.get_animation(self.file_path)
        if anim:
            self.sprite = pyglet.sprite.Sprite(anim, x=0, y=0, batch=self.batch)
            self.loaded = True
            self.placeholder.delete()
            print("Background successfully loaded.")
        else:
            print("Failed to load background animation.")

    def update(self, dt):
        pass

    def draw(self):
        if self.sprite:
            self.sprite.draw()
        else:
            self.placeholder.draw()


# === Player Sprite Enumeration ===
class PlayerSprite:
    # Uprav si cestu podľa svojej štruktúry.
    SPRITES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../aseprite/sprites'))
    IDLE_LEFT    = os.path.join(SPRITES_PATH, 'sonic_idle_left.aseprite')
    IDLE_RIGHT   = os.path.join(SPRITES_PATH, 'sonic_idle_right.aseprite')
    RUN_LEFT     = os.path.join(SPRITES_PATH, 'sonic_run_left.aseprite')
    RUN_RIGHT    = os.path.join(SPRITES_PATH, 'sonic_run_right.aseprite')
    JUMP_LEFT    = os.path.join(SPRITES_PATH, 'sonic_jump_left.aseprite')
    JUMP_RIGHT   = os.path.join(SPRITES_PATH, 'sonic_jump_right.aseprite')


# === Player Class ===
class Player:
    # Zvýšené hodnoty pre rýchlosť, zrýchlenie, spomalenie a skok.
    MAX_SPEED = 500       # zvýšená maximálna rýchlosť
    ACCELERATION = 800    # rýchlejšie zrýchlenie
    DECELERATION = 1000   # rýchlejšie spomalenie
    JUMP_VELOCITY = 800    # vyšší skok
    GRAVITY = -2000       # o niečo silnejšia gravitácia
    HITBOX_WIDTH = 148
    HITBOX_HEIGHT = 180

    def __init__(self, batch, window):
        self.batch = batch
        self.window = window  # Pre obmedzenie pohybu
        self.animations = {}
        for attr in dir(PlayerSprite):
            if not attr.startswith("__") and attr.isupper():
                value = getattr(PlayerSprite, attr)
                if isinstance(value, str) and value.lower().endswith(".aseprite"):
                    anim = ResourceManager.get_animation(value)
                    if anim:
                        self.animations[attr] = anim
                    else:
                        print(f"Animation '{attr}' failed to load.")
        self.x = 100
        self.y = 300
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = 'right'
        self.is_jumping = False
        self.jump_timer = 0
        self.current_action = 'IDLE_RIGHT'
        self.animation = self.animations.get(self.current_action)
        if self.animation is None:
            fallback_img = pyglet.image.SolidColorImagePattern(color=(0, 255, 0, 255)).create_image(64, 64)
            self.animation = pyglet.image.Animation([pyglet.image.AnimationFrame(fallback_img, 1.0)])
        self.sprite = pyglet.sprite.Sprite(self.animation, x=self.x, y=self.y, batch=self.batch)
        self.active_movement_keys = set()
        # Premenná pre kontrolu držania jump tlačítka.
        self.jump_held = False

    def set_action(self, action_key):
        # Ak Sonic je vo vzduchu a chceme nastaviť jump animáciu, povolíme to.
        if self.is_jumping and not action_key.startswith("JUMP_"):
            return
        if self.current_action != action_key:
            self.current_action = action_key
            anim = self.animations.get(action_key)
            if anim:
                self.sprite.image = anim
                print(f"Switched action to {action_key}")
            else:
                print(f"Animation for {action_key} not found in cache.")

    def move_right(self):
        self.active_movement_keys.add('RIGHT')
        self.direction = 'right'
        if not self.is_jumping:
            self.set_action('RUN_RIGHT')

    def move_left(self):
        self.active_movement_keys.add('LEFT')
        self.direction = 'left'
        if not self.is_jumping:
            self.set_action('RUN_LEFT')

    def jump(self):
        # Skok je povolen len ak Sonic je na zemi (y == 300) a nie je už v skoku.
        if self.is_jumping or self.y != 300:
            return
        self.is_jumping = True
        self.jump_timer = 1.0  # Jump animácia hrá aspoň 1 sekundu.
        self.velocity_y = self.JUMP_VELOCITY
        self.jump_held = True  # Predpokladáme, že pri stlačení jump tlačítka je jump držiavaný.
        if self.direction == 'right':
            self.set_action('JUMP_RIGHT')
        else:
            self.set_action('JUMP_LEFT')

    def update(self, dt):
        # Ak je Sonic v skoku, odpočítavame jump_timer.
        if self.is_jumping:
            self.jump_timer -= dt

        # Horizontálny pohyb
        if 'RIGHT' in self.active_movement_keys:
            self.velocity_x += self.ACCELERATION * dt
            if self.velocity_x > self.MAX_SPEED:
                self.velocity_x = self.MAX_SPEED
        elif 'LEFT' in self.active_movement_keys:
            self.velocity_x -= self.ACCELERATION * dt
            if self.velocity_x < -self.MAX_SPEED:
                self.velocity_x = -self.MAX_SPEED
        else:
            if self.velocity_x > 0:
                self.velocity_x -= self.DECELERATION * dt
                if self.velocity_x < 1:
                    self.velocity_x = 0
            elif self.velocity_x < 0:
                self.velocity_x += self.DECELERATION * dt
                if self.velocity_x > -1:
                    self.velocity_x = 0
            if self.velocity_x == 0 and not self.is_jumping:
                self.set_action('IDLE_RIGHT' if self.direction == 'right' else 'IDLE_LEFT')

        # Vertikálny pohyb (skok a gravitácia)
        if self.is_jumping:
            # Ak je jump tlačítko držané, použijeme nižšiu gravitáciu pre vyšší skok.
            effective_gravity = self.GRAVITY if not self.jump_held else self.GRAVITY * 0.5
            self.velocity_y += effective_gravity * dt
            next_y = self.y + self.velocity_y * dt
            if next_y < 300 and self.jump_timer <= 0:
                self.y = 300
                self.is_jumping = False
                self.velocity_y = 0
                self.jump_held = False
                if self.active_movement_keys:
                    self.set_action('RUN_RIGHT' if self.direction == 'right' else 'RUN_LEFT')
                else:
                    self.set_action('IDLE_RIGHT' if self.direction == 'right' else 'IDLE_LEFT')
            else:
                self.y = next_y

        self.x += self.velocity_x * dt

        window_width = self.window.width
        window_height = self.window.height
        self.x = max(0, min(self.x, window_width - self.sprite.width))
        self.y = max(0, min(self.y, window_height - self.sprite.height))
        self.sprite.x = self.x
        self.sprite.y = self.y

    def on_key_press(self, symbol, modifiers):
        # Ak je Sonic vo vzduchu, pri stlačení D/A aktualizujeme len rýchlosť a smer.
        if self.is_jumping and symbol in (key.D, key.A):
            if symbol == key.D:
                self.active_movement_keys.add('RIGHT')
                self.direction = 'right'
            elif symbol == key.A:
                self.active_movement_keys.add('LEFT')
                self.direction = 'left'
            return

        if symbol == key.D:
            self.move_right()
        elif symbol == key.A:
            self.move_left()
        elif symbol == key.SPACE:
            self.jump()

    def on_key_release(self, symbol, modifiers):
        if symbol == key.D:
            self.active_movement_keys.discard('RIGHT')
        elif symbol == key.A:
            self.active_movement_keys.discard('LEFT')
        elif symbol == key.SPACE:
            self.jump_held = False  # Keď uvoľníš jump tlačítko, prestaneš ho držať.


# === Game Class ===
class Game:
    def __init__(self):
        self.window = pyglet.window.Window(fullscreen=True, caption="Sonic Game")
        self.background_batch = pyglet.graphics.Batch()
        self.foreground_batch = pyglet.graphics.Batch()
        self.background_path = os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '../aseprite/sprites')),
            'sunsethill_animated.gif'
        )
        self.background = Background(self.background_path, self.background_batch)
        self.player = Player(self.foreground_batch, self.window)
        self.window.push_handlers(self)
        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

    def on_draw(self):
        self.window.clear()
        self.background_batch.draw()
        self.foreground_batch.draw()

    def on_key_press(self, symbol, modifiers):
        self.player.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.player.on_key_release(symbol, modifiers)

    def update(self, dt):
        self.player.update(dt)
        self.background.update(dt)

    def run(self):
        pyglet.app.run()


if __name__ == '__main__':
    game = Game()
    game.run()
