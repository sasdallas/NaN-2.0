import scenebase
import pygame
import components
import processors
import interpolation
import random
import text
import os
import time
import util
import title
import fireball



def get_player(world):
    player = world.create_entity()
    image = components.Image("playerIdle.png")
    animation = components.Animation("playerSimple.png", splitx=80, framelength=.1)
    carry_image = components.Image("playerCarryIdle.png")
    carry_animation = components.Animation("playerCarrySimple.png", splitx=80, framelength=.1)
    jump = components.Audio("jump.ogg")
    throw = components.Audio("throw")
    world.add_component(player, components.Position(100, 560))
    world.add_component(player, components.Velocity())
    world.add_component(player, image)
    world.add_component(player, components.Size(80, 80))
    world.add_component(player, components.Player(image, animation, carry_image, carry_animation, jump, throw))

    return player


def create_entity(world, image, rect):
    entity = world.create_entity()
    world.add_component(entity, components.Image(image))
    world.add_component(entity, components.Position(rect.x, rect.y))
    world.add_component(entity, components.Size(rect.width, rect.height))
    return entity



def CreateFireball(world,x,y):
    fireimg = pygame.image.load("images/fireball.png")
    width = fireimg.get_width()
    height = fireimg.get_height()
    
    fireball = create_entity(world, "fireball.png", pygame.Rect(x,y,width,height))
    
    return fireball

def next_scene(from_scene, to_scene):
    from_scene.switch_to_scene(to_scene)

def fade_out(world):
    for ent, i in world.get_component(components.Image):
        world.add_component(ent, components.ChangeAlpha(0, 1))
    for ent, a in world.get_component(components.Animation):
        world.add_component(ent, components.ChangeAlpha(0, 1))

def fade_up(world, entity, from_scene, to_scene):
    world.add_component(entity, components.ChangePosition((0, -100), 4, interpolation.Smooth(), True, fade_out, world))
    world.add_component(entity, components.ChangeAlpha(0, 4, interpolation.Smooth()))
    world.add_component(entity, components.Delay(5, next_scene, from_scene, to_scene))

def notify(world, font, message, from_scene, to_scene):
    entity = world.create_entity()
    world.add_component(entity, components.Position(640, 500))
    world.add_component(entity, components.Image("speech.png"))
    util.drawText(world.component_for_entity(entity, components.Image).image, message, (255, 255, 255), pygame.Rect(30, 20, 246, 134), font)
    world.add_component(entity, components.Size(307, 173))
    world.add_component(entity, components.Delay(2, fade_up, world, entity, from_scene, to_scene))
    return entity


def FireballMessage(world):
    #since this isnt a class, we have to manually get font.
    
    font_path_for_fireball = os.path.join(components.get_base_path(), "kenpixel.ttf")
    small_font_fire = pygame.font.Font(font_path_for_fireball, 16)
    bubble = create_entity(world, "speech.png", pygame.Rect(200, 100, 307, 173))
    world.add_component(bubble, components.Hang())
    image = world.component_for_entity(bubble, components.Image).image
    #I used random strs
    firetexts = ["AHHHHH HOW ARE YOU SHOOTING FIREBALLS AHHHHH!!!!!!!!!!","OH MY GOD HE IS A DEMON!!! RUN!!!","CALL THE FIRE DEPARTMENT NAN JUST SPIT UP A FIREBALL!!!!"]
    util.drawText(image,str(random.choice(firetexts)),(255, 255, 255), pygame.Rect(30, 20, 246, 134),small_font_fire)
    


class SceneOne(scenebase.SceneBase):
    def __init__(self):
        scenebase.SceneBase.__init__(self, 'audio/Retro Reggae.ogg')

    def init(self):
        scenebase.SceneBase.init(self)

        bg = create_entity(self.world, "IntroBG.png", pygame.Rect(640, 360, 1280, 720))
        self.world.add_component(bg, components.Background())

        player = get_player(self.world)

        sword = create_entity(self.world, "sword.png", pygame.Rect(300, 560, 80, 80))
        self.world.add_component(sword, components.Velocity())
        self.world.add_component(sword, components.Audio("light"))
        #Yep, I added 8Bit explosions on the dragon.
        def dragon_hit():
            #I extracted the GIF Frames from my gif img of 8bit explosion and placed in nan/images/gifframes
            #Total of 23 frames, I will do for i in range(23) and update the image for each frame. Delay 0.05s
            #Create Entities
            frame = 1
            
            explosion1 = create_entity(self.world,"gifframes/frame_0_delay-0.05s.png",pygame.Rect(853,121,80,80))
            
            time.sleep(0.5)
            self.world.component_for_entity(explosion1,components.Image).image = pygame.image.load("images/gifframes/frame_" + str(frame) + "_delay-0.05s.png")
            frame=frame+1
                
                
                
            
            self.world.component_for_entity(dragon, components.Animation).frame = 1
            damage = notify(self.world, self.font, "999,999,999,999,999,999", self, text.TextScene("And thusly the skilled adventurer NaN took out yet another dragon. Dragon killing was no longer a dangerous quest but rather routine cleaning. With the dragon population dwindling NaN had time to help more people with their non life threatening problems.", SceneTwo()))
            image = self.font.render("999,999,999,999,999,999", False, (255, 128, 0))

            self.world.component_for_entity(damage, components.Image).image = image
            self.world.component_for_entity(damage, components.Position).x = 960
            self.world.component_for_entity(damage, components.Position).y = 320
            self.world.component_for_entity(damage, components.Size).width = image.get_width()
            self.world.component_for_entity(damage, components.Size).height = image.get_height()
        
            pygame.mixer.Sound(os.path.join(components.get_base_path(), 'audio', 'dragon.ogg')).play()

        dragon = self.world.create_entity()
        self.world.add_component(dragon, components.Position(1000, 500))
        self.world.add_component(dragon, components.Velocity(0, 0))
        self.world.add_component(dragon, components.Animation("dragon.png", splitx=640, frame=0))
        self.world.add_component(dragon, components.Size(640, 640))
        self.world.add_component(dragon, components.Touch(sword, rect=pygame.Rect(0, -400, -320, 0), touch=dragon_hit))

        def move_up(entity):
            self.world.add_component(entity, components.ChangePosition((0, -40), 1, interpolation.Smooth(), True, move_down, entity))
        def move_down(entity):
            self.world.add_component(entity, components.ChangePosition((0, 40), 1, interpolation.Smooth(), True, move_up, entity))

        tutorial = self.world.create_entity()
        image = self.font.render("use arrow keys or WASD to move", False, (32, 255, 128))
        self.world.add_component(tutorial, components.Position(640, 680))
        self.world.add_component(tutorial, components.Image(image=image))
        self.world.add_component(tutorial, components.Size(image.get_width(), image.get_height()))
        move_up(tutorial)

        clouds = []
        for i in [1,2,3,4,5,6]:
            cloud = create_entity(self.world, "cloud.png", pygame.Rect(random.randrange(100, 1180), random.randrange(75, 200), 160, 80))
            self.world.add_component(cloud, components.Background())
            self.world.add_component(cloud, components.Hang())
            clouds.append(cloud)

        self.world.add_processor(processors.RenderProcessor())
        self.world.add_processor(processors.InputProcessor(), priority=10)
        self.world.add_processor(processors.PhysicsProcessor(600), priority=5)
        self.world.add_processor(processors.AnimationProcessor(), priority=5)
        self.world.add_processor(processors.PlayerProcessor(player, 100), priority=25)
        self.world.add_processor(processors.Scene1Processor(player, tutorial, self.font), priority=20)

