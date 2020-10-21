import os
import sys
import interpolation
import pygame

def get_base_path():
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return sys._MEIPASS
    except Exception:
        return os.path.abspath(".")

class Player:
    facing_right=True
    holding=None

    def __init__(self, image=None, animation=None, carry_image=None, carry_animation=None, jump=None, throw=None):
        self.image = image
        self.animation = animation
        self.carry_image = carry_image
        self.carry_animation = carry_animation
        self.jump = jump
        self.throw = throw

class Position:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

class Size:
    def __init__(self, width=0.0, height=0.0, scale=1.0):
        self.width = width
        self.height = height
        self.scale = scale

class Text:
    def __init__(self, text="", font=None, color=(0, 128, 0)):
        self.text = text
        self.font = font
        self.color = color

class Background: # Just an identifier component, because I can't/don't know how to sort the get_components generator
    def __init__(self):
        pass

class Image:
    def __init__(self, file=None, image=None, blend=0, alpha=255):
        if file:
            self.image = pygame.image.load(os.path.join(get_base_path(), 'images', file)).convert_alpha()
        else:
            self.image = image
        self.blend = blend
        self.alpha = alpha

class Reactive:
    x = 0
    y = 0

    def __init__(self):
        pass

class Audio:
    def __init__(self, file=None, sound=None):
        if file:
            self.sound = pygame.mixer.Sound(os.path.join(get_base_path(), 'audio', file))
        else:
            self.sound = sound

class Animation:
    time = 0

    def __init__(self, file=None, image=None, splitx=0, framelength=-1, frame=0, blend=0, alpha=255):
        if file:
            self.image = pygame.image.load(os.path.join(get_base_path(), 'images', file)).convert_alpha()
        else:
            self.image = image
        self.splitx=splitx
        self.framelength=framelength
        self.maxframes=self.image.get_width()/splitx
        self.frame = frame
        self.blend = blend
        self.alpha = alpha

class Click:
    def __init__(self, run=None, *args):
        self.run = run
        self.args = args

class Over:
    active = False

    def __init__(self, enterf=None, exitf=None, entity=None):
        self.enterf = enterf
        self.exitf = exitf
        self.entity = entity

class Touch:
    active = False

    def __init__(self, target=None, multi=False, rect=pygame.Rect(0,0,0,0), touch=None, *args):
        self.target = target
        self.multi = multi
        self.rect = rect
        self.touch = touch
        self.args = args

class Circle:
    def __init__(self, color=(0,128,0), radius=0.0, width=0):
        self.color = color
        self.radius = radius
        self.width = width

class Rect:
    def __init__(self, color=(0,128,0), rect=pygame.Rect(0, 0, 0, 0), width=0):
        self.color = color
        self.rect = rect
        self.width = width

class Velocity:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

class RotationalVelocity:
    angle = 0
    image = None
    scale = 0

    def __init__(self, speed=0):
        self.speed = speed

class ChangePosition:
    current = None

    def __init__(self, target=(0,0), time=0, interp=interpolation.InterpolationBase(), relative=False, chain=None, *args):
        self.target = target
        self.time = time
        self.interp = interp
        self.relative = relative
        self.chain = chain
        self.args = args

class ChangeSize:
    current = None

    def __init__(self, target=1, time=0, interp=interpolation.InterpolationBase(), chain=None, *args):
        self.target = target
        self.time = time
        self.interp = interp
        self.chain = chain
        self.args = args

class ChangeVelocity:
    current = None

    def __init__(self, target=(0,0), time=0, interp=interpolation.InterpolationBase(), chain=None, *args):
        self.target = target
        self.time = time
        self.interp = interp
        self.chain = chain
        self.args = args

class ChangeAlpha:
    current = None

    def __init__(self, target=0, time=0, interp=interpolation.InterpolationBase(), chain=None, *args):
        self.target = target
        self.time = time
        self.interp = interp
        self.chain = chain
        self.args = args

class CircleAnimation:
    current = 0

    def __init__(self, radius=0, time=0, stopangle=0, loop=False, chain=None, *args):
        self.radius = radius
        self.time = time
        self.stopangle = stopangle
        self.loop = loop
        self.chain = chain
        self.args = args

class Delay:
    def __init__(self, time=0, chain=None, *args):
        self.time = time
        self.chain = chain
        self.args = args

class Platform:
    def __init__(self):
        pass

class Hang:
    def __init__(self):
        pass

class Flammable:
    def __init__(self, lit=False):
        self.lit = lit


