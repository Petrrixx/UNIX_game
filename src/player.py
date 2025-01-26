import pyglet
from enum import Enum
from pyglet.window import key
import os
from pyglet import shapes
import aseprite.aseprite as aseprite

# Debug výpisy pre import
print("Aseprite module path:", aseprite.__file__)
print("Aseprite module attributes:", dir(aseprite))

# Načítanie Aseprite dekóderov
pyglet.image.codecs.add_decoders(aseprite)
batch = pyglet.graphics.Batch()
SPRITES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../aseprite/sprites'))


class PlayerSprite(Enum):
    IDLE_LEFT = os.path.join(SPRITES_PATH, 'sonic_idle_left.aseprite')
    IDLE_RIGHT = os.path.join(SPRITES_PATH, 'sonic_idle_right.aseprite')
    RUN_LEFT = os.path.join(SPRITES_PATH, 'sonic_run_left.aseprite')
    RUN_RIGHT = os.path.join(SPRITES_PATH, 'sonic_run_right.aseprite')
    CROUCH_LEFT = os.path.join(SPRITES_PATH, 'sonic_crouch_left.aseprite')
    CROUCH_RIGHT = os.path.join(SPRITES_PATH, 'sonic_crouch_right.aseprite')
    JUMP_LEFT = os.path.join(SPRITES_PATH, 'sonic_jump_left.aseprite')
    JUMP_RIGHT = os.path.join(SPRITES_PATH, 'sonic_jump_right.aseprite')
    ATTACK_LEFT = os.path.join(SPRITES_PATH, 'sonic_attack_left.aseprite')
    ATTACK_RIGHT = os.path.join(SPRITES_PATH, 'sonic_attack_right.aseprite')
    JUMP_ATTACK_LEFT = os.path.join(SPRITES_PATH, 'sonic_jump_attack_left.aseprite')
    JUMP_ATTACK_RIGHT = os.path.join(SPRITES_PATH, 'sonic_jump_attack_right.aseprite')
    SPECIAL_ATTACK_LEFT = os.path.join(SPRITES_PATH, 'sonic_spatk_left.aseprite')
    SPECIAL_ATTACK_RIGHT = os.path.join(SPRITES_PATH, 'sonic_spatk_right.aseprite')
    DASH_LEFT = os.path.join(SPRITES_PATH, 'sonic_dash_left.aseprite')
    DASH_RIGHT = os.path.join(SPRITES_PATH, 'sonic_dash_right.aseprite')
    LOOK_UP_LEFT = os.path.join(SPRITES_PATH, 'sonic_up_left_click.aseprite')
    LOOK_UP_RIGHT = os.path.join(SPRITES_PATH, 'sonic_up_right_click.aseprite')
    LOOK_UP_LEFT_HOLD = os.path.join(SPRITES_PATH, 'sonic_up_left_hold.aseprite')
    LOOK_UP_RIGHT_HOLD = os.path.join(SPRITES_PATH, 'sonic_up_right_hold.aseprite')
    UP_ABILITY_LEFT = os.path.join(SPRITES_PATH, 'sonic_up_ability_left.aseprite')
    UP_ABILITY_RIGHT = os.path.join(SPRITES_PATH, 'sonic_up_ability_right.aseprite')
    GAME_OVER = os.path.join(SPRITES_PATH, 'sonic_game_over.aseprite')