class SceneTwo(scenebase.SceneBase):
    def __init__(self):
        scenebase.SceneBase.__init__(self, 'audio/Retro Comedy.ogg')

    def init(self):
        scenebase.SceneBase.init(self)

        bg = create_entity(self.world, "OutsideSceneBG.png", pygame.Rect(640, 360, 1280, 720))
        self.world.add_component(bg, components.Background())

        player = get_player(self.world)

        flower = create_entity(self.world, "Flower.png", pygame.Rect(240, 560, 80, 80))
        self.world.add_component(flower, components.Velocity())
        self.world.add_component(flower, components.Flammable())
        self.world.add_component(flower, components.Audio("light"))

        vase = create_entity(self.world, "Vase.png", pygame.Rect(510, 560, 80, 80))
        self.world.add_component(vase, components.Velocity())
        self.world.add_component(vase, components.Flammable())
        self.world.add_component(vase, components.Audio("light"))

        guy = create_entity(self.world, "NPC2.png", pygame.Rect(340, 560, 80, 80))
        self.world.add_component(guy, components.Velocity())
        self.world.add_component(guy, components.Flammable())
        self.world.add_component(guy, components.Audio("grunt"))

        guy2 = create_entity(self.world, "NPC1.png", pygame.Rect(950, 560, 80, 80))
        self.world.add_component(guy2, components.Velocity())
        self.world.add_component(guy2, components.Flammable())
        self.world.add_component(guy2, components.Audio("grunt"))
        self.world.component_for_entity(guy2, components.Image).image = pygame.transform.flip(self.world.component_for_entity(guy2, components.Image).image, False, False)

        def puzzle_complete():
            notify(self.world, self.small_font, "You better not have dropped her or anything.", self, text.TextScene("With adventuring work in low demand and the cost of living constantly increasing, NaN was forced to stoop to more and more menial work.", SceneThree()))
            
        cat = create_entity(self.world, "Cat.png", pygame.Rect(1100, 170, 80, 80))
        self.world.add_component(cat, components.Hang())
        self.world.add_component(cat, components.Flammable())
        self.world.add_component(cat, components.Touch(guy, touch=puzzle_complete))
        self.world.add_component(cat, components.Audio("light"))

        bubble = create_entity(self.world, "speech.png", pygame.Rect(200, 100, 307, 173))
        self.world.add_component(bubble, components.Hang())
        image = self.world.component_for_entity(bubble, components.Image).image
        util.drawText(image, "Oh no! My wonderful cat has found herself stuck in a tree! Won't someone please help me?", (255, 255, 255), pygame.Rect(30, 20, 246, 134), self.small_font)

        self.world.add_processor(processors.RenderProcessor())
        self.world.add_processor(processors.InputProcessor(), priority=10)
        self.world.add_processor(processors.PhysicsProcessor(600), priority=5)
        self.world.add_processor(processors.AnimationProcessor(), priority=5)
        self.world.add_processor(processors.PlayerProcessor(player, 95), priority=25)

