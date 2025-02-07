import os
import random
import pyglet
from pyglet.window import key
import aseprite.aseprite as aseprite
from pyglet import math  # Pre prácu s maticami
from pyglet.gl import *  # Pre prípadné použitie OpenGL

# Zaregistrujeme Aseprite dekóder:
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

# === DamageText Class ===
class DamageText:
    def __init__(self, text, x, y, duration=1.0):
        self.text = text
        self.x = x
        self.y = y
        self.duration = duration
        self.timer = duration
        self.label = pyglet.text.Label(
            text,
            font_name='Arial',
            font_size=24,
            x=x,
            y=y,
            anchor_x='center',
            anchor_y='center',
            color=(255, 0, 0, 255)
        )
    def update(self, dt):
        self.timer -= dt
    def draw(self):
        if self.timer > 0:
            self.label.draw()

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
            self.sprite = pyglet.sprite.Sprite(anim, x=0, y=-100, batch=self.batch)
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

# === Ground Class ===
class Ground:
    def __init__(self, file_path, batch, y_position):
        self.sprite = pyglet.sprite.Sprite(pyglet.image.load(file_path), x=0, y=y_position, batch=batch)
    def draw(self):
        self.sprite.draw()

# === Player Sprite Enumeration ===
class PlayerSprite:
    SPRITES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../aseprite/sprites'))
    IDLE_LEFT    = os.path.join(SPRITES_PATH, 'sonic_idle_left.aseprite')
    IDLE_RIGHT   = os.path.join(SPRITES_PATH, 'sonic_idle_right.aseprite')
    RUN_LEFT     = os.path.join(SPRITES_PATH, 'sonic_run_left.aseprite')
    RUN_RIGHT    = os.path.join(SPRITES_PATH, 'sonic_run_right.aseprite')
    JUMP_LEFT    = os.path.join(SPRITES_PATH, 'sonic_jump_left.aseprite')
    JUMP_RIGHT   = os.path.join(SPRITES_PATH, 'sonic_jump_right.aseprite')

# === Player Class ===
class Player:
    MAX_SPEED = 800
    ACCELERATION = 800
    DECELERATION = 1000
    JUMP_VELOCITY = 800
    GRAVITY = -1500
    HITBOX_WIDTH = 148
    HITBOX_HEIGHT = 180
    def __init__(self, batch, window):
        self.batch = batch
        self.window = window
        self.animations = {}
        for attr in dir(PlayerSprite):
            if not attr.startswith("__") and attr.isupper():
                value = getattr(PlayerSprite, attr)
                if isinstance(value, str) and value.lower().endswith(".aseprite"):
                    anim = ResourceManager.get_animation(value)
                    if anim:
                        self.animations[attr] = anim
        self.x = 1100
        self.y = 300
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = 'right'
        self.is_jumping = False
        self.jump_timer = 0
        self.current_action = 'IDLE_RIGHT'
        self.animation = self.animations.get(self.current_action)
        if self.animation is None:
            fallback_img = pyglet.image.SolidColorImagePattern(color=(0,255,0,255)).create_image(64,64)
            self.animation = pyglet.image.Animation([pyglet.image.AnimationFrame(fallback_img, 1.0)])
        self.sprite = pyglet.sprite.Sprite(self.animation, x=self.x, y=self.y, batch=self.batch)
        self.sprite.anchor_x = 0
        self.sprite.anchor_y = 0
        self.active_movement_keys = set()
        self.jump_held = False
        self.hit_cooldown = 0  # Cooldown pred ďalším zásahom

    def set_action(self, action_key):
        if self.is_jumping and not action_key.startswith("JUMP_"):
            return
        if self.current_action != action_key:
            self.current_action = action_key
            anim = self.animations.get(action_key)
            if anim:
                self.sprite.image = anim
                print(f"Switched action to {action_key}")

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
        if self.is_jumping or self.y != 300:
            return
        self.is_jumping = True
        self.jump_timer = 1.0
        self.velocity_y = self.JUMP_VELOCITY
        self.jump_held = True
        if self.direction == 'right':
            self.set_action('JUMP_RIGHT')
        else:
            self.set_action('JUMP_LEFT')

    def update(self, dt):
        if self.hit_cooldown > 0:
            self.hit_cooldown -= dt
            if self.hit_cooldown < 0:
                self.hit_cooldown = 0
        if self.is_jumping:
            self.jump_timer -= dt
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
        if self.is_jumping:
            effective_gravity = self.GRAVITY if not self.jump_held else self.GRAVITY * 0.5
            self.velocity_y += effective_gravity * dt
            self.y += self.velocity_y * dt
            if self.y <= 300 and self.jump_timer <= 0:
                self.y = 300
                self.is_jumping = False
                self.velocity_y = 0
                self.jump_held = False
                if self.active_movement_keys:
                    self.set_action('RUN_RIGHT' if self.direction == 'right' else 'RUN_LEFT')
                else:
                    self.set_action('IDLE_RIGHT' if self.direction == 'right' else 'IDLE_LEFT')
        self.x += self.velocity_x * dt
        window_width = self.window.width
        window_height = self.window.height
        self.x = max(1000, min(self.x, 3400 - self.sprite.width))
        self.y = max(0, min(self.y, window_height - self.sprite.height))
        self.sprite.x = self.x
        self.sprite.y = self.y

    def on_key_press(self, symbol, modifiers):
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
            self.jump_held = False

