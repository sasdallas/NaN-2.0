import esper
import pygame
import os
import components
class SceneBase:
    def __init__(self, bgm):
        self.world = esper.World()
        self.next = self
        self.bgm = bgm

    def init(self):
        self.font = SceneBase.font
        self.small_font = SceneBase.small_font
        self.large_font = SceneBase.large_font
        self.titlefont = SceneBase.titlefont

    def switch_to_scene(self, next_scene):
        if next_scene is not None:
            next_scene.init()
            
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(1000)
            if next_scene.bgm is not None:
                
                pygame.mixer.music.load(os.path.join(components.get_base_path(), next_scene.bgm))
                pygame.mixer.music.play(-1)

        self.next = next_scene

    def terminate(self):
        self.switch_to_scene(None)
    