class SceneThree(scenebase.SceneBase):
    def __init__(self):
        scenebase.SceneBase.__init__(self, 'audio/Retro Polka.ogg')

    def init(self):
        scenebase.SceneBase.init(self)

        bg = create_entity(self.world, "HouseScene2BG.png", pygame.Rect(640, 360, 1280, 720))
        self.world.add_component(bg, components.Background())

        player = get_player(self.world)

        floor2 = create_entity(self.world, "WoodPlatform2.png", pygame.Rect(400, 390, 480, 40))
        self.world.add_component(floor2, components.Platform())
        self.world.add_component(floor2, components.Background())

        stair = create_entity(self.world, "WoodPlatform1.png", pygame.Rect(760, 500, 240, 40))
        self.world.add_component(stair, components.Platform())
        self.world.add_component(stair, components.Background())

        bed = create_entity(self.world, "Bed.png", pygame.Rect(260, 330, 160, 80))
        self.world.add_component(bed, components.Velocity())
        self.world.add_component(bed, components.Flammable())
        self.world.add_component(bed, components.Audio("heavy"))

        bookshelf = create_entity(self.world, "Bookshelf.png", pygame.Rect(420, 290, 80, 160))
        self.world.add_component(bookshelf, components.Velocity())
        self.world.add_component(bookshelf, components.Flammable())
        self.world.add_component(bookshelf, components.Audio("heavy"))

        chest = create_entity(self.world, "chest.png", pygame.Rect(540, 330, 80, 80))
        self.world.add_component(chest, components.Velocity())
        self.world.add_component(chest, components.Flammable())
        self.world.add_component(chest, components.Audio("chest"))

        guy = create_entity(self.world, "NPC1.png", pygame.Rect(280, 560, 80, 80))
        self.world.add_component(guy, components.Velocity())
        self.world.add_component(guy, components.Flammable())
        self.world.add_component(guy, components.Audio("grunt"))

        left_chair = create_entity(self.world, "Chair.png", pygame.Rect(430, 560, 80, 80))
        self.world.add_component(left_chair, components.Velocity())
        self.world.add_component(left_chair, components.Flammable())
        self.world.add_component(left_chair, components.Audio("light"))

        right_chair = create_entity(self.world, "Chair.png", pygame.Rect(610, 560, 80, 80))
        self.world.add_component(right_chair, components.Velocity())
        self.world.add_component(right_chair, components.Flammable())
        self.world.add_component(right_chair, components.Audio("light"))
        self.world.component_for_entity(right_chair, components.Image).image = pygame.transform.flip(self.world.component_for_entity(right_chair, components.Image).image, False, False)

        table = create_entity(self.world, "Table.png", pygame.Rect(520, 560, 80, 80))
        self.world.add_component(table, components.Velocity())
        self.world.add_component(table, components.Flammable())
        self.world.add_component(table, components.Audio("heavy"))

        def puzzle_complete():
            p = self.world.component_for_entity(player, components.Player)
            if p.holding is books:
                p.holding = None
            self.world.delete_entity(books)
            notify(self.world, self.small_font, "Wow, you got the books dirty. I can't use these anymore.", self, text.TextScene("These thankless jobs took their toll on NaN. He put on a friendly face, but inside he was growing weary...", SceneFour()))

        books = create_entity(self.world, "PileOfBooks.png", pygame.Rect(1000, 560, 80, 80))
        self.world.add_component(books, components.Velocity())
        self.world.add_component(books, components.Flammable())
        self.world.add_component(books, components.Touch(bookshelf, rect=pygame.Rect(5, 0, -10, 0), touch=puzzle_complete))
        self.world.add_component(books, components.Audio("light"))

        lamp = create_entity(self.world, "Chandelier.png", pygame.Rect(760, 170, 80, 80))
        self.world.add_component(lamp, components.Flammable(True))
        self.world.add_component(lamp, components.Hang())
        self.world.add_component(lamp, components.Audio("glass.ogg"))

        bubble = create_entity(self.world, "speech.png", pygame.Rect(1000, 100, 307, 173))
        self.world.add_component(bubble, components.Hang())
        image = self.world.component_for_entity(bubble, components.Image).image
        util.drawText(image, "Ah! NaN, just in time! I need your help putting my books away. They are very important!", (255, 255, 255), pygame.Rect(30, 20, 246, 134), self.small_font)

        self.world.add_processor(processors.RenderProcessor())
        self.world.add_processor(processors.InputProcessor(), priority=10)
        self.world.add_processor(processors.PhysicsProcessor(600), priority=5)
        self.world.add_processor(processors.AnimationProcessor(), priority=5)
        self.world.add_processor(processors.PlayerProcessor(player, 85), priority=25)

class SceneFour(scenebase.SceneBase):
    count = 0

    def __init__(self):
        scenebase.SceneBase.__init__(self, 'audio/Retro Beat.ogg')

    def init(self):
        scenebase.SceneBase.init(self)

        bg = create_entity(self.world, "HouseScene3BG.png", pygame.Rect(640, 360, 1280, 720))
        self.world.add_component(bg, components.Background())

        player = get_player(self.world)

        floor = self.world.create_entity()
        self.world.add_component(floor, components.Position(640, 560))
        self.world.add_component(floor, components.Size(1280, 100))
        #self.world.add_component(floor, components.Image("box1.png"))

        def spider_tally():
            self.count += 1
            if self.count == 3:
                puzzle_complete()

        for i in [(200, 320), (280, 240), (420, 230), (440, 400), (590, 300), (680, 170), (760, 390), (830, 230)]:
            spider = create_entity(self.world, "Cobweb.png", pygame.Rect(i[0], i[1], 80, 80))
            self.world.add_component(spider, components.Hang())
            self.world.add_component(spider, components.Flammable())
            self.world.add_component(spider, components.Audio("light"))
            self.world.add_component(spider, components.Touch(floor, touch=spider_tally))

        box = create_entity(self.world, "box1.png", pygame.Rect(520, 560, 80, 80))
        self.world.add_component(box, components.Velocity())
        self.world.add_component(box, components.Flammable(True))
        self.world.add_component(box, components.Audio("light"))

        guy = create_entity(self.world, "NPC3.png", pygame.Rect(210, 560, 80, 80))
        self.world.add_component(guy, components.Velocity())
        self.world.add_component(guy, components.Flammable())
        self.world.add_component(guy, components.Audio("grunt"))

        def puzzle_complete():
            notify(self.world, self.small_font, "Now get out of my barn!", self, text.TextScene("Lack of real adventuring work not only wore on NaN, but it dulled him. His body atrophied as his mind numbed, and he realized he could no longer perform the same feats he'd grown accustomed to.", SceneFive()))

        cat = create_entity(self.world, "Cat.png", pygame.Rect(1190, 560, 80, 80))
        self.world.add_component(cat, components.Velocity(0,0))
        self.world.add_component(cat, components.Flammable())
        self.world.add_component(cat, components.Audio("light"))

        bubble = create_entity(self.world, "speech.png", pygame.Rect(1000, 100, 307, 173))
        self.world.add_component(bubble, components.Hang())
        image = self.world.component_for_entity(bubble, components.Image).image
        util.drawText(image, "My barn is dusty and full of cobwebs. NaN! Come here and do this for me.", (255, 255, 255), pygame.Rect(30, 20, 246, 134), self.small_font)

        self.world.add_processor(processors.RenderProcessor())
        self.world.add_processor(processors.InputProcessor(), priority=10)
        self.world.add_processor(processors.PhysicsProcessor(600), priority=5)
        self.world.add_processor(processors.AnimationProcessor(), priority=5)
        self.world.add_processor(processors.PlayerProcessor(player, 75), priority=25)