# === Ring Class ===
class Ring:
    def __init__(self, file_path, batch, x, y):
        self.sprite = pyglet.sprite.Sprite(ResourceManager.get_animation(file_path), x=x, y=y, batch=batch)
        self.x = x
        self.y = y
        self.width = self.sprite.width
        self.height = self.sprite.height
        self.collected = False
    def update(self, dt):
        pass
    def draw(self):
        if not self.collected:
            self.sprite.draw()
    def get_hitbox(self):
        return (self.x, self.y, self.x + self.width, self.y + self.sprite.height)

# === Rings Manager ===
class RingsManager:
    def __init__(self, file_path, batch, ground_y, count=6):
        self.rings = []
        self.batch = batch
        self.collected_count = 0
        row1_y = ground_y + 50
        row1_start = 1600
        spacing = 10
        for i in range(3):
            x = row1_start + i * (self._ring_width(file_path, batch) + spacing)
            ring = Ring(file_path, batch, x, row1_y)
            self.rings.append(ring)
        row2_y = ground_y + 140
        row2_start = 1600
        for i in range(3):
            x = row2_start + i * (self._ring_width(file_path, batch) + spacing)
            ring = Ring(file_path, batch, x, row2_y)
            self.rings.append(ring)
    def _ring_width(self, file_path, batch):
        temp_sprite = pyglet.sprite.Sprite(ResourceManager.get_animation(file_path), x=0, y=0, batch=batch)
        width = temp_sprite.width
        temp_sprite.delete()
        return width
    def update(self, dt, player):
        collected = 0
        for ring in self.rings:
            if not ring.collected and self.check_collision(player, ring):
                ring.collected = True
                ring.sprite.delete()
                collected += 1
        return collected
    def check_collision(self, player, ring):
        px1, py1 = player.x, player.y
        px2, py2 = player.x + player.sprite.width, player.y + player.sprite.height
        rx1, ry1, rx2, ry2 = ring.get_hitbox()
        return not (px2 < rx1 or px1 > rx2 or py2 < ry1 or py1 > ry2)
    def draw(self):
        for ring in self.rings:
            ring.draw()

# === Ring Counter (UI) ===
class RingCounter:
    def __init__(self, icon_path, x=30, y=30):
        self.icon = pyglet.sprite.Sprite(pyglet.image.load(icon_path), x=x, y=y)
        self.count = 0
        self.label = pyglet.text.Label(str(self.count),
                                       font_name='Arial',
                                       font_size=20,
                                       x=x + self.icon.width + 20,
                                       y=y + self.icon.height // 2,
                                       anchor_y='center',
                                       color=(255, 255, 255, 255))
    def update(self, new_count):
        self.count = new_count
        self.label.text = str(self.count)
    def draw(self):
        self.icon.draw()
        self.label.draw()

