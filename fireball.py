import components
import game
import processors
import pygame
class Fireball:
    def __init__(self,x,y):
        self.vx = 5
        self.vy = 0
        self.x = x
        self.y = y
        self.image = pygame.image.load("images/fireball.png")
    def update(self):
        self.x = minmax(self.x + self.vx, 0, 1280 - self.image.get_width())
        
        