class SceneFive(scenebase.SceneBase):
    def __init__(self):
        scenebase.SceneBase.__init__(self, 'audio/Space Cadet.ogg')

    def init(self):
        scenebase.SceneBase.init(self)

        bg = create_entity(self.world, "HouseSceneBlacksmithBG.png", pygame.Rect(640, 360, 1280, 720))
        self.world.add_component(bg, components.Background())

        player = get_player(self.world)

        for i in [("WoodPlatform3.png", 760, 390, 720, 40), ("WoodPlatformHalf.png", 280, 500, 120, 40), ("WoodPlatformThird.png", 360, 440, 80, 40), ("WoodPlatformThird.png", 200, 560, 80, 40)]:
            platform = create_entity(self.world, i[0], pygame.Rect(i[1], i[2], i[3], i[4]))
            self.world.add_component(platform, components.Platform())
            self.world.add_component(platform, components.Background())

        anvil = create_entity(self.world, "Anvil.png", pygame.Rect(710, 560, 80, 80))
        self.world.add_component(anvil, components.Velocity())
        self.world.add_component(anvil, components.Audio("heavy"))

        bed = create_entity(self.world, "Bed.png", pygame.Rect(500, 330, 160, 80))
        self.world.add_component(bed, components.Velocity())
        self.world.add_component(bed, components.Flammable())
        self.world.add_component(bed, components.Audio("heavy"))

        bookshelf = create_entity(self.world, "Bookshelf.png", pygame.Rect(640, 290, 80, 160))
        self.world.add_component(bookshelf, components.Velocity())
        self.world.add_component(bookshelf, components.Flammable())
        self.world.add_component(bookshelf, components.Audio("heavy"))

        guy = create_entity(self.world, "NPC3.png", pygame.Rect(280, 560, 80, 80))
        self.world.add_component(guy, components.Velocity())
        self.world.add_component(guy, components.Flammable())
        self.world.add_component(guy, components.Audio("grunt"))

        left_chair = create_entity(self.world, "Chair.png", pygame.Rect(480, 560, 80, 80))
        self.world.add_component(left_chair, components.Velocity())
        self.world.add_component(left_chair, components.Flammable())
        self.world.add_component(left_chair, components.Audio("light"))

        top_chair = create_entity(self.world, "Chair.png", pygame.Rect(770, 330, 80, 80))
        self.world.add_component(top_chair, components.Velocity())
        self.world.add_component(top_chair, components.Flammable())
        self.world.add_component(top_chair, components.Audio("light"))

        table = create_entity(self.world, "Table.png", pygame.Rect(570, 560, 80, 80))
        self.world.add_component(table, components.Velocity())
        self.world.add_component(table, components.Flammable())
        self.world.add_component(table, components.Audio("heavy"))

        def puzzle_complete():
            notify(self.world, self.small_font, "You got a crack in it. Thanks for nothing.", self, text.TextScene("NaN was depressed. For the majority of his life he was the strongest, fastest, all around best adventurer in the whole realm. But it was his own effectiveness led to his now pitiful existence.", SceneSix()))

        def open_container(container, item_string):
            if container is not None:
                p = self.world.component_for_entity(container, components.Position)
                self.world.delete_entity(container)
                item = create_entity(self.world, item_string, pygame.Rect(p.x, p.y, 80, 80))
                self.world.add_component(item, components.Audio("light"))
                self.world.add_component(item, components.Flammable())
                if container is chest:
                    self.world.add_component(item, components.Touch(guy, rect=pygame.Rect(0,0,0,0), touch=puzzle_complete))
                if self.world.component_for_entity(player, components.Player).holding == container:
                    self.world.component_for_entity(player, components.Player).holding = item
                    i = self.world.component_for_entity(item, components.Image)
                    s = self.world.component_for_entity(item, components.Size)
                    i.image = pygame.transform.rotate(i.image, 90)
                    tmp = s.width
                    s.width = s.height
                    s.height = tmp
                else:
                    v = self.world.component_for_entity(container, components.Velocity)
                    self.world.add_component(item, components.Velocity(v.x, v.y))
                self.world.component_for_entity(item, components.Audio).sound.play()

        chest = create_entity(self.world, "chest.png", pygame.Rect(1070, 330, 80, 80))
        self.world.add_component(chest, components.Velocity())
        self.world.add_component(chest, components.Flammable())
        self.world.add_component(chest, components.Touch(anvil, False, pygame.Rect(0,0,0,0), open_container, chest, "Vase.png"))
        self.world.add_component(chest, components.Audio("chest"))

        box = create_entity(self.world, "box1.png", pygame.Rect(860, 330, 80, 80))
        self.world.add_component(box, components.Velocity())
        self.world.add_component(box, components.Flammable())
        self.world.add_component(box, components.Touch(anvil, False, pygame.Rect(0,0,0,0), open_container, box, "Chair.png"))
        self.world.add_component(box, components.Audio("heavy"))

        box2 = create_entity(self.world, "box2.png", pygame.Rect(950, 330, 80, 80))
        self.world.add_component(box2, components.Velocity())
        self.world.add_component(box2, components.Flammable())
        self.world.add_component(box2, components.Touch(anvil, False, pygame.Rect(0,0,0,0), open_container, box2, "PileOfBooks.png"))
        self.world.add_component(box2, components.Audio("heavy"))

        lamp = create_entity(self.world, "Chandelier.png", pygame.Rect(520, 170, 80, 80))
        self.world.add_component(lamp, components.Flammable(True))
        self.world.add_component(lamp, components.Hang())

        lamp2 = create_entity(self.world, "Chandelier.png", pygame.Rect(1000, 170, 80, 80))
        self.world.add_component(lamp2, components.Flammable(True))
        self.world.add_component(lamp2, components.Hang())

        forge = create_entity(self.world, "Forge.png", pygame.Rect(1040, 520, 80, 160))
        self.world.add_component(anvil, components.Velocity())
        self.world.add_component(forge, components.Flammable(True))
        self.world.add_component(anvil, components.Audio("heavy"))

        workbench = create_entity(self.world, "Workbench.png", pygame.Rect(870, 560, 160, 80))
        self.world.add_component(workbench, components.Velocity())
        self.world.add_component(workbench, components.Flammable())
        self.world.add_component(workbench, components.Audio("heavy"))

        bubble = create_entity(self.world, "speech.png", pygame.Rect(200, 100, 307, 173))
        self.world.add_component(bubble, components.Hang())
        util.drawText(self.world.component_for_entity(bubble, components.Image).image, "Shoot, now where did that vase go? NaN, you touched it last. You need to find it for me!", (255, 255, 255), pygame.Rect(30, 20, 246, 134), self.small_font)

        self.world.add_processor(processors.RenderProcessor())
        self.world.add_processor(processors.InputProcessor(), priority=10)
        self.world.add_processor(processors.PhysicsProcessor(600), priority=5)
        self.world.add_processor(processors.AnimationProcessor(), priority=5)
        self.world.add_processor(processors.PlayerProcessor(player, 60), priority=25)

