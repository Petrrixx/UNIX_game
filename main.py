import pyglet

window = pyglet.window.Window(800, 600, "Sonic Game")

sonic_image = pyglet.resource.image('resources/sprites/sonic.png')
sonic_sprite = pyglet.sprite.Sprite(sonic_image, x=100, y=100)

@window.event
def on_draw():
    window.clear()
    sonic_sprite.draw()

pyglet.app.run()
