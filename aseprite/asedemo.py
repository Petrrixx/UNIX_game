# TÁTO TRIEDA NIE JE MOJA, JE ZOBRANÁ Z GITU.

from re import fullmatch
import pyglet
import aseprite

window = pyglet.window.Window(1920, 1080)
batch = pyglet.graphics.Batch()

# Add image decoders from the loaded codec module.
pyglet.image.codecs.add_decoders(aseprite)

# Load the animation as before
image = pyglet.image.load_animation("sprites/sonic_idle_right.aseprite")
sprite = pyglet.sprite.Sprite(img=image, x=0, y=0, batch=batch)

# Set nearest-neighbor filtering for pixelated look
for frame in image.frames:
    texture = frame.image.get_texture()  # Get the texture explicitly
    texture.mag_filter = pyglet.gl.GL_NEAREST

# Define zoom factor
zoom = 1.0  # 2x zoom

@window.event
def on_draw():
    window.clear()

    # Scale the sprite to simulate zoom
    sprite.scale = zoom
    sprite.x = (window.width - sprite.width * sprite.scale) / 2
    sprite.y = (window.height - sprite.height * sprite.scale) / 2

    # Draw all content
    batch.draw()

if __name__ == "__main__":
    pyglet.app.run()