class SceneSix(scenebase.SceneBase):
    def __init__(self):
        scenebase.SceneBase.__init__(self, 'audio/Space Cadet.ogg')

    def init(self):
        scenebase.SceneBase.init(self)

        bg = create_entity(self.world, "HouseScene1BG.png", pygame.Rect(640, 360, 1280, 720))
        self.world.add_component(bg, components.Background())

        player = get_player(self.world)

        for i in [("WoodPlatform3.png", 520, 390, 720, 40), ("WoodPlatformHalf.png", 1000, 500, 120, 40), ("WoodPlatformThird.png", 920, 440, 80, 40), ("WoodPlatformThird.png", 1080, 560, 80, 40)]:
            platform = create_entity(self.world, i[0], pygame.Rect(i[1], i[2], i[3], i[4]))
            self.world.add_component(platform, components.Platform())
            self.world.add_component(platform, components.Background())

        for i in [(520, 330), (760, 330), (280, 560), (520, 560)]:
            bed = create_entity(self.world, "Bed.png", pygame.Rect(i[0], i[1], 160, 80))
            self.world.add_component(bed, components.Velocity())
            self.world.add_component(bed, components.Flammable())
            self.world.add_component(bed, components.Audio("heavy"))

        guy = create_entity(self.world, "NPC2.png", pygame.Rect(1000, 460, 80, 80))
        self.world.add_component(guy, components.Velocity())
        self.world.add_component(guy, components.Flammable())
        self.world.add_component(guy, components.Audio("grunt"))

        table = create_entity(self.world, "TableBig.png", pygame.Rect(280, 330, 160, 80))
        self.world.add_component(table, components.Velocity())
        self.world.add_component(table, components.Flammable())
        self.world.add_component(table, components.Audio("heavy"))

        def puzzle_complete():
            if self.world.component_for_entity(mug, components.Flammable).lit:
                p = self.world.component_for_entity(player, components.Player)
                if p.holding is mug:
                    p.holding = None
                self.world.delete_entity(mug)
                #self.switch_to_scene(text.TextScene("NaN was unsure how much longer he could go on like this. He still wanted to help people, but was filled with thoughts of inadequacy and self doubt.", SceneSeven()))
                notify(self.world, self.small_font, "Way to take your time.", self, text.TextScene("Eventually he'd had enough. He decided he would get revenge on his town for treating him this way.", SceneSeven()))
            else:
                complaint = create_entity(self.world, "speech.png", pygame.Rect(640, 500, 307, 173))
                self.world.add_component(complaint, components.ChangeAlpha(0, 4, interpolation.Smooth()))
                util.drawText(self.world.component_for_entity(complaint, components.Image).image, "It's cold! Heat it up for me.", (255, 255, 255), pygame.Rect(30, 20, 246, 134), self.small_font)

        mug = create_entity(self.world, "Mug.png", pygame.Rect(250, 160, 80, 80))
        self.world.add_component(mug, components.Hang())
        self.world.add_component(mug, components.Flammable())
        self.world.add_component(mug, components.Touch(guy, True, touch=puzzle_complete))
        self.world.add_component(mug, components.Audio("light"))

        lamp = create_entity(self.world, "Chandelier.png", pygame.Rect(520, 160, 80, 80))
        self.world.add_component(lamp, components.Flammable(True))
        self.world.add_component(lamp, components.Hang())

        lamp2 = create_entity(self.world, "Chandelier.png", pygame.Rect(760, 160, 80, 80))
        self.world.add_component(lamp2, components.Flammable(True))
        self.world.add_component(lamp2, components.Hang())

        fireplace = create_entity(self.world, "Fireplace.png", pygame.Rect(760, 520, 160, 160))
        self.world.add_component(fireplace, components.Flammable(True))
        self.world.add_component(fireplace, components.Velocity())
        self.world.add_component(fireplace, components.Background())

        # shelf
        create_entity(self.world, "shelf.png", pygame.Rect(250, 210, 80, 20))

        bubble = create_entity(self.world, "speech.png", pygame.Rect(1000, 100, 307, 173))
        self.world.add_component(bubble, components.Hang())
        image = self.world.component_for_entity(bubble, components.Image).image
        util.drawText(image, "About time you got here, NaN. I need my coffee stat! It's probably been sitting there for hours!", (255, 255, 255), pygame.Rect(30, 20, 246, 134), self.small_font)

        self.world.add_processor(processors.RenderProcessor())
        self.world.add_processor(processors.InputProcessor(), priority=10)
        self.world.add_processor(processors.PhysicsProcessor(600), priority=5)
        self.world.add_processor(processors.AnimationProcessor(), priority=5)
        self.world.add_processor(processors.PlayerProcessor(player, 40), priority=25)


