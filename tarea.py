#Roberto Rivera / CC3501 Seccion 1
import pyglet
import numpy as np
from pyglet.shapes import Circle, Rectangle, Line, Star, Triangle
import random


window = pyglet.window.Window(1000, 700)
batch = pyglet.graphics.Batch()


estrellas = []
for i in range(50):
    estrella = Star(random.randint(0, window.width), random.randint(0, window.height), outer_radius = 5, 
                    inner_radius= 3, num_spikes = 5, rotation = 0, color = (255, 255, 255), batch = batch)
    estrellas.append(estrella)

def st(t):
    for estrella in estrellas:
        estrella.y += -200*t
        if estrella.y < 0:
            estrella.x = random.randint(0, window.width)
            estrella.y = random.randint(705, 800)


class Nave:
    def __init__(self, dx, dy):
        self.body = (Triangle(x=475+dx, y=330+dy, x2=500+dx, y2=450+dy,
                    x3=500+dx, y3=300+dy, color=(128, 128, 128), batch=batch), 
                    Triangle(x=525+dx, y=330+dy, x2=500+dx, y2=450+dy,
                    x3=500+dx, y3=300+dy, color=(115, 115, 115), batch=batch),
                    Triangle(x=487.5+dx, y=330+dy, x2=500+dx, y2=375+dy,
                    x3=500+dx, y3=325+dy, color=(255, 0, 0), batch=batch),
                    Triangle(x=512.5+dx, y=330+dy, x2=500+dx, y2=375+dy,
                    x3=500+dx, y3=325+dy, color=(200, 0, 0), batch=batch),
                    Triangle(x=470+dx, y=330+dy, x2=445+dx, y2=340+dy,
                    x3=415+dx, y3=250+dy, color=(128, 128, 128), batch=batch),
                    Triangle(x=530+dx, y=330+dy, x2=555+dx, y2=340+dy,
                    x3=585+dx, y3=250+dy, color=(115, 115, 115), batch=batch),
                    Triangle(x=482.5+dx, y=330+dy, x2=480+dx, y2=390+dy,
                    x3=455+dx, y3=275+dy, color=(70, 180, 220), batch=batch),
                    Triangle(x=517.5+dx, y=330+dy, x2=520+dx, y2=390+dy,
                    x3=545+dx, y3=275+dy, color=(55, 165, 205), batch=batch)
                    )

nave = Nave(0 , 0)
nave2 = Nave(150 , -150)
nave3 = Nave(-150 , -150)

@window.event
def on_draw():
    window.clear()
    batch.draw()


if __name__ == '__main__':
    pyglet.clock.schedule_interval(st, 1/60.0)
    pyglet.app.run()