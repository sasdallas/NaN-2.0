import scenebase
import pygame
import components
import processors
import text
import game
import math

class TitleScene(scenebase.SceneBase):
    def __init__(self):
        scenebase.SceneBase.__init__(self, None)

    def init(self):
        scenebase.SceneBase.init(self)

        def start_game():
            for ent, (p, i) in self.world.get_components(components.Position, components.Image):
                self.world.add_component(ent, components.ChangePosition((p.x, p.y + 100), .25))
                self.world.add_component(ent, components.ChangeAlpha(0, .25))
            def change_scene():
                self.switch_to_scene(text.TextScene("This is the story of an adventurer named NaN, known across the land for his unwavering enthusiasm for helping anyone with anything. His abilities were known far and wide, and indeed our story even begins with him defeating a dragon with ease...", game.SceneOne()))
            next_scene = self.world.create_entity()
            self.world.add_component(next_scene, components.Delay(.5, change_scene))

        def scene_select():
            self.switch_to_scene(SceneSelect())

        def quit_game():
            self.terminate()

        def highlight(entity):
            t = self.world.component_for_entity(entity, components.Text)
            image = t.font.render("> " + t.text + " <", False, (0, 128, 128))
            self.world.component_for_entity(entity, components.Image).image = image
            size = self.world.component_for_entity(entity, components.Size)
            size.width = image.get_width()
            size.height = image.get_height()

        def lowlight(entity):
            t = self.world.component_for_entity(entity, components.Text)
            image = t.font.render(t.text, False, t.color)
            self.world.component_for_entity(entity, components.Image).image = image
            size = self.world.component_for_entity(entity, components.Size)
            size.width = image.get_width()
            size.height = image.get_height()

        start = self.world.create_entity()
        image = self.large_font.render("start", False, (0, 128, 0))
        self.world.add_component(start, components.Position(640, 440))
        self.world.add_component(start, components.Text("start", self.large_font))
        self.world.add_component(start, components.Image(image=image))
        self.world.add_component(start, components.Size(image.get_width(), image.get_height(), .75))
        self.world.add_component(start, components.Click(start_game))
        self.world.add_component(start, components.Over(highlight, lowlight))
        self.world.add_component(start, components.Audio("click"))

        scene = self.world.create_entity()
        image = self.large_font.render("scene select", False, (0, 128, 0))
        self.world.add_component(scene, components.Position(640, 540))
        self.world.add_component(scene, components.Text("scene select", self.large_font))
        self.world.add_component(scene, components.Image(image=image))
        self.world.add_component(scene, components.Size(image.get_width(), image.get_height(), .75))
        self.world.add_component(scene, components.Click(scene_select))
        self.world.add_component(scene, components.Over(highlight, lowlight))
        self.world.add_component(scene, components.Audio("click"))

        quitbutton = self.world.create_entity()
        image = self.large_font.render("quit", False, (0, 128, 0))
        self.world.add_component(quitbutton, components.Position(640, 640))
        self.world.add_component(quitbutton, components.Text("quit", self.large_font))
        self.world.add_component(quitbutton, components.Image(image=image))
        self.world.add_component(quitbutton, components.Size(image.get_width(), image.get_height(), .75))
        self.world.add_component(quitbutton, components.Click(quit_game))
        self.world.add_component(quitbutton, components.Over(highlight, lowlight))
        self.world.add_component(quitbutton, components.Audio("click"))

        title = self.world.create_entity()
        image = self.titlefont.render("NaN 2.0", False, (0, 128, 0))
        self.world.add_component(title, components.Position(640, 240))
        self.world.add_component(title, components.Image(image=image))
        self.world.add_component(title, components.Size(image.get_width(), image.get_height()))

        self.world.add_processor(processors.RenderProcessor())
        self.world.add_processor(processors.InputProcessor(), priority=10)
        self.world.add_processor(processors.PhysicsProcessor(), priority=5)
        self.world.add_processor(processors.AnimationProcessor(), priority=5)