class SceneSeven(scenebase.SceneBase):
    def __init__(self):
        scenebase.SceneBase.__init__(self, 'audio/Retro Reggae.ogg')

    def init(self):
        scenebase.SceneBase.init(self)

        bg = create_entity(self.world, "IntroBG.png", pygame.Rect(640, 360, 1280, 720))
        self.world.add_component(bg, components.Background())

        player = get_player(self.world)

        saddle = create_entity(self.world, "saddle.png", pygame.Rect(300, 560, 80, 80))
        self.world.add_component(saddle, components.Velocity())
        self.world.add_component(saddle, components.Audio("light"))
        def dragon_hit():
            self.world.component_for_entity(dragon, components.Animation).frame = 1
            damage = notify(self.world, self.font, "Dragon Tamed", self, text.TextScene("Sadly, the dragon refused to be tamed. Instead, though, it granted NaN the power of fireballs! Let's see how this turns out...",SceneEight()))
            image = self.font.render("Dragon Tamed", False, (255, 128, 0))
            self.world.component_for_entity(damage, components.Image).image = image
            self.world.component_for_entity(damage, components.Position).x = 960
            self.world.component_for_entity(damage, components.Position).y = 320
            self.world.component_for_entity(damage, components.Size).width = image.get_width()
            self.world.component_for_entity(damage, components.Size).height = image.get_height()
            pygame.mixer.Sound(os.path.join(components.get_base_path(), 'audio', 'dragon.ogg')).play()
        dragon = self.world.create_entity()
        self.world.add_component(dragon, components.Position(1000, 500))
        self.world.add_component(dragon, components.Velocity(0, 0))
        self.world.add_component(dragon, components.Animation("dragon.png", splitx=640, frame=0))
        self.world.add_component(dragon, components.Size(640, 640))
        self.world.add_component(dragon, components.Touch(saddle, rect=pygame.Rect(0, -400, -320, 0), touch=dragon_hit))

        
        def move_up(entity):
            self.world.add_component(entity, components.ChangePosition((0, -40), 1, interpolation.Smooth(), True, move_down, entity))
        def move_down(entity):
            self.world.add_component(entity, components.ChangePosition((0, 40), 1, interpolation.Smooth(), True, move_up, entity))





        tutorial = self.world.create_entity()
        image = self.font.render("'put' the saddle on the dragon", False, (32, 255, 128))
        self.world.add_component(tutorial, components.Position(640, 680))
        self.world.add_component(tutorial, components.Image(image=image))
        self.world.add_component(tutorial, components.Size(image.get_width(), image.get_height()))
        move_up(tutorial)


        clouds = []
        for i in [1,2,3,4,5,6]:
            cloud = create_entity(self.world, "cloud.png", pygame.Rect(random.randrange(100, 1180), random.randrange(75, 200), 160, 80))
            self.world.add_component(cloud, components.Background())
            self.world.add_component(cloud, components.Hang())
            clouds.append(cloud)

        self.world.add_processor(processors.RenderProcessor())
        self.world.add_processor(processors.InputProcessor(), priority=10)
        self.world.add_processor(processors.PhysicsProcessor(600), priority=5)
        self.world.add_processor(processors.AnimationProcessor(), priority=5)
        self.world.add_processor(processors.PlayerProcessor(player, 100), priority=25)
        self.world.add_processor(processors.DragonSceneProcessor(player, tutorial, self.font), priority=20)




class SceneEight(scenebase.SceneBase):
    def __init__(self):
        scenebase.SceneBase.__init__(self, 'audio/fireballed.mp3')

    def init(self):
        scenebase.SceneBase.init(self)

        
        bg = create_entity(self.world, "HouseScene2BG.png", pygame.Rect(640, 360, 1280, 720))
        self.world.add_component(bg, components.Background())

        player = get_player(self.world)

        floor2 = create_entity(self.world, "WoodPlatform2.png", pygame.Rect(400, 390, 480, 40))
        self.world.add_component(floor2, components.Platform())
        self.world.add_component(floor2, components.Background())

        stair = create_entity(self.world, "WoodPlatform1.png", pygame.Rect(760, 500, 240, 40))
        self.world.add_component(stair, components.Platform())
        self.world.add_component(stair, components.Background())

        bed = create_entity(self.world, "Bed.png", pygame.Rect(260, 330, 160, 80))
        self.world.add_component(bed, components.Velocity())
        self.world.add_component(bed, components.Flammable())
        
        self.world.add_component(bed, components.Audio("heavy"))

        bookshelf = create_entity(self.world, "Bookshelf.png", pygame.Rect(420, 290, 80, 160))
        self.world.add_component(bookshelf, components.Velocity())
        self.world.add_component(bookshelf, components.Flammable())
        self.world.add_component(bookshelf, components.Audio("heavy"))

        chest = create_entity(self.world, "chest.png", pygame.Rect(540, 330, 80, 80))
        self.world.add_component(chest, components.Velocity())
        self.world.add_component(chest, components.Flammable())
        self.world.add_component(chest, components.Audio("chest"))

        guy = create_entity(self.world, "NPC1.png", pygame.Rect(280, 560, 80, 80))
        self.world.add_component(guy, components.Velocity())
        self.world.add_component(guy, components.Flammable())
        self.world.add_component(guy, components.Audio("grunt"))

        left_chair = create_entity(self.world, "Chair.png", pygame.Rect(430, 560, 80, 80))
        self.world.add_component(left_chair, components.Velocity())
        self.world.add_component(left_chair, components.Flammable())
        self.world.add_component(left_chair, components.Audio("light"))

        right_chair = create_entity(self.world, "Chair.png", pygame.Rect(610, 560, 80, 80))
        self.world.add_component(right_chair, components.Velocity())
        self.world.add_component(right_chair, components.Flammable())
        self.world.add_component(right_chair, components.Audio("light"))
        self.world.component_for_entity(right_chair, components.Image).image = pygame.transform.flip(self.world.component_for_entity(right_chair, components.Image).image, False, False)

        table = create_entity(self.world, "Table.png", pygame.Rect(520, 560, 80, 80))
        self.world.add_component(table, components.Velocity())
        self.world.add_component(table, components.Flammable())
        self.world.add_component(table, components.Audio("heavy"))
        puzzledone = False
        def puzzle_complete():
            if self.world.component_for_entity(guy, components.Flammable).lit:
                puzzledone = True
                p = self.world.component_for_entity(player, components.Player)
                if p.holding is bed:
                    p.holding = None
                self.world.delete_entity(books)
                notify(self.world, self.small_font, "AHHHHHHHHHHH IM ON FIREEEEEE", self, text.TextScene("With a joyful look on his face, NaN strolled across the streets, looking for people to set on fire.", SceneNine()))
            
        books = create_entity(self.world, "PileOfBooks.png", pygame.Rect(1000, 560, 80, 80))
        self.world.add_component(books, components.Velocity())
        self.world.add_component(books, components.Flammable())
        self.world.add_component(books, components.Touch(bookshelf, rect=pygame.Rect(5, 0, -10, 0)))
        self.world.add_component(books, components.Audio("light"))

        lamp = create_entity(self.world, "Chandelier.png", pygame.Rect(760, 170, 80, 80))
        self.world.add_component(lamp, components.Flammable(True))
        self.world.add_component(lamp, components.Hang())
        self.world.add_component(lamp, components.Audio("glass.ogg"))

        bubble = create_entity(self.world, "speech.png", pygame.Rect(1000, 100, 307, 173))
        self.world.add_component(bubble, components.Hang())
        image = self.world.component_for_entity(bubble, components.Image).image
        util.drawText(image, "Where the heck is NaN? My other books fell off! Note: you must scene select next scene", (255, 255, 255), pygame.Rect(30, 20, 246, 134), self.small_font)

        
        
        def move_up(entity):
            self.world.add_component(entity, components.ChangePosition((0, -40), 1, interpolation.Smooth(), True, move_down, entity))
        def move_down(entity):
            self.world.add_component(entity, components.ChangePosition((0, 40), 1, interpolation.Smooth(), True, move_up, entity))  
        tutorial = self.world.create_entity()
        image = self.font.render("press f to launch a fireball", False, (32, 255, 128))
        self.world.add_component(tutorial, components.Position(640, 680))
        self.world.add_component(tutorial, components.Image(image=image))
        self.world.add_component(tutorial, components.Size(image.get_width(), image.get_height()))
        move_up(tutorial)
        
        
        
        self.world.add_processor(processors.RenderProcessor())
        self.world.add_processor(processors.InputProcessor(), priority=10)
        self.world.add_processor(processors.PhysicsProcessor(600), priority=5)
        self.world.add_processor(processors.AnimationProcessor(), priority=5)
        self.world.add_processor(processors.FireballPlayerProcessor(player, 85), priority=25)
        