# === Menu Class ===
class Menu:
    def __init__(self, window):
        self.window = window
        menu_bg_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../aseprite/sprites')), 'titleGif.gif')
        self.bg = pyglet.sprite.Sprite(ResourceManager.get_animation(menu_bg_path), x=0, y=0)
        game_title_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../aseprite/sprites')), 'gameTitle.png')
        game_title_image = pyglet.image.load(game_title_path)
        game_title_image.anchor_x = game_title_image.width // 2
        game_title_image.anchor_y = game_title_image.height // 2
        self.title = pyglet.sprite.Sprite(game_title_image, x=self.window.width // 2, y=int(self.window.height * 0.75))
        start_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../aseprite/sprites')), 'start.gif')
        start_anim = ResourceManager.get_animation(start_path)
        self.start = pyglet.sprite.Sprite(start_anim, x=self.window.width // 2 - 200, y=int(self.window.height * 0.4))
        for frame in self.start.image.frames:
            frame.image.anchor_x = frame.image.width // 2
            frame.image.anchor_y = frame.image.height // 2
        press_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../aseprite/sprites')), 'press.gif')
        press_anim = ResourceManager.get_animation(press_path)
        self.press = pyglet.sprite.Sprite(press_anim, x=self.window.width // 2 - 180, y=int(self.window.height * 0.25))
        for frame in self.press.image.frames:
            frame.image.anchor_x = frame.image.width // 2
            frame.image.anchor_y = frame.image.height // 2
    def draw(self):
        self.bg.draw()
        self.title.draw()
        self.start.draw()
        self.press.draw()

# === LoadingScreen Class ===
class LoadingScreen:
    def __init__(self, window):
        self.window = window
        loading_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../aseprite/sprites')), 'loading.gif')
        loading_anim = ResourceManager.get_animation(loading_path)
        self.sprite = pyglet.sprite.Sprite(loading_anim, x=self.window.width * 0.4, y=self.window.height * 0.15 - 1000)
        for frame in self.sprite.image.frames:
            frame.image.anchor_x = frame.image.width // 2
            frame.image.anchor_y = frame.image.height // 2
    def draw(self):
        self.sprite.draw()

# === GameText Class ===
class GameText:
    def __init__(self, file_path, batch, x, y):
        image = pyglet.image.load(file_path)
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        self.sprite = pyglet.sprite.Sprite(image, x=x, y=y, batch=batch)
    def draw(self):
        self.sprite.draw()

# === Boss Classes ===

# Abstraktná trieda Boss
class Boss:
    def __init__(self, x, y, health, movement_speed, damage, batch):
        self.x = x
        self.y = y
        self.health = health
        self.movement_speed = movement_speed
        self.damage = damage
        self.batch = batch  # Teraz odovzdávame batch (napr. self.foreground_batch)
        self.sprite = None
        self.direction = 'left'
        self.active = True
        self.hit_cooldown = 0
    def update(self, dt):
        raise NotImplementedError
    def draw(self):
        if self.sprite:
            self.sprite.draw()
    def take_damage(self, amount):
        if self.hit_cooldown > 0:
            return
        self.health -= amount
        self.hit_cooldown = 3.0
        print(f"Boss health: {self.health}")
        if self.health <= 0:
            self.active = False
            if self.sprite is not None:
                self.sprite.delete()
                self.sprite = None
    def update_cooldown(self, dt):
        if self.hit_cooldown > 0:
            self.hit_cooldown -= dt
            if self.hit_cooldown < 0:
                self.hit_cooldown = 0

# Projectile Class
class Projectile:
    def __init__(self, file_path, batch, x, y, velocity_x, velocity_y):
        self.batch = batch
        self.sprite = pyglet.sprite.Sprite(ResourceManager.get_animation(file_path), x=x, y=y, batch=self.batch)
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.active = True
    def update(self, dt):
        if not self.active or self.sprite is None:
            return
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.sprite.x = self.x
        self.sprite.y = self.y
        if self.y <= 300:
            self.active = False
            self.sprite.delete()
            self.sprite = None
    def draw(self):
        if self.active and self.sprite is not None:
            self.sprite.draw()
    def get_hitbox(self):
        return (self.x, self.y, self.x + self.sprite.width, self.y + self.sprite.height)

# Explosion Class
class Explosion:
    def __init__(self, file_path, batch, x, y, duration=1.0):
        self.batch = batch
        self.sprite = pyglet.sprite.Sprite(ResourceManager.get_animation(file_path), x=x, y=y, batch=self.batch)
        self.x = x
        self.y = y
        self.duration = duration
        self.timer = duration
    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0 and self.sprite is not None:
            self.sprite.delete()
            self.sprite = None
    def draw(self):
        if self.timer > 0 and self.sprite is not None:
            self.sprite.draw()

# Eggman (Boss) Class – damage hráča dokážu dať len projektily
class Eggman(Boss):
    def __init__(self, batch):
        super().__init__(x=3000, y=650, health=10, movement_speed=150, damage=1, batch=batch)
        eggman_left_path = os.path.join(PlayerSprite.SPRITES_PATH, 'eggman_left.gif')
        eggman_right_path = os.path.join(PlayerSprite.SPRITES_PATH, 'eggman_right.gif')
        self.anim_left = ResourceManager.get_animation(eggman_left_path)
        self.anim_right = ResourceManager.get_animation(eggman_right_path)
        self.sprite = pyglet.sprite.Sprite(self.anim_right, x=self.x, y=self.y, batch=self.batch)
        self.sprite.anchor_x = 0
        self.sprite.anchor_y = 0
        self.projectile_timer = 3.0
        self.projectiles = []
    def update(self, dt):
        if not self.active:
            return
        self.update_cooldown(dt)
        if self.direction == 'left':
            self.x -= self.movement_speed * dt
            if self.x < 1000:
                self.x = 1000
                self.direction = 'right'
        else:
            self.x += self.movement_speed * dt
            if self.x > 3200:
                self.x = 3200
                self.direction = 'left'
        self.movement_speed = 150 + (10 - self.health) * 10
        if self.direction == 'left':
            self.sprite.image = self.anim_left
        else:
            self.sprite.image = self.anim_right
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.projectile_timer -= dt
        if self.projectile_timer <= 0:
            self.spawn_projectile()
            self.projectile_timer = 3.0 * (self.health / 10.0)
        for proj in self.projectiles:
            proj.update(dt)
        self.projectiles = [p for p in self.projectiles if p.active]
    def spawn_projectile(self):
        proj_path = os.path.join(PlayerSprite.SPRITES_PATH, 'projectile.gif')
        if self.direction == 'left':
            proj_x = self.x - 50
            velocity_x = -200
        else:
            proj_x = self.x + 50
            velocity_x = 200
        proj_y = self.y
        proj_velocity_y = -150
        projectile = Projectile(proj_path, self.batch, proj_x, proj_y, velocity_x, proj_velocity_y)
        self.projectiles.append(projectile)
    def draw(self):
        if self.active and self.sprite is not None:
            self.sprite.draw()
        for proj in self.projectiles:
            proj.draw()

# Eggdrill (Boss) Class – damage hráča dáva len špic hitboxu (rozšírená o 10 pixelov navyše)
class Eggdrill(Boss):
    def __init__(self, batch):
        super().__init__(x=2500, y=300, health=10, movement_speed=200, damage=1, batch=batch)
        eggdrill_left_path = os.path.join(PlayerSprite.SPRITES_PATH, 'eggdrill_left.gif')
        eggdrill_right_path = os.path.join(PlayerSprite.SPRITES_PATH, 'eggdrill_right.gif')
        self.anim_left = ResourceManager.get_animation(eggdrill_left_path)
        self.anim_right = ResourceManager.get_animation(eggdrill_right_path)
        self.sprite = pyglet.sprite.Sprite(self.anim_right, x=self.x, y=self.y, batch=self.batch)
        self.sprite.anchor_x = 0
        self.sprite.anchor_y = 0

    def update(self, dt):
        if not self.active:
            return
        # Pridáme update cooldown, aby sa hit_cooldown znižoval
        self.update_cooldown(dt)
        if self.direction == 'left':
            self.x -= self.movement_speed * dt
            if self.x < 1000:
                self.x = 1000
                self.direction = 'right'
        else:
            self.x += self.movement_speed * dt
            if self.x > 3200:
                self.x = 3200
                self.direction = 'left'
        self.movement_speed = 200 + (10 - self.health) * 15
        if self.direction == 'left':
            self.sprite.image = self.anim_left
        else:
            self.sprite.image = self.anim_right
        self.sprite.x = self.x
        self.sprite.y = self.y

    def get_hitbox(self):
        # Rozšírime hitbox o 10 pixelov dopredu
        if self.direction == 'right':
            return (self.x + self.sprite.width - 30, self.y, self.x + self.sprite.width, self.y + self.sprite.height)
        else:
            return (self.x, self.y, self.x + 30, self.y + self.sprite.height)

    def draw(self):
        if self.active and self.sprite is not None:
            self.sprite.draw()

# MetalSonic (Boss) Class – damage hráča dáva len keď je v stave "flying"
class MetalSonic(Boss):
    def __init__(self, batch):
        super().__init__(x=1000, y=700, health=10, movement_speed=400, damage=1, batch=batch)
        right_img = os.path.join(PlayerSprite.SPRITES_PATH, 'metalsonic_right.gif')
        right_fly_img = os.path.join(PlayerSprite.SPRITES_PATH, 'metalsonic_right_fly.gif')
        left_img = os.path.join(PlayerSprite.SPRITES_PATH, 'metalsonic_left.gif')
        left_fly_img = os.path.join(PlayerSprite.SPRITES_PATH, 'metalsonic_left_fly.gif')
        self.anim_right = ResourceManager.get_animation(right_img)
        self.anim_right_fly = ResourceManager.get_animation(right_fly_img)
        self.anim_left = ResourceManager.get_animation(left_img)
        self.anim_left_fly = ResourceManager.get_animation(left_fly_img)
        self.sprite = pyglet.sprite.Sprite(self.anim_right, x=self.x, y=self.y, batch=self.batch)
        self.sprite.anchor_x = 0
        self.sprite.anchor_y = 0
        self.state = "flying"  # Stavy: "flying", "waiting", "moving_vertical"
        self.wait_timer = 0
        self.target_y = self.y
    def update(self, dt):
        if not self.active:
            return
        self.update_cooldown(dt)
        speed = 400 + (10 - self.health) * 50
        if self.state == "flying":
            if self.direction == 'right':
                self.x += speed * dt
                if self.x >= 3200:
                    self.x = 3200
                    self.direction = 'left'
                    self.state = "waiting"
                    self.wait_timer = 4.0
            else:
                self.x -= speed * dt
                if self.x <= 1000:
                    self.x = 1000
                    self.direction = 'right'
                    self.state = "waiting"
                    self.wait_timer = 4.0
            if self.direction == 'right':
                self.sprite.image = self.anim_right_fly
            else:
                self.sprite.image = self.anim_left_fly
        elif self.state == "waiting":
            self.wait_timer -= dt
            if self.direction == 'right':
                self.sprite.image = self.anim_right
            else:
                self.sprite.image = self.anim_left
            if self.wait_timer <= 0:
                self.target_y = random.randint(300, 700)
                self.state = "moving_vertical"
        elif self.state == "moving_vertical":
            vertical_speed = 100 + (10 - self.health) * 20
            if self.y < self.target_y:
                self.y += vertical_speed * dt
                if self.y >= self.target_y:
                    self.y = self.target_y
                    self.state = "flying"
            elif self.y > self.target_y:
                self.y -= vertical_speed * dt
                if self.y <= self.target_y:
                    self.y = self.target_y
                    self.state = "flying"
            if self.direction == 'right':
                self.sprite.image = self.anim_right_fly
            else:
                self.sprite.image = self.anim_left_fly
        self.sprite.x = self.x
        self.sprite.y = self.y
    def draw(self):
        if self.active and self.sprite is not None:
            self.sprite.draw()
    def get_hitbox(self):
        return (self.x, self.y, self.x + self.sprite.width, self.y + self.sprite.height)

# === BossManager – s prístupom k window, ui_batch a hre ===
class BossManager:
    def __init__(self, batch, window, ui_batch, game):
        self.boss = None
        self.batch = batch
        self.window = window
        self.ui_batch = ui_batch
        self.game = game  # Referencia na hru pre prepnutie stavu
        self.boss_spawned = False
        self.explosions = []
        self.win_displayed = False
        self.lose_displayed = False
    def spawn_boss(self):
        if not self.boss_spawned:
            boss_class = random.choice([Eggman, Eggdrill, MetalSonic])
            self.boss = boss_class(self.batch)
            self.boss_spawned = True
            print("Boss spawned:", type(self.boss).__name__)

    def update(self, dt, player, player_rings):
        # Ak je boss spawnutý a aktívny, aktualizujeme jeho stav
        if self.boss_spawned and self.boss and self.boss.active:
            self.boss.update(dt)

            # Všeobecná kolízia: ak Sonic koliduje s bossom a nie je skákajúci,
            # Sonic dostáva damage
            if self.check_collision(player, self.boss) and player.hit_cooldown <= 0:
                if not player.is_jumping:
                    player.hit_cooldown = 3.0
                    player_rings = max(player_rings - 1, 0)
                    dmg_x = (player.x + player.sprite.width / 2) if player.sprite else player.x
                    dmg_y = (player.y + player.sprite.height + 20) if player.sprite else player.y
                    self.game.damage_texts.append(DamageText("-1 HP", dmg_x, dmg_y, 1.0))

            # Špecifické spracovanie podľa typu bossa:
            if isinstance(self.boss, Eggman):
                # Eggman nedáva damage hráčovi priamym dotykom, iba projektilmi
                for proj in self.boss.projectiles:
                    if self.check_collision(player, proj) and player.hit_cooldown <= 0:
                        player.hit_cooldown = 3.0
                        proj.active = False
                        if proj.sprite is not None:
                            proj.sprite.delete()
                            proj.sprite = None
                        player_rings = max(player_rings - 1, 0)
                        dmg_x = (player.x + player.sprite.width / 2) if player.sprite else player.x
                        dmg_y = (player.y + player.sprite.height + 20) if player.sprite else player.y
                        self.game.damage_texts.append(DamageText("-1 HP", dmg_x, dmg_y, 1.0))
                        # Dodatočný blok: ak Sonic je skákajúci a dotkne sa Eggmana, boss dostane damage.
                if player.is_jumping and self.check_collision(player,
                                                              self.boss) and self.boss.hit_cooldown <= 0:
                    self.boss.take_damage(1)
                    player.hit_cooldown = 3.0
                    dmg_x = (self.boss.x + self.boss.sprite.width / 2) if self.boss.sprite else self.boss.x
                    dmg_y = (self.boss.y + self.boss.sprite.height) if self.boss.sprite else self.boss.y
                    self.game.damage_texts.append(DamageText("-1 HP", dmg_x, dmg_y, 1.0))
            elif isinstance(self.boss, Eggdrill):
                ex1, ey1, ex2, ey2 = self.boss.get_hitbox()
                if (player.x + player.sprite.width > ex1 and player.x < ex2 and
                        player.y + player.sprite.height > ey1 and player.y < ey2):
                    if player.hit_cooldown <= 0 and not player.is_jumping:
                        player.hit_cooldown = 3.0
                        player_rings = max(player_rings - 1, 0)
                        dmg_x = (player.x + player.sprite.width / 2) if player.sprite else player.x
                        dmg_y = (player.y + player.sprite.height + 20) if player.sprite else player.y
                        self.game.damage_texts.append(DamageText("-1 HP", dmg_x, dmg_y, 1.0))
                # Ak Sonic je skákajúci a dotkne sa Eggdrilla a boss nie je v cooldown, boss dostane damage
                if player.is_jumping and self.check_collision(player, self.boss) and self.boss.hit_cooldown <= 0:
                    self.boss.take_damage(1)
                    player.hit_cooldown = 3.0
                    dmg_x = (self.boss.x + self.boss.sprite.width / 2) if self.boss.sprite else self.boss.x
                    dmg_y = (self.boss.y + self.boss.sprite.height) if self.boss.sprite else self.boss.y
                    self.game.damage_texts.append(DamageText("-1 HP", dmg_x, dmg_y, 1.0))
            elif isinstance(self.boss, MetalSonic):
                if self.boss.state == "flying":
                    if self.check_collision(player, self.boss) and player.hit_cooldown <= 0:
                        if player.is_jumping and self.boss.hit_cooldown <= 0:
                            self.boss.take_damage(1)
                            player.hit_cooldown = 3.0
                            dmg_x = (self.boss.x + self.boss.sprite.width / 2) if self.boss.sprite else self.boss.x
                            dmg_y = (self.boss.y + self.boss.sprite.height) if self.boss.sprite else self.boss.y
                            self.game.damage_texts.append(DamageText("-1 HP", dmg_x, dmg_y, 1.0))
                        elif not player.is_jumping:
                            player.hit_cooldown = 3.0
                            player_rings = max(player_rings - 1, 0)
                            dmg_x = (player.x + player.sprite.width / 2) if player.sprite else player.x
                            dmg_y = (player.y + player.sprite.height + 20) if player.sprite else player.y
                            self.game.damage_texts.append(DamageText("-1 HP", dmg_x, dmg_y, 1.0))
                # Aj mimo stavu "flying": ak Sonic je skákajúci a dotkne sa bossa a boss nie je v cooldown, boss dostane damage.
                if player.is_jumping and self.check_collision(player, self.boss) and self.boss.hit_cooldown <= 0:
                    self.boss.take_damage(1)
                    player.hit_cooldown = 3.0
                    dmg_x = (self.boss.x + self.boss.sprite.width / 2) if self.boss.sprite else self.boss.x
                    dmg_y = (self.boss.y + self.boss.sprite.height) if self.boss.sprite else self.boss.y
                    self.game.damage_texts.append(DamageText("-1 HP", dmg_x, dmg_y, 1.0))
            # V tejto vetve vždy vrátime hodnotu player_rings
            return player_rings

        elif self.boss_spawned and self.boss and not self.boss.active:
            if not self.explosions:
                self.spawn_explosions(self.boss.x, self.boss.y)
            for exp in self.explosions:
                exp.update(dt)
            if all(exp.timer <= 0 for exp in self.explosions) and not self.win_displayed:
                self.win_displayed = True
                self.display_end_message("gameText2.png")  # YOU WIN
            return player_rings

        return player_rings

    def check_collision(self, entity1, entity2):
        e1x1, e1y1 = entity1.x, entity1.y
        e1x2, e1y2 = entity1.x + entity1.sprite.width, entity1.y + entity1.sprite.height
        if hasattr(entity2, 'sprite') and entity2.sprite is not None:
            e2x1, e2y1 = entity2.x, entity2.y
            e2x2, e2y2 = entity2.x + entity2.sprite.width, entity2.y + entity2.sprite.height
        else:
            return False
        return not (e1x2 < e2x1 or e1x1 > e2x2 or e1y2 < e2y1 or e1y1 > e2y2)

    def spawn_explosions(self, x, y):
        exp_path = os.path.join(PlayerSprite.SPRITES_PATH, 'explosion.gif')
        offsets = [(-50, -50), (50, -50), (-50, 50), (50, 50)]
        for dx, dy in offsets:
            exp = Explosion(exp_path, self.batch, x + dx, y + dy, duration=1.0)
            self.explosions.append(exp)

    def display_end_message(self, image_file):
        end_img = pyglet.image.load(os.path.join(PlayerSprite.SPRITES_PATH, image_file))
        end_img.anchor_x = end_img.width // 2
        end_img.anchor_y = end_img.height // 2
        self.end_sprite = pyglet.sprite.Sprite(end_img, x=self.window.width // 2, y=self.window.height // 2,
                                               batch=self.ui_batch)
        pyglet.clock.schedule_once(self.return_to_menu, 3.0)

    def return_to_menu(self, dt):
        pyglet.app.exit()

    def draw(self):
        # Bossy sú teraz v globálnom batchu, takže tu kreslíme iba explózie
        for exp in self.explosions:
            exp.draw()

# === GameText Class ===
class GameText:
    def __init__(self, file_path, batch, x, y):
        image = pyglet.image.load(file_path)
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        self.sprite = pyglet.sprite.Sprite(image, x=x, y=y, batch=batch)
    def draw(self):
        self.sprite.draw()

# === Game Class (s kamera follow, menu a boss fight) ===
class Game:
    def __init__(self):
        self.window = pyglet.window.Window(fullscreen=True, caption="Sonic Game")
        self.background_batch = pyglet.graphics.Batch()
        self.ground_batch = pyglet.graphics.Batch()
        self.foreground_batch = pyglet.graphics.Batch()
        self.ui_batch = pyglet.graphics.Batch()

        self.state = "menu"
        self.camera_x = 0

        self.menu = Menu(self.window)
        self.loading = LoadingScreen(self.window)

        self.background_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../aseprite/sprites')),
                                            'sunsethill_animated.gif')
        self.background = Background(self.background_path, self.background_batch)

        ground_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../aseprite/sprites')),
                                   'ground.png')
        self.ground = Ground(ground_path, self.ground_batch, y_position=-120)

        self.player = Player(self.foreground_batch, self.window)

        ring_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../aseprite/sprites')),
                                 'ring.gif')
        self.rings_manager = RingsManager(ring_path, self.foreground_batch, ground_y=280, count=6)

        ring_icon_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../aseprite/sprites')),
                                      'ringPhoto.png')
        self.ring_counter = RingCounter(ring_icon_path, x=30, y=self.window.height - 100)

        game_text_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../aseprite/sprites')),
                                      'gameText1.png')
        self.game_text = GameText(game_text_path, self.foreground_batch, x=2000, y=400)

        self.boss_manager = BossManager(self.foreground_batch, self.window, self.ui_batch, self)

        self.player_rings = 6

        # Zoznam pre damage texty
        self.damage_texts = []

        self.window.push_handlers(self)
        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

    def on_draw(self):
        self.window.clear()
        if self.state == "menu":
            self.menu.draw()
        elif self.state == "loading":
            self.loading.draw()
        elif self.state == "game":
            self.window.view = math.Mat4().translate((-self.camera_x, 0, 0))
            self.background_batch.draw()
            self.ground_batch.draw()
            self.foreground_batch.draw()
            self.window.view = math.Mat4()
            self.ring_counter.draw()
            self.ui_batch.draw()
            for dt in self.damage_texts:
                dt.draw()
        else:
            self.ui_batch.draw()
            for dt in self.damage_texts:
                dt.draw()

    def on_key_press(self, symbol, modifiers):
        if self.state == "menu":
            if symbol == key.SPACE:
                self.state = "loading"
                pyglet.clock.schedule_once(self.start_game, 2.0)
        elif self.state == "game":
            self.player.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        if self.state == "game":
            self.player.on_key_release(symbol, modifiers)

    def start_game(self, dt):
        self.state = "game"

    def update(self, dt):
        if self.state == "game":
            self.player.update(dt)
            self.background.update(dt)
            new_rings = self.rings_manager.update(dt, self.player)
            self.player_rings += new_rings
            self.ring_counter.update(self.player_rings)
            self.game_text.draw()
            self.camera_x = self.player.x - self.window.width / 2
            if self.player.x >= 1300 and not self.boss_manager.boss_spawned:
                self.boss_manager.spawn_boss()
            if self.boss_manager.boss_spawned:
                self.player_rings = self.boss_manager.update(dt, self.player, self.player_rings)
            if self.player_rings <= 0:
                self.boss_manager.display_end_message("gameText3.png")  # YOU LOSE
                pyglet.clock.schedule_once(lambda dt: pyglet.app.exit(), 3.0)

        # Aktualizácia damage textov
        for dt_obj in self.damage_texts:
            dt_obj.update(dt)
        self.damage_texts = [dt_obj for dt_obj in self.damage_texts if dt_obj.timer > 0]

    def run(self):
        pyglet.app.run()

if __name__ == '__main__':
    game = Game()
    game.run()