class Player:
    MAX_SPEED = 300  # Maximálna rýchlosť (px/s)
    ACCELERATION = 600  # Akcelerácia (px/s²)
    DECELERATION = 800  # Deakcelerácia (px/s²)
    JUMP_VELOCITY = 500  # Počiatočná rýchlosť skoku (px/s)
    GRAVITY = -1500  # Gravitácia (px/s²)
    HITBOX_WIDTH = 148
    HITBOX_HEIGHT = 180

    def __init__(self):
        self.x = 100
        self.y = 300
        self.velocity_x = 0
        self.velocity_y = 0
        self.current_action = PlayerSprite.IDLE_RIGHT
        self.animation = self.load_animation(self.current_action)
        self.sprite = pyglet.sprite.Sprite(self.animation, x=self.x, y=self.y, batch=batch)
        if self.animation:
            for frame in self.animation.frames:
                frame.image.get_texture().mag_filter = pyglet.gl.GL_NEAREST
        self.hitbox = shapes.Rectangle(self.x, self.y, self.HITBOX_WIDTH, self.HITBOX_HEIGHT, color=(50, 50, 255))
        self.is_jumping = False
        self.direction = 'right'

        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False

        self.active_movement_keys = []
        self.active_action_keys = []
        self.look_up_scheduled = False

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.sprite.x = self.x
        self.sprite.y = self.y

    def load_animation(self, action):
        try:
            animation = pyglet.image.load_animation(action.value)
            print(f"Loaded animation {action.name} with {len(animation.frames)} frames.")
            for i, frame in enumerate(animation.frames):
                print(f"Frame {i}: duration={frame.duration}")
                frame.image.get_texture().mag_filter = pyglet.gl.GL_NEAREST
            return animation
        except Exception as e:
            print(f"Error loading animation {action.name}: {e}")
            return None

    def set_action(self, action):
        if self.current_action != action:
            print(f"Changing action from {self.current_action.name} to {action.name}")
            self.current_action = action
            self.animation = self.load_animation(self.current_action)
            if self.animation:
                self.sprite.image = self.animation
            else:
                print(f"Failed to set animation for {action.name}")

    def move_right(self):
        self.moving_right = True
        self.direction = 'right'
        self.set_action(PlayerSprite.RUN_RIGHT)

    def move_left(self):
        self.moving_left = True
        self.direction = 'left'
        self.set_action(PlayerSprite.RUN_LEFT)

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = self.JUMP_VELOCITY
            if self.direction == 'right':
                self.set_action(PlayerSprite.JUMP_RIGHT)
            else:
                self.set_action(PlayerSprite.JUMP_LEFT)

    def crouch(self):  # ZMENA: Metóda crouch je už definovaná, ale pripomenieme jej použitie
        if self.direction == 'right':
            self.set_action(PlayerSprite.CROUCH_RIGHT)
        else:
            self.set_action(PlayerSprite.CROUCH_LEFT)

    def stop_moving_left(self):
        self.moving_left = False

    def stop_moving_right(self):
        self.moving_right = False

    def look_up(self):
        if self.direction == 'right':
            self.set_action(PlayerSprite.LOOK_UP_RIGHT)
        else:
            self.set_action(PlayerSprite.LOOK_UP_LEFT)

        if not self.look_up_scheduled:
            pyglet.clock.schedule_once(self.set_hold_animation, 0.2)
            self.look_up_scheduled = True

    def set_hold_animation(self, dt):
        if self.direction == 'right':
            self.set_action(PlayerSprite.LOOK_UP_RIGHT_HOLD)
        else:
            self.set_action(PlayerSprite.LOOK_UP_LEFT_HOLD)
        self.look_up_scheduled = False

    def stop_look_up(self):
        if self.look_up_scheduled:
            pyglet.clock.unschedule(self.set_hold_animation)
            self.look_up_scheduled = False

        if not self.moving_left and not self.moving_right and not self.is_jumping:
            self.set_action(PlayerSprite.IDLE_RIGHT if self.direction == 'right' else PlayerSprite.IDLE_LEFT)
        else:
            self.set_action(PlayerSprite.RUN_RIGHT if self.direction == 'right' else PlayerSprite.RUN_LEFT)

    # ZMENA: Pridanie metódy stop_crouch na návrat do predchádzajúcej animácie pri uvoľnení C
    def stop_crouch(self):
        """Prestane sa skláňať."""
        if not self.moving_left and not self.moving_right and not self.is_jumping and 'E' not in self.active_action_keys:
            self.set_action(PlayerSprite.IDLE_RIGHT if self.direction == 'right' else PlayerSprite.IDLE_LEFT)
        elif 'E' in self.active_action_keys:
            self.look_up()
        else:
            self.set_action(PlayerSprite.RUN_RIGHT if self.direction == 'right' else PlayerSprite.RUN_LEFT)

    def update_action_based_on_movement_keys(self):
        if not self.active_movement_keys:
            if not self.is_jumping and 'E' not in self.active_action_keys and 'C' not in self.active_action_keys:
                self.set_action(PlayerSprite.IDLE_RIGHT if self.direction == 'right' else PlayerSprite.IDLE_LEFT)
            elif 'E' in self.active_action_keys:
                self.look_up()
            elif 'C' in self.active_action_keys:
                self.crouch()
            return

        last_key = self.active_movement_keys[-1]
        if last_key == key.D:
            self.move_right()
        elif last_key == key.A:
            self.move_left()
        elif last_key == key.W:
            self.moving_up = True
        elif last_key == key.S:
            self.moving_down = True

    def update(self, dt):
        if self.moving_right:
            self.velocity_x += self.ACCELERATION * dt
            if self.velocity_x > self.MAX_SPEED:
                self.velocity_x = self.MAX_SPEED
        elif self.moving_left:
            self.velocity_x -= self.ACCELERATION * dt
            if self.velocity_x < -self.MAX_SPEED:
                self.velocity_x = -self.MAX_SPEED
        else:
            if self.velocity_x > 0:
                self.velocity_x -= self.DECELERATION * dt
                if self.velocity_x < 0:
                    self.velocity_x = 0
            elif self.velocity_x < 0:
                self.velocity_x += self.DECELERATION * dt
                if self.velocity_x > 0:
                    self.velocity_x = 0

            if self.velocity_x == 0 and not self.is_jumping and not self.active_action_keys:
                self.set_action(PlayerSprite.IDLE_RIGHT if self.direction == 'right' else PlayerSprite.IDLE_LEFT)

        if self.is_jumping:
            self.velocity_y += self.GRAVITY * dt
            self.y += self.velocity_y * dt

            if self.y <= 300:
                self.y = 300
                self.is_jumping = False
                self.velocity_y = 0
                if not self.moving_left and not self.moving_right and not self.active_action_keys:
                    self.set_action(PlayerSprite.IDLE_RIGHT if self.direction == 'right' else PlayerSprite.IDLE_LEFT)
                else:
                    self.set_action(PlayerSprite.RUN_RIGHT if self.direction == 'right' else PlayerSprite.RUN_LEFT)
        else:
            if self.moving_up:
                self.y += 100 * dt
            if self.moving_down:
                self.y -= 100 * dt

        self.x += self.velocity_x * dt
        self.x = max(0, min(self.x, window.width - self.sprite.width))
        self.y = max(0, min(self.y, window.height - self.sprite.height))

        self.sprite.x = self.x
        self.sprite.y = self.y
        self.hitbox.x = self.x
        self.hitbox.y = self.y

    def draw(self):
        self.sprite.draw()

    def freeze_animation(self, frame_index):
        """Zastaví animáciu na konkrétnom frame."""
        if frame_index < len(self.animation.frames):
            frame = self.animation.frames[frame_index]
            self.sprite.image = frame.image
            print(f"Frozen animation at frame {frame_index}.")
        else:
            print(f"Frame index {frame_index} out of range.")

    def set_custom_loop(self, frame_indices):
        """Nastaví vlastný loop frameov."""
        from pyglet.image import Animation, AnimationFrame

        selected_frames = [
            AnimationFrame(self.animation.frames[i].image, self.animation.frames[i].duration)
            for i in frame_indices if i < len(self.animation.frames)
        ]

        if selected_frames:
            self.sprite.image = Animation(selected_frames)
            print(f"Custom loop set with frames: {frame_indices}.")
        else:
            print("No valid frames selected for custom loop.")