class SceneNine(scenebase.SceneBase):
    def __init__(self):
        scenebase.SceneBase.__init__(self, 'audio/fireballed.mp3')

    def init(self):
        scenebase.SceneBase.init(self)

        bg = create_entity(self.world, "OutsideSceneBG.png", pygame.Rect(640, 360, 1280, 720))
        self.world.add_component(bg, components.Background())

        player = get_player(self.world)

        flower = create_entity(self.world, "Flower.png", pygame.Rect(240, 560, 80, 80))
        self.world.add_component(flower, components.Velocity())
        self.world.add_component(flower, components.Flammable())
        self.world.add_component(flower, components.Audio("light"))

        vase = create_entity(self.world, "Vase.png", pygame.Rect(510, 560, 80, 80))
        self.world.add_component(vase, components.Velocity())
        self.world.add_component(vase, components.Flammable())
        self.world.add_component(vase, components.Audio("light"))

        guy = create_entity(self.world, "NPC2.png", pygame.Rect(340, 560, 80, 80))
        self.world.add_component(guy, components.Velocity())
        self.world.add_component(guy, components.Flammable())
        self.world.add_component(guy, components.Audio("grunt"))

        guy2 = create_entity(self.world, "NPC1.png", pygame.Rect(950, 560, 80, 80))
        self.world.add_component(guy2, components.Velocity())
        self.world.add_component(guy2, components.Flammable())
        self.world.add_component(guy2, components.Audio("grunt"))
        self.world.component_for_entity(guy2, components.Image).image = pygame.transform.flip(self.world.component_for_entity(guy2, components.Image).image, False, False)

        def puzzle_complete():
            if self.world.component_for_entity(cat, components.Flammable).lit:
                notify(self.world, self.small_font, "MY CAT!!! GET THE HECK OUT OF HERE!!!!", self, text.TextScene("NaN went on to burn more people", SceneTen()))
            
        cat = create_entity(self.world, "Cat.png", pygame.Rect(1100, 170, 80, 80))
        self.world.add_component(cat, components.Hang())
        self.world.add_component(cat, components.Flammable())
        self.world.add_component(cat, components.Touch(guy, touch=puzzle_complete))
        self.world.add_component(cat, components.Audio("light"))

        bubble = create_entity(self.world, "speech.png", pygame.Rect(200, 100, 307, 173))
        self.world.add_component(bubble, components.Hang())
        image = self.world.component_for_entity(bubble, components.Image).image
        util.drawText(image, "Hey NaN, yeah you! Get my cat out of that tree! Note: giv her cat to continue, all other scenes are like this now!", (255, 255, 255), pygame.Rect(30, 20, 246, 134), self.small_font)

        self.world.add_processor(processors.RenderProcessor())
        self.world.add_processor(processors.InputProcessor(), priority=10)
        self.world.add_processor(processors.PhysicsProcessor(600), priority=5)
        self.world.add_processor(processors.AnimationProcessor(), priority=5)
        self.world.add_processor(processors.FireballPlayerProcessor(player, 95), priority=25)




#A boss battle!
"""class SceneTen(scenebase.SceneBase):
    def __init__(self):
        scenebase.SceneBase.__init__(self, 'audio/dragonbossbattle.mp3')

    def init(self):
        
        scenebase.SceneBase.init(self)
        dragonhealth = 100
        bg = create_entity(self.world, "IntroBG.png", pygame.Rect(640, 360, 1280, 720))
        self.world.add_component(bg, components.Background())

        player = get_player(self.world)

        saddle = create_entity(self.world, "saddle.png", pygame.Rect(300, 560, 80, 80))
        self.world.add_component(saddle, components.Velocity())
        self.world.add_component(saddle, components.Audio("light"))
        
        def dragon_hit():
            self.world.component_for_entity(dragon, components.Animation).frame = 1
            damage = notify(self.world, self.font, "Dragon Tamed", self, text.TextScene("Sadly, the dragon refused to be tamed. Instead, though, it granted NaN the power of fireballs! Let's see how this turns out...",SceneEight()))
            image = self.font.render("Dragon Tamed", False, (255, 128, 0))
            self.world.component_for_entity(damage, components.Image).image = image
            self.world.component_for_entity(damage, components.Position).x = 960
            self.world.component_for_entity(damage, components.Position).y = 320
            self.world.component_for_entity(damage, components.Size).width = image.get_width()
            self.world.component_for_entity(damage, components.Size).height = image.get_height()
            pygame.mixer.Sound(os.path.join(components.get_base_path(), 'audio', 'dragon.ogg')).play()
        dragon = self.world.create_entity()
        self.world.add_component(dragon, components.Position(1000, 500))
        self.world.add_component(dragon, components.Velocity(0, 0))
        self.world.add_component(dragon, components.Animation("dragon.png", splitx=640, frame=0))
        self.world.add_component(dragon, components.Size(640, 640))
        self.world.add_component(dragon, components.Touch(saddle, rect=pygame.Rect(0, -400, -320, 0), touch=dragon_hit))
        
        
        
        
        
        
        


        tutorial = self.world.create_entity()
        image = self.font.render("Dragon Health: " + str(dragonhealth), False, (32, 255, 128))
        self.world.add_component(tutorial, components.Position(640, 680))
        self.world.add_component(tutorial, components.Image(image=image))
        self.world.add_component(tutorial, components.Size(image.get_width(), image.get_height()))
        

        
        
        
        
        clouds = []
        for i in [1,2,3,4,5,6]:
            cloud = create_entity(self.world, "cloud.png", pygame.Rect(random.randrange(100, 1180), random.randrange(75, 200), 160, 80))
            self.world.add_component(cloud, components.Background())
            self.world.add_component(cloud, components.Hang())
            clouds.append(cloud)

        self.world.add_processor(processors.RenderProcessor())
        self.world.add_processor(processors.InputProcessor(), priority=10)
        self.world.add_processor(processors.PhysicsProcessor(600), priority=5)
        self.world.add_processor(processors.AnimationProcessor(), priority=5)
        self.world.add_processor(processors.FireballPlayerProcessor(player, 100), priority=25)
        try:
            fireball = processors.FireballPlayerProcessor.BossBattleFireballLoop()
        except:
            print("Exception")
 """        






