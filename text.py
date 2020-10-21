import scenebase
import pygame
import components
import processors
import interpolation
import util
import os

class TextScene(scenebase.SceneBase):
    def __init__(self, text, scene):
        scenebase.SceneBase.__init__(self, None)
        self.text = text
        self.scene = scene

    def init(self):
        scenebase.SceneBase.init(self)
        
        text = self.world.create_entity()
        image = pygame.Surface([1280,720], pygame.SRCALPHA, 32).convert_alpha()
        util.drawText(image, self.text, (255, 255, 255), pygame.Rect(100, 100, 1080, 520), self.font)
        self.world.add_component(text, components.Position(640, 240))
        self.world.add_component(text, components.Image(image=image, alpha=0))
        self.world.add_component(text, components.Size(image.get_width(), image.get_height()))
        self.world.add_component(text, components.ChangePosition((640, 340), .5))
        self.world.add_component(text, components.ChangeAlpha(1, 1))
        #self.world.add_component(text, components.Reactive())

        def fade_out(entity):
            self.world.add_component(entity, components.ChangeAlpha(.5, 1, interpolation.Circle(), fade_in, entity))

        def fade_in(entity):
            self.world.add_component(entity, components.ChangeAlpha(1, 1, interpolation.Circle(), fade_out, entity))

        continue_text = self.world.create_entity()
        image = self.font.render("press any button to continue", False, (32, 128, 255))
        self.world.add_component(continue_text, components.Position(640, 640))
        self.world.add_component(continue_text, components.Image(image=image))
        self.world.add_component(continue_text, components.Size(image.get_width(), image.get_height()))
        #self.world.add_component(continue_text, components.Reactive())
        fade_in(continue_text)

        def fade_scene():
            for ent in [text, continue_text]:
                if self.world.has_component(ent, components.ChangeAlpha):
                    self.world.remove_component(ent, components.ChangeAlpha)
                self.world.add_component(ent, components.ChangeAlpha(0, .5))
                self.world.add_component(ent, components.ChangePosition((640, self.world.component_for_entity(ent, components.Position).y + 50), .5))

            self.world.add_component(text, components.Delay(1, next_scene))
            pygame.mixer.Sound(os.path.join(components.get_base_path(), 'audio', 'click')).play()

        def next_scene():
            self.switch_to_scene(self.scene)

        self.world.add_processor(processors.RenderProcessor())
        self.world.add_processor(processors.AnimationProcessor(), priority=5)
        self.world.add_processor(processors.TextProcessor(fade_scene), priority=10)
        self.world.add_processor(processors.InputProcessor())