window = pyglet.window.Window(1920, 1080)
player = Player()


@window.event
def on_key_press(symbol, modifiers):
    # ZMENA: Pridali sme key.C pre crouch
    if symbol in (key.W, key.A, key.S, key.D, key.E, key.C):
        if symbol in (key.W, key.A, key.S, key.D):
            if symbol not in player.active_movement_keys and len(player.active_movement_keys) < 1:
                player.active_movement_keys.append(symbol)
                if symbol == key.D:
                    player.move_right()
                elif symbol == key.A:
                    player.move_left()
                elif symbol == key.W:
                    player.moving_up = True
                elif symbol == key.S:
                    player.moving_down = True

        elif symbol == key.E:
            if symbol not in player.active_action_keys:
                player.active_action_keys.append('E')
                player.look_up()

        # ZMENA: Akčný kláves C pre crouch
        elif symbol == key.C:
            if 'C' not in player.active_action_keys:
                player.active_action_keys.append('C')
                player.crouch()


@window.event
def on_key_release(symbol, modifiers):
    if symbol in (key.W, key.A, key.S, key.D, key.E, key.C):
        if symbol in (key.W, key.A, key.S, key.D):
            if symbol in player.active_movement_keys:
                player.active_movement_keys.remove(symbol)
                if symbol == key.D:
                    player.stop_moving_right()
                elif symbol == key.A:
                    player.stop_moving_left()
                elif symbol == key.W:
                    player.moving_up = False
                elif symbol == key.S:
                    player.moving_down = False
                player.update_action_based_on_movement_keys()

        elif symbol == key.E:
            if 'E' in player.active_action_keys:
                player.active_action_keys.remove('E')
                player.stop_look_up()

        # ZMENA: Uvoľnenie klávesy C
        elif symbol == key.C:
            if 'C' in player.active_action_keys:
                player.active_action_keys.remove('C')
                player.stop_crouch()


@window.event
def on_draw():
    window.clear()
    batch.draw()


def update(dt):
    player.update(dt)


pyglet.clock.schedule_interval(update, 1 / 60.0)
pyglet.app.run()