class Scene10(scenebase.SceneBase):
    def __init__(self):
        scenebase.SceneBase.__init__(self, 'audio/fireballed.mp3')
    def init(self):
        scenebase.SceneBase.init(self)

        bg = create_entity(self.world, "HouseScene2BG.png", pygame.Rect(640, 360, 1280, 720))
        self.world.add_component(bg, components.Background())

        player = get_player(self.world)

        floor2 = create_entity(self.world, "WoodPlatform2.png", pygame.Rect(400, 390, 480, 40))
        self.world.add_component(floor2, components.Platform())
        self.world.add_component(floor2, components.Background())

        stair = create_entity(self.world, "WoodPlatform1.png", pygame.Rect(760, 500, 240, 40))
        self.world.add_component(stair, components.Platform())
        self.world.add_component(stair, components.Background())

        bed = create_entity(self.world, "Bed.png", pygame.Rect(260, 330, 160, 80))
        self.world.add_component(bed, components.Velocity())
        self.world.add_component(bed, components.Flammable())
        self.world.add_component(bed, components.Audio("heavy"))

        bookshelf = create_entity(self.world, "Bookshelf.png", pygame.Rect(420, 290, 80, 160))
        self.world.add_component(bookshelf, components.Velocity())
        self.world.add_component(bookshelf, components.Flammable())
        self.world.add_component(bookshelf, components.Audio("heavy"))

        chest = create_entity(self.world, "chest.png", pygame.Rect(540, 330, 80, 80))
        self.world.add_component(chest, components.Velocity())
        self.world.add_component(chest, components.Flammable())
        self.world.add_component(chest, components.Audio("chest"))

        guy = create_entity(self.world, "NPC1.png", pygame.Rect(280, 560, 80, 80))
        self.world.add_component(guy, components.Velocity())
        self.world.add_component(guy, components.Flammable())
        self.world.add_component(guy, components.Audio("grunt"))

        left_chair = create_entity(self.world, "Chair.png", pygame.Rect(430, 560, 80, 80))
        self.world.add_component(left_chair, components.Velocity())
        self.world.add_component(left_chair, components.Flammable())
        self.world.add_component(left_chair, components.Audio("light"))

        right_chair = create_entity(self.world, "Chair.png", pygame.Rect(610, 560, 80, 80))
        self.world.add_component(right_chair, components.Velocity())
        self.world.add_component(right_chair, components.Flammable())
        self.world.add_component(right_chair, components.Audio("light"))
        self.world.component_for_entity(right_chair, components.Image).image = pygame.transform.flip(self.world.component_for_entity(right_chair, components.Image).image, False, False)

        table = create_entity(self.world, "Table.png", pygame.Rect(520, 560, 80, 80))
        self.world.add_component(table, components.Velocity())
        self.world.add_component(table, components.Flammable())
        self.world.add_component(table, components.Audio("heavy"))

        def puzzle_complete():
            if self.world.component_for_entity(ps4, components.Flammable).lit:

                p = self.world.component_for_entity(player, components.Player)
                if p.holding is ps4:
                    p.holding = None
                self.world.delete_entity(ps4)
                notify(self.world, self.small_font, "THANKS NAN FOR BURNING MY GARBAGE PS4", self, text.TextScene("These thankless jobs took their toll on NaN. He put on a friendly face, but inside he was growing weary...", SceneFour()))
            
            
        ps4 = create_entity(self.world, "playstation.png", pygame.Rect(1000, 560, 80, 80))
        self.world.add_component(ps4, components.Velocity())
        self.world.add_component(ps4, components.Flammable())
        self.world.add_component(ps4, components.Touch(bookshelf, rect=pygame.Rect(5, 0, -10, 0), touch=puzzle_complete))
        self.world.add_component(ps4, components.Audio("light"))

        lamp = create_entity(self.world, "Chandelier.png", pygame.Rect(760, 170, 80, 80))
        self.world.add_component(lamp, components.Flammable(True))
        self.world.add_component(lamp, components.Hang())
        self.world.add_component(lamp, components.Audio("glass.ogg"))

        bubble = create_entity(self.world, "speech.png", pygame.Rect(1000, 100, 307, 173))
        self.world.add_component(bubble, components.Hang())
        image = self.world.component_for_entity(bubble, components.Image).image
        util.drawText(image, "EY NAN MOVE MY PS4 TO THE BOOKSHELF", (255, 255, 255), pygame.Rect(30, 20, 246, 134), self.small_font)

        self.world.add_processor(processors.RenderProcessor())
        self.world.add_processor(processors.InputProcessor(), priority=10)
        self.world.add_processor(processors.PhysicsProcessor(600), priority=5)
        self.world.add_processor(processors.AnimationProcessor(), priority=5)
        self.world.add_processor(processors.PlayerProcessor(player, 85), priority=25)
        self.world.add_processor(processors.FireballPlayerProcessor(player, 85), priority=25)