class SceneSelect(scenebase.SceneBase):
    def __init__(self):
        scenebase.SceneBase.__init__(self, None)

    def init(self):
        scenebase.SceneBase.init(self)

        def go_back():
            self.switch_to_scene(TitleScene())

        def open_scene(scene):
            self.switch_to_scene(scene)

        def highlight(entity):
            t = self.world.component_for_entity(entity, components.Text)
            image = t.font.render("> " + t.text + " <", False, (0, 128, 128))
            self.world.component_for_entity(entity, components.Image).image = image
            size = self.world.component_for_entity(entity, components.Size)
            size.width = image.get_width()
            size.height = image.get_height()

        def lowlight(entity):
            t = self.world.component_for_entity(entity, components.Text)
            image = t.font.render(t.text, False, t.color)
            self.world.component_for_entity(entity, components.Image).image = image
            size = self.world.component_for_entity(entity, components.Size)
            size.width = image.get_width()

        back = self.world.create_entity()
        image = self.large_font.render("back", False, (0, 128, 0))
        self.world.add_component(back, components.Position(640, 360))
        self.world.add_component(back, components.Text("back", self.large_font))
        self.world.add_component(back, components.Image(image=image))
        self.world.add_component(back, components.Size(image.get_width(), image.get_height(), .75))
        self.world.add_component(back, components.Reactive())
        self.world.add_component(back, components.Click(go_back))
        self.world.add_component(back, components.Over(highlight, lowlight))
        self.world.add_component(back, components.Audio("click"))

        scene1 = self.world.create_entity()
        label1 = self.world.create_entity()
        image = self.large_font.render("1", False, (0, 128, 0))
        self.world.add_component(label1, components.Position(300, 170))
        self.world.add_component(label1, components.Text("1", self.large_font))
        self.world.add_component(label1, components.Image(image=image))
        self.world.add_component(label1, components.Size(image.get_width(), image.get_height()))
        self.world.add_component(label1, components.Reactive())

        self.world.add_component(scene1, components.Position(300, 100))
        self.world.add_component(scene1, components.Platform())
        self.world.add_component(scene1, components.Image("IntroBG.png"))
        self.world.add_component(scene1, components.Size(320, 180))
        self.world.add_component(scene1, components.Reactive())
        self.world.add_component(scene1, components.Click(open_scene, game.SceneOne()))
        self.world.add_component(scene1, components.Over(highlight, lowlight, label1))

        scene2 = self.world.create_entity()
        label2 = self.world.create_entity()
        image = self.large_font.render("2", False, (0, 128, 0))
        self.world.add_component(label2, components.Position(980, 170))
        self.world.add_component(label2, components.Text("2", self.large_font))
        self.world.add_component(label2, components.Image(image=image))
        self.world.add_component(label2, components.Size(image.get_width(), image.get_height()))
        self.world.add_component(label2, components.Reactive())

        self.world.add_component(scene2, components.Position(980, 100))
        self.world.add_component(scene2, components.Platform())
        self.world.add_component(scene2, components.Image("OutsideSceneBG.png"))
        self.world.add_component(scene2, components.Size(320, 180))
        self.world.add_component(scene2, components.Reactive())
        self.world.add_component(scene2, components.Click(open_scene, game.SceneTwo()))
        self.world.add_component(scene2, components.Over(highlight, lowlight, label2))

        scene3 = self.world.create_entity()
        label3 = self.world.create_entity()
        image = self.large_font.render("3", False, (0, 128, 0))
        self.world.add_component(label3, components.Position(300, 420))
        self.world.add_component(label3, components.Text("3", self.large_font))
        self.world.add_component(label3, components.Image(image=image))
        self.world.add_component(label3, components.Size(image.get_width(), image.get_height()))
        self.world.add_component(label3, components.Reactive())

        self.world.add_component(scene3, components.Position(300, 350))
        self.world.add_component(scene3, components.Platform())
        self.world.add_component(scene3, components.Image("HouseScene2BG.png"))
        self.world.add_component(scene3, components.Size(320, 180))
        self.world.add_component(scene3, components.Reactive())
        self.world.add_component(scene3, components.Click(open_scene, game.SceneThree()))
        self.world.add_component(scene3, components.Over(highlight, lowlight, label3))

        scene4 = self.world.create_entity()
        label4 = self.world.create_entity()
        image = self.large_font.render("4", False, (0, 128, 0))
        self.world.add_component(label4, components.Position(980, 420))
        self.world.add_component(label4, components.Text("4", self.large_font))
        self.world.add_component(label4, components.Image(image=image))
        self.world.add_component(label4, components.Size(image.get_width(), image.get_height()))
        self.world.add_component(label4, components.Reactive())

        self.world.add_component(scene4, components.Position(980, 350))
        self.world.add_component(scene4, components.Platform())
        self.world.add_component(scene4, components.Image("HouseScene3BG.png"))
        self.world.add_component(scene4, components.Size(320, 180))
        self.world.add_component(scene4, components.Reactive())
        self.world.add_component(scene4, components.Click(open_scene, game.SceneFour()))
        self.world.add_component(scene4, components.Over(highlight, lowlight, label4))

        scene5 = self.world.create_entity()
        label5 = self.world.create_entity()
        image = self.large_font.render("5", False, (0, 128, 0))
        self.world.add_component(label5, components.Position(300, 670))
        self.world.add_component(label5, components.Text("5", self.large_font))
        self.world.add_component(label5, components.Image(image=image))
        self.world.add_component(label5, components.Size(image.get_width(), image.get_height()))
        self.world.add_component(label5, components.Reactive())

        self.world.add_component(scene5, components.Position(300, 600))
        self.world.add_component(scene5, components.Platform())
        self.world.add_component(scene5, components.Image("HouseSceneBlacksmithBG.png"))
        self.world.add_component(scene5, components.Size(320, 180))
        self.world.add_component(scene5, components.Reactive())
        self.world.add_component(scene5, components.Click(open_scene, game.SceneFive()))
        self.world.add_component(scene5, components.Over(highlight, lowlight, label5))

        scene6 = self.world.create_entity()
        label6 = self.world.create_entity()
        image = self.large_font.render("6", False, (0, 128, 0))
        self.world.add_component(label6, components.Position(980, 670))
        self.world.add_component(label6, components.Text("6", self.large_font))
        self.world.add_component(label6, components.Image(image=image))
        self.world.add_component(label6, components.Size(image.get_width(), image.get_height()))
        self.world.add_component(label6, components.Reactive())

        self.world.add_component(scene6, components.Position(980, 600))
        self.world.add_component(scene6, components.Platform())
        self.world.add_component(scene6, components.Image("HouseScene1BG.png"))
        self.world.add_component(scene6, components.Size(320, 180))
        self.world.add_component(scene6, components.Reactive())
        self.world.add_component(scene6, components.Click(open_scene, game.SceneSix()))
        self.world.add_component(scene6, components.Over(highlight, lowlight, label6))


        scene7 = self.world.create_entity()
        label7 = self.world.create_entity()
        image = self.large_font.render("7", False, (0, 128, 0))
        self.world.add_component(label7, components.Position(501,150))
        self.world.add_component(label7, components.Text("7",self.large_font))
        self.world.add_component(label7, components.Image(image=image))
        self.world.add_component(label7, components.Size(image.get_width(), image.get_height()))
        self.world.add_component(label7, components.Reactive())
        self.world.add_component(scene7, components.Position(500,94))
        self.world.add_component(scene7, components.Platform())
        self.world.add_component(scene7, components.Image("IntroBG.png"))
        self.world.add_component(scene7, components.Size(320, 180))
        self.world.add_component(scene7, components.Reactive())
        self.world.add_component(scene7, components.Click(open_scene, game.SceneSeven()))
        self.world.add_component(scene7, components.Over(highlight, lowlight, label7))


        scene8 = self.world.create_entity()
        label8 = self.world.create_entity()
        image = self.large_font.render("8", False, (0, 128, 0))
        self.world.add_component(label8, components.Position(488,420))
        self.world.add_component(label8, components.Text("8",self.large_font))
        self.world.add_component(label8, components.Image(image=image))
        self.world.add_component(label8, components.Size(image.get_width(), image.get_height()))
        self.world.add_component(label8, components.Reactive())
        self.world.add_component(scene8, components.Position(469,367))
        self.world.add_component(scene8, components.Platform())
        self.world.add_component(scene8, components.Image("HouseScene2BG.png"))
        self.world.add_component(scene8, components.Size(320, 180))
        self.world.add_component(scene8, components.Reactive())
        self.world.add_component(scene8, components.Click(open_scene, game.SceneEight()))
        self.world.add_component(scene8, components.Over(highlight, lowlight, label8))

        scene9 = self.world.create_entity()
        label9 = self.world.create_entity()
        image = self.large_font.render("9", False, (0, 128, 0))
        self.world.add_component(label9, components.Position(472,685))
        self.world.add_component(label9, components.Text("9",self.large_font))
        self.world.add_component(label9, components.Image(image=image))
        self.world.add_component(label9, components.Size(image.get_width(), image.get_height()))
        self.world.add_component(label9, components.Reactive())
        self.world.add_component(scene9, components.Position(472,598))
        self.world.add_component(scene9, components.Platform())
        self.world.add_component(scene9, components.Image("OutsideSceneBG.png"))
        self.world.add_component(scene9, components.Size(320, 180))
        self.world.add_component(scene9, components.Reactive())
        self.world.add_component(scene9, components.Click(open_scene, game.SceneNine()))
        self.world.add_component(scene9, components.Over(highlight, lowlight, label9))


        for ent, (i, p, s, r) in self.world.get_components(components.Image, components.Position, components.Size, components.Reactive):
            if r.x == 0:
                r.x = p.x
                r.y = p.y
            mousex, mousey = pygame.mouse.get_pos()
            mousex *= 1280 / pygame.display.get_surface().get_width()
            mousey *= 720 / pygame.display.get_surface().get_height()
            p.x = r.x + (r.x - mousex) / 10
            p.y = r.y + (r.y - mousey) / 10
            s.scale = 100 / min(400, max(100, math.sqrt((r.x - mousex) ** 2 + (r.y - mousey) ** 2)))

        self.world.add_processor(processors.RenderProcessor())
        self.world.add_processor(processors.InputProcessor(), priority=10)
        self.world.add_processor(processors.PhysicsProcessor(), priority=5)
        self.world.add_processor(processors.AnimationProcessor(), priority=5)
