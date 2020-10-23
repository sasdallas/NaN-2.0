
import pygame
import esper
import components
import math
import util
import interpolation
import random
import game
import scenebase
import numpy as np
# TODO clean up, abstract, w/e
class RenderProcessor(esper.Processor):
    def __init__(self):
        esper.Processor.__init__(self)

    def render(self, ent, p, s, dt, screen):
        if self.world.has_component(ent, components.Image):
            i = self.world.component_for_entity(ent, components.Image)
            image = pygame.transform.scale(i.image, (int(s.width * s.scale), int(s.height * s.scale)))
            self.render_image(image, p, s, i.alpha, i.blend, screen)
        elif self.world.has_component(ent, components.Animation):
            a = self.world.component_for_entity(ent, components.Animation)
            a.time += dt
            frame = (a.time // a.framelength) % a.maxframes
            if a.framelength == -1:
                frame = a.frame
            rect = pygame.Rect(frame * a.splitx, 0, a.splitx, a.image.get_height())
            image = pygame.transform.scale(a.image.subsurface(rect), (int(s.width * s.scale), int(s.height * s.scale)))
            self.render_image(image, p, s, a.alpha, a.blend, screen)

    def render_image(self, image, p, s, alpha, blend, screen):
        if alpha == 255:
            screen.blit(image, (p.x - s.width * s.scale // 2, p.y - s.height * s.scale // 2), special_flags=blend)
        else:
            util.blit_alpha(screen, image, (p.x - s.width * s.scale // 2, p.y - s.height * s.scale // 2), alpha, blend)

    def process(self, filtered_events, pressed_keys, dt, screen):
        for ent, (b, p, s) in self.world.get_components(components.Background, components.Position, components.Size):
            self.render(ent, p, s, dt, screen)

        for ent, (a, p, s) in self.world.get_components(components.Animation, components.Position, components.Size):
            if self.world.has_component(ent, components.Player) or self.world.has_component(ent, components.Background):
                continue
            self.render(ent, p, s, dt, screen)

        for ent, (i, p, s) in self.world.get_components(components.Image, components.Position, components.Size):
            if self.world.has_component(ent, components.Player) or self.world.has_component(ent, components.Background):
                continue
            self.render(ent, p, s, dt, screen)

        for ent, (c, p) in self.world.get_components(components.Circle, components.Position):
            pygame.draw.circle(screen, c.color, (int(p.x), int(p.y)), c.radius, c.width)

        for ent, (r, p) in self.world.get_components(components.Rect, components.Position):
            r.rect.x = p.x
            r.rect.y = p.y
            pygame.draw.rect(screen, r.color, r.rect)

        for ent, (pl, p, s) in self.world.get_components(components.Player, components.Position, components.Size):
            self.render(ent, p, s, dt, screen)

class InputProcessor(esper.Processor):
    def __init__(self):
        esper.Processor.__init__(self)

    def process(self, filtered_events, pressed_keys, dt, screen):
        for event in filtered_events:
            if event.type == pygame.MOUSEMOTION:
                x, y = pygame.mouse.get_pos()
                x *= 1280 / pygame.display.get_surface().get_width()
                y *= 720 / pygame.display.get_surface().get_height()
                for ent, (s, p, o) in self.world.get_components(components.Size, components.Position, components.Over):
                    if p.x - s.width * s.scale // 2 <= x and p.x + s.width * s.scale // 2 >= x and p.y - s.height * s.scale / 2 <= y and p.y + s.height * s.scale // 2 >= y:
                        if not o.active:
                            o.enterf(ent if o.entity is None else o.entity)
                            o.active = True
                    elif o.active:
                        o.exitf(ent if o.entity is None else o.entity)
                        o.active = False
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                x *= 1280 / pygame.display.get_surface().get_width()
                y *= 720 / pygame.display.get_surface().get_height()
                for ent, (s, p, c) in self.world.get_components(components.Size, components.Position, components.Click):
                    if p.x - s.width * s.scale // 2 <= x and p.x + s.width * s.scale // 2 >= x and p.y - s.height // 2 <= y and p.y + s.height // 2 >= y:
                        c.run(*c.args)
                        if (self.world.has_component(ent, components.Audio)):
                            self.world.component_for_entity(ent, components.Audio).sound.play()

class PlayerProcessor(esper.Processor):
    def __init__(self, player, vitality):
        esper.Processor.__init__(self)
        self.player = player
        self.vitality = vitality

    def process(self, filtered_events, pressed_keys, dt, screen):
        v = self.world.component_for_entity(self.player, components.Velocity)
        p = self.world.component_for_entity(self.player, components.Player)
        s = self.world.component_for_entity(self.player, components.Size)
        pos = self.world.component_for_entity(self.player, components.Position)
        v.x = 0
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            v.x -= 3 * self.vitality
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            v.x += 3 * self.vitality
            
        if (p.facing_right and v.x < 0) or (not p.facing_right and v.x > 0):
            p.facing_right = not p.facing_right
            p.image.image = pygame.transform.flip(p.image.image, True, False)
            p.animation.image = pygame.transform.flip(p.animation.image, True, False)
            p.carry_image.image = pygame.transform.flip(p.carry_image.image, True, False)
            p.carry_animation.image = pygame.transform.flip(p.carry_animation.image, True, False)
        if v.x == 0 and self.world.has_component(self.player, components.Animation):
            self.world.remove_component(self.player, components.Animation)
            if p.holding:
                self.world.add_component(self.player, p.carry_image)
            else:
                self.world.add_component(self.player, p.image)
        elif v.x != 0 and self.world.has_component(self.player, components.Image):
            self.world.remove_component(self.player, components.Image)
            if p.holding:
                self.world.add_component(self.player, p.carry_animation)
            else:
                self.world.add_component(self.player, p.animation)
        for event in filtered_events:
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_SPACE) and v.y == 0:
                    v.y -= 6 * self.vitality
                    p.jump.sound.play()
                elif event.key == pygame.K_e:
                    if p.holding:
                        if self.world.has_component(self.player, components.Image):
                            self.world.remove_component(self.player, components.Image)
                            self.world.add_component(self.player, p.image)
                        elif self.world.has_component(self.player, components.Animation):
                            self.world.remove_component(self.player, components.Animation)
                            self.world.add_component(self.player, p.animation)
                        i = self.world.component_for_entity(p.holding, components.Image)
                        s = self.world.component_for_entity(p.holding, components.Size)
                        i.image = pygame.transform.rotate(i.image, -90)
                        tmp = s.width
                        s.width = s.height
                        s.height = tmp
                        self.world.add_component(p.holding, components.Velocity(0,0))
                        p.holding = None
                    else:
                        rect = pygame.Rect(pos.x, pos.y - s.height * s.scale / 2, s.width * s.scale * (1 if p.facing_right else -1), s.height * s.scale)
                        rect.normalize()
                        for ent, (p2, i, s, v) in self.world.get_components(components.Position, components.Image, components.Size, components.Velocity):
                            if self.world.has_component(ent, components.Player):
                                continue
                            if rect.collidepoint(p2.x, p2.y):
                                p.holding = ent
                                if self.world.has_component(self.player, components.Image):
                                    self.world.remove_component(self.player, components.Image)
                                    self.world.add_component(self.player, p.carry_image)
                                elif self.world.has_component(self.player, components.Animation):
                                    self.world.remove_component(self.player, components.Animation)
                                    self.world.add_component(self.player, p.carry_animation)
                                if self.world.has_component(ent, components.RotationalVelocity):
                                    r = self.world.component_for_entity(ent, components.RotationalVelocity)
                                    i.image = r.image
                                    s.width = r.width
                                    s.height = r.height
                                    self.world.remove_component(ent, components.RotationalVelocity)
                                i.image = pygame.transform.rotate(i.image, 90)
                                tmp = s.width
                                s.width = s.height
                                s.height = tmp
                                self.world.remove_component(ent, components.Velocity)
                                if self.world.has_component(ent, components.Audio):
                                    self.world.component_for_entity(ent, components.Audio).sound.play()
                                break
            elif event.type == pygame.MOUSEBUTTONDOWN and p.holding:
                if self.world.has_component(self.player, components.Image):
                    self.world.remove_component(self.player, components.Image)
                    self.world.add_component(self.player, p.image)
                elif self.world.has_component(self.player, components.Animation):
                    self.world.remove_component(self.player, components.Animation)
                    self.world.add_component(self.player, p.animation)
                i = self.world.component_for_entity(p.holding, components.Image)
                s = self.world.component_for_entity(p.holding, components.Size)
                i.image = pygame.transform.rotate(i.image, -90)
                tmp = s.width
                s.width = s.height
                s.height = tmp
                x = event.pos[1] * 1280 / pygame.display.get_surface().get_width()
                y = event.pos[0] * 720 / pygame.display.get_surface().get_height()
                angle = math.atan2(x - pos.y, y - pos.x) % (2 * math.pi)
                self.world.add_component(p.holding, components.Velocity(math.cos(angle)*16 * self.vitality, math.sin(angle)*12 * self.vitality))
                self.world.add_component(p.holding, components.RotationalVelocity(320))
                p.holding = None
                p.throw.sound.play()

        if p.holding:
            p3 = self.world.component_for_entity(p.holding, components.Position)
            p3.x = pos.x
            p3.y = pos.y - s.height + 10

class PhysicsProcessor(esper.Processor):
    def __init__(self, ground=-1):
        esper.Processor.__init__(self)
        self.ground = ground

    def remove_entity(self, entity):
        self.world.delete_entity(entity)

    def process(self, filtered_events, pressed_keys, dt, screen):
        for ent, (p, s, v) in self.world.get_components(components.Position, components.Size, components.Velocity):
            if v.y == 0 and self.world.has_component(ent, components.RotationalVelocity):
                r = self.world.component_for_entity(ent, components.RotationalVelocity)
                i = self.world.component_for_entity(ent, components.Image)
                i.image = r.image
                s.width = r.width
                s.height = r.height
                self.world.remove_component(ent, components.RotationalVelocity)

            v.y = min(v.y + 9.81*100*dt, 53*100) # terminal velocity
            if not self.world.has_component(ent, components.Player):
                v.x *= .98

            p.x = max(min(p.x + v.x * dt, 1280), 0)
            if self.ground != -1:
                p.y = min(p.y + v.y * dt, self.ground - s.height * s.scale / 2)

                if p.y >= self.ground - s.height * s.scale / 2 and v.y > 0:
                    v.y = 0

            else:
                p.y -= v.y * dt
        #Touch Physics
        for ent, (t, p, s)  in self.world.get_components(components.Touch, components.Position, components.Size):
            rect = pygame.Rect(p.x + t.rect.x, p.y + s.height / 2 + t.rect.y, s.width + t.rect.width, s.height + t.rect.height)
            tp = self.world.component_for_entity(t.target, components.Position)
            ts = self.world.component_for_entity(t.target, components.Size)
            if rect.colliderect(pygame.Rect(tp.x, tp.y, ts.width, ts.height)):
                if not t.active:
                    t.touch(*t.args)
                    if t.multi:
                        t.active = True
                    else:
                        self.world.remove_component(ent, components.Touch)
            else:
                t.active = False
        #Hanging Object Physics
        for hangEnt, (h, p, s) in self.world.get_components(components.Hang, components.Position, components.Size):
            rect = pygame.Rect(p.x, p.y, s.width, s.height)
            for ent, (v, tp, ts) in self.world.get_components(components.Velocity, components.Position, components.Size):
                if not self.world.has_component(ent, components.Player):
                    if rect.colliderect(pygame.Rect(tp.x, tp.y, ts.width, ts.height)):
                        if self.world.has_component(hangEnt, components.Hang):
                            self.world.remove_component(hangEnt, components.Hang)
                        self.world.add_component(hangEnt, components.Velocity(0,0))
                        break
        #Platform physics
        for platEnt, (tl, box, pf) in self.world.get_components(components.Position, components.Size, components.Platform):
            for ent, (p, s, v) in self.world.get_components(components.Position, components.Size, components.Velocity):
                if (tl.x - box.width / 2) < p.x < (tl.x + box.width / 2) and (tl.y - box.height) < (p.y + s.height / 2) - 20 < tl.y:
                    if v.y > 0:
                        p.y = min(((tl.y - box.height) - s.height / 2) + 20, p.y)
                    v.y = min(0, v.y)
        #Flamable stuff
        for flamEnt, (f, p, s) in self.world.get_components(components.Flammable, components.Position, components.Size):
            if f.lit:
                if not self.world.has_component(flamEnt, components.Delay):
                    flame = self.world.create_entity()
                    self.world.add_component(flame, components.Position(p.x - s.width / 2 + random.random() * s.width, p.y - s.height / 2 + random.random() * s.height))
                    self.world.add_component(flame, components.Size(60,60))
                    size = int(random.random() * 20)
                    self.world.add_component(flame, components.Rect((255, random.random() * 255, 0), pygame.Rect(0, 0, size, size)))
                    self.world.add_component(flame, components.ChangePosition((-25 + random.random() * 50, -50 - random.random() * 100), 1, interpolation.PowIn(2), True, self.remove_entity, flame))
                    self.world.add_component(flamEnt, components.Delay(.03))

                for ent, (f2, tp, ts) in self.world.get_components(components.Flammable, components.Position, components.Size):
                    if not f2.lit:
                        rect = pygame.Rect(p.x, p.y, s.width, s.height)
                        if rect.colliderect(pygame.Rect(tp.x, tp.y, ts.width, ts.height)):
                            f2.lit = True

class AnimationProcessor(esper.Processor):
    def __init__(self):
        esper.Processor.__init__(self)

    def process(self, filtered_events, pressed_keys, dt, screen):
        to_remove = []
        to_run = []
        # Position Animation
        for ent, (p, c) in self.world.get_components(components.Position, components.ChangePosition):
            if c.current is None:
                c.current = dt
                c.original = (p.x, p.y)
            else:
                c.current += dt

            if c.current >= c.time:
                to_remove.append((ent, components.ChangePosition))
                if c.chain:
                    to_run.append((c.chain, c.args))
            if c.relative:
                x,y = c.target
                ox, oy = c.original
                x = x * (c.interp.apply(min(1, c.current / c.time)) - c.interp.apply(min(1, (c.current - dt) / c.time)))
                y = y * (c.interp.apply(min(1, c.current / c.time)) - c.interp.apply(min(1, (c.current - dt) / c.time)))
                
                p.x += x
                p.y += y
            else:
                x,y = c.target
                ox, oy = c.original
                percent = min(1, c.current / c.time)
                x = x * c.interp.apply(percent) + ox * (1 - c.interp.apply(percent))
                y = y * c.interp.apply(percent) + oy * (1 - c.interp.apply(percent))

                p.x = x
                p.y = y

        # Size Animation
        for ent, (s, c) in self.world.get_components(components.Size, components.ChangeSize):
            if not c.current:
                c.current = dt
                c.original = s.scale
            else:
                c.current += dt

            if c.current >= c.time:
                scale = c.target
                to_remove.append((ent, components.ChangeSize))
                if c.chain:
                    to_run.append((c.chain, c.args))
            else:
                scale = c.target * c.interp.apply(c.current / c.time) + c.original * (1 - c.interp.apply(c.current / c.time))

            s.scale = scale

        # Velocity Animation
        for ent, (v, c) in self.world.get_components(components.Velocity, components.ChangeVelocity):
            if not c.current:
                c.current = dt
                c.original = (v.x,v.y)
            else:
                c.current += dt

            if c.current >= c.time:
                x,y = c.target
                to_remove.append((ent, components.ChangeVelocity))
                if c.chain:
                    to_run.append((c.chain, c.args))
            else:
                x,y = c.target
                ox, oy = c.original
                x = x * c.interp.apply(c.current / c.time) + ox * (1 - c.interp.apply(c.current / c.time))
                y = y * c.interp.apply(c.current / c.time) + oy * (1 - c.interp.apply(c.current / c.time))

            v.x = x
            v.y = y

        # Alpha Animation
        for ent, a in self.world.get_component(components.ChangeAlpha):
            if not a.current:
                a.current = dt
                if self.world.has_component(ent, components.Image):
                    a.original = self.world.component_for_entity(ent, components.Image).alpha / 255
                elif self.world.has_component(ent, components.Animation):
                    a.original = self.world.component_for_entity(ent, components.Animation).alpha / 255
            else:
                a.current += dt

            if a.current >= a.time:
                alpha = a.target
                to_remove.append((ent, components.ChangeAlpha))
                if a.chain:
                    to_run.append((a.chain, a.args))
            else:
                alpha = a.target * a.interp.apply(a.current / a.time) + a.original * (1 - a.interp.apply(a.current / a.time))

            if self.world.has_component(ent, components.Image):
                self.world.component_for_entity(ent, components.Image).alpha = alpha * 255
            elif self.world.has_component(ent, components.Animation):
                self.world.component_for_entity(ent, components.Animation).alpha = alpha * 255

        # Circle Animation
        for ent, (v, c) in self.world.get_components(components.Velocity, components.CircleAnimation):
            c.current += dt
            oldy = v.y
            v.x = math.cos(math.pi * 2 * c.current / c.time) * c.radius / c.time
            v.y = math.sin(math.pi * 2 * c.current / c.time) * c.radius / c.time
            if abs((math.pi * 2 * c.current / c.time) % (2 * math.pi) - c.stopangle % (2 * math.pi)) < .1:
                if not c.loop:
                    to_remove.append((ent, components.Velocity))
                    to_remove.append((ent, components.CircleAnimation))
                if c.chain:
                    to_run.append((c.chain, c.args))

        # Rotational Velocity
        for ent, (i, r, s) in self.world.get_components(components.Image, components.RotationalVelocity, components.Size):
            if not r.image:
                r.image = i.image
                r.width = s.width
                r.height = s.height
            width = i.image.get_width()
            height = i.image.get_height()
            r.angle += dt * r.speed
            i.image = pygame.transform.rotate(r.image, r.angle)
            s.width *= i.image.get_width() / width
            s.height *= i.image.get_height() / height

        # Delay Animation
        for ent, d in self.world.get_component(components.Delay):
            d.time -= dt
            if d.time <= 0:
                to_remove.append((ent, components.Delay))
                if d.chain:
                    to_run.append((d.chain, d.args))

        # Remove Components
        for (ent, comp) in to_remove:
            self.world.remove_component(ent, comp)

        for (chain, args) in to_run:
            chain(*args)

class TextProcessor(esper.Processor):
    def __init__(self, callback):
        esper.Processor.__init__(self)
        self.callback = callback

    def process(self, filtered_events, pressed_keys, dt, screen):
        for event in filtered_events:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.callback()

class Scene1Processor(esper.Processor):
    moved = False

    def __init__(self, player, tutorial, font):
        esper.Processor.__init__(self)
        self.player = player
        self.tutorial = tutorial
        self.font = font

    def process(self, filtered_events, pressed_keys, dt, screen):
        p = self.world.component_for_entity(self.player, components.Position)
        if p.x > 900:
            p.x = 900

        for event in filtered_events:
            if event.type == pygame.KEYDOWN:
                if self.moved and event.key == pygame.K_e:
                    image = self.font.render("aim your mouse and click to throw", False, (32, 255, 128))
                    self.world.component_for_entity(self.tutorial, components.Image).image = image
                    imgs = self.world.component_for_entity(self.tutorial, components.Size)
                    imgs.width = image.get_width()
                    imgs.height = image.get_height()
                elif not self.moved and event.key in [pygame.K_w, pygame.K_a, pygame.K_d, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT]:
                    image = self.font.render("press E to pick up your sword", False, (32, 255, 128))
                    self.world.component_for_entity(self.tutorial, components.Image).image = image
                    imgs = self.world.component_for_entity(self.tutorial, components.Size)
                    imgs.width = image.get_width()
                    imgs.height = image.get_height()
                    self.moved = True
                
class DragonSceneProcessor(esper.Processor):
    moved = False

    def __init__(self, player, tutorial, font):
        esper.Processor.__init__(self)
        self.player = player
        self.tutorial = tutorial
        self.font = font

    def process(self, filtered_events, pressed_keys, dt, screen):
        p = self.world.component_for_entity(self.player, components.Position)
        if p.x > 900:
            p.x = 900

        for event in filtered_events:
            if event.type == pygame.KEYDOWN:
                if self.moved and event.key == pygame.K_e:
                    image = self.font.render("DO IT", False, (32, 255, 128))
                    self.world.component_for_entity(self.tutorial, components.Image).image = image
                    imgs = self.world.component_for_entity(self.tutorial, components.Size)
                    imgs.width = image.get_width()
                    imgs.height = image.get_height()
                elif not self.moved and event.key in [pygame.K_w, pygame.K_a, pygame.K_d, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT]:
                    image = self.font.render("is it this hard to grab a SWORD?", False, (32, 255, 128))
                    self.world.component_for_entity(self.tutorial, components.Image).image = image
                    imgs = self.world.component_for_entity(self.tutorial, components.Size)
                    imgs.width = image.get_width()
                    imgs.height = image.get_height()
                    self.moved = True

class FireballPlayerProcessor(esper.Processor):
    def __init__(self, player, vitality):
        esper.Processor.__init__(self)
        self.player = player
        self.vitality = vitality
        self.MessageShown = False
        self.player_is_facing_right = True
        self.player_is_facing_left = False

    
    
    def process(self, filtered_events, pressed_keys, dt, screen):
        v = self.world.component_for_entity(self.player, components.Velocity)
        p = self.world.component_for_entity(self.player, components.Player)
        s = self.world.component_for_entity(self.player, components.Size)
        pos = self.world.component_for_entity(self.player, components.Position)
        v.x = 0
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            v.x -= 3 * self.vitality
            self.player_is_facing_right = False
            self.player_is_facing_left = True
        elif pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            v.x += 3 * self.vitality
            self.player_is_facing_right = True
            self.player_is_facing_left = False
        
        p.holdingfireball = False
            
            
        if (p.facing_right and v.x < 0) or (not p.facing_right and v.x > 0):
            p.facing_right = not p.facing_right
            self.player_is_facing_right = False
            p.image.image = pygame.transform.flip(p.image.image, True, False)
            p.animation.image = pygame.transform.flip(p.animation.image, True, False)
            p.carry_image.image = pygame.transform.flip(p.carry_image.image, True, False)
            p.carry_animation.image = pygame.transform.flip(p.carry_animation.image, True, False)
        if v.x == 0 and self.world.has_component(self.player, components.Animation):
            self.world.remove_component(self.player, components.Animation)
            if p.holding:
                self.world.add_component(self.player, p.carry_image)
            else:
                self.world.add_component(self.player, p.image)
        elif v.x != 0 and self.world.has_component(self.player, components.Image):
            self.world.remove_component(self.player, components.Image)
            if p.holding:
                self.world.add_component(self.player, p.carry_animation)
            else:
                self.world.add_component(self.player, p.animation)
        for event in filtered_events:
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_SPACE) and v.y == 0:
                    v.y -= 6 * self.vitality
                    p.jump.sound.play()
                elif event.key == pygame.K_f:
                    if self.MessageShown == False:
                        game.FireballMessage(self.world)
                        self.MessageShown = True
                        
                    global fireball
                    self.fireball = game.CreateFireball(self.world,pos.x,pos.y)
                    self.world.add_component(self.fireball, components.Position(pos.x,pos.y))
                    self.world.add_component(self.fireball, components.Velocity())
                    self.world.add_component(self.fireball, components.Flammable(True))
                    v = self.world.component_for_entity(self.fireball, components.Velocity)
                    if self.player_is_facing_right == True:
                        while not v.x > 1300:
                            v.x += 3
                            
                    elif self.player_is_facing_right == False:
                        while not v.x == 0:
                            v.x -= 3
                            
                    
                            
                        
                        
                        
                        
                elif event.key == pygame.K_e:
                    if p.holding:
                        if self.world.has_component(self.player, components.Image):
                            self.world.remove_component(self.player, components.Image)
                            self.world.add_component(self.player, p.image)
                        elif self.world.has_component(self.player, components.Animation):
                            self.world.remove_component(self.player, components.Animation)
                            self.world.add_component(self.player, p.animation)
                        i = self.world.component_for_entity(p.holding, components.Image)
                        s = self.world.component_for_entity(p.holding, components.Size)
                        i.image = pygame.transform.rotate(i.image, -90)
                        tmp = s.width
                        s.width = s.height
                        s.height = tmp
                        self.world.add_component(p.holding, components.Velocity(0,0))
                        p.holding = None
                    
                    else:
                        rect = pygame.Rect(pos.x, pos.y - s.height * s.scale / 2, s.width * s.scale * (1 if p.facing_right else -1), s.height * s.scale)
                        rect.normalize()
                        for ent, (p2, i, s, v) in self.world.get_components(components.Position, components.Image, components.Size, components.Velocity):
                            if self.world.has_component(ent, components.Player):
                                continue
                            if rect.collidepoint(p2.x, p2.y):
                                p.holding = ent
                                if self.world.has_component(self.player, components.Image):
                                    self.world.remove_component(self.player, components.Image)
                                    self.world.add_component(self.player, p.carry_image)
                                elif self.world.has_component(self.player, components.Animation):
                                    self.world.remove_component(self.player, components.Animation)
                                    self.world.add_component(self.player, p.carry_animation)
                                if self.world.has_component(ent, components.RotationalVelocity):
                                    r = self.world.component_for_entity(ent, components.RotationalVelocity)
                                    i.image = r.image
                                    s.width = r.width
                                    s.height = r.height
                                    self.world.remove_component(ent, components.RotationalVelocity)
                                i.image = pygame.transform.rotate(i.image, 90)
                                tmp = s.width
                                s.width = s.height
                                s.height = tmp
                                self.world.remove_component(ent, components.Velocity)
                                if self.world.has_component(ent, components.Audio):
                                    self.world.component_for_entity(ent, components.Audio).sound.play()
                                break
            elif event.type == pygame.MOUSEBUTTONDOWN and p.holding:
                if self.world.has_component(self.player, components.Image):
                    self.world.remove_component(self.player, components.Image)
                    self.world.add_component(self.player, p.image)
                elif self.world.has_component(self.player, components.Animation):
                    self.world.remove_component(self.player, components.Animation)
                    self.world.add_component(self.player, p.animation)
                i = self.world.component_for_entity(p.holding, components.Image)
                s = self.world.component_for_entity(p.holding, components.Size)
                i.image = pygame.transform.rotate(i.image, -90)
                tmp = s.width
                s.width = s.height
                s.height = tmp
                x = event.pos[1] * 1280 / pygame.display.get_surface().get_width()
                y = event.pos[0] * 720 / pygame.display.get_surface().get_height()
                angle = math.atan2(x - pos.y, y - pos.x) % (2 * math.pi)
                self.world.add_component(p.holding, components.Velocity(math.cos(angle)*16 * self.vitality, math.sin(angle)*12 * self.vitality))
                self.world.add_component(p.holding, components.RotationalVelocity(320))
                p.holding = None
                p.throw.sound.play()
            elif event.type == pygame.MOUSEBUTTONDOWN and p.holdingfireball == True:
                
                v = self.world.component_for_entity(self.fireball, components.Velocity)
                
                while not v.x == 800:
                    v.x = v.x + 1
                    v = self.world.component_for_entity(self.fireball, components.Velocity)

        if p.holding:
            p3 = self.world.component_for_entity(p.holding, components.Position)
            p3.x = pos.x
            p3.y = pos.y - s.height + 10

        def BossBattleFireballLoop():
            while True:
                if fireball:
                    return fireball
            


# Sam's LAZER PROCESSOR
class LaserProcessor(esper.Processor):
    def __init__(self, player, vitality):
        esper.Processor.__init__(self)
        self.player = player
        self.vitality = vitality
        self.MessageShown = False
        self.player_is_facing_right = True
    def process(self, filtered_events, pressed_keys, dt, screen):
        v = self.world.component_for_entity(self.player, components.Velocity)
        p = self.world.component_for_entity(self.player, components.Player)
        s = self.world.component_for_entity(self.player, components.Size)
        pos = self.world.component_for_entity(self.player, components.Position)
        v.x = 0
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            v.x -= 3 * self.vitality
            self.player_is_facing_right = False
            self.player_is_facing_left = True
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            v.x += 3 * self.vitality
            self.player_is_facing_right = True

        
        p.holdingfireball = False
            
            
        if (p.facing_right and v.x < 0) or (not p.facing_right and v.x > 0):
            p.facing_right = not p.facing_right
            self.player_is_facing_right = False
            p.image.image = pygame.transform.flip(p.image.image, True, False)
            p.animation.image = pygame.transform.flip(p.animation.image, True, False)
            p.carry_image.image = pygame.transform.flip(p.carry_image.image, True, False)
            p.carry_animation.image = pygame.transform.flip(p.carry_animation.image, True, False)
        if v.x == 0 and self.world.has_component(self.player, components.Animation):
            self.world.remove_component(self.player, components.Animation)
            if p.holding:
                self.world.add_component(self.player, p.carry_image)
            else:
                self.world.add_component(self.player, p.image)
        elif v.x != 0 and self.world.has_component(self.player, components.Image):
            self.world.remove_component(self.player, components.Image)
            if p.holding:
                self.world.add_component(self.player, p.carry_animation)
            else:
                self.world.add_component(self.player, p.animation)
        for event in filtered_events:
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_SPACE) and v.y == 0:
                    v.y -= 6 * self.vitality
                    p.jump.sound.play()
                elif event.key == pygame.K_l:
                    if self.MessageShown == False:
                        game.LaserMessage(self.world)
                        self.MessageShown = True
                        
                    global laser
                    self.laser = game.CreateLaser(self.world,pos.x,pos.y)
                    self.world.add_component(self.laser, components.Position(pos.x,pos.y))
                    self.world.add_component(self.laser, components.Velocity())
                    self.world.add_component(self.laser, components.Flammable(True))
                    v = self.world.component_for_entity(self.laser, components.Velocity)
                    mouseX,mouseY = pygame.mouse.get_pos()
                    """
                    mousething = np.array([mouseX,mouseY])
                    cornor = np.array([pos.x,pos.y])
                    double = np.array([mouseX-pos.x,mouseY-pos.y])
                    a = np.linalg.norm(double)
                    b = double / a
                    self.world.remove_component(self.laser, components.Velocity)
                    v = self.world.add_component(self.laser, components.Velocity(b[0],b[1]))
                    """
                    if self.player_is_facing_right == True:
                        while not v.x > 1300:
                            v.x += 3
                            
                    elif self.player_is_facing_right == False:
                        while not v.x == 0:
                            v.x -= 3
                            
                    
                    
                    
                            
                        
                        
                        
                        
                elif event.key == pygame.K_e:
                    if p.holding:
                        if self.world.has_component(self.player, components.Image):
                            self.world.remove_component(self.player, components.Image)
                            self.world.add_component(self.player, p.image)
                        elif self.world.has_component(self.player, components.Animation):
                            self.world.remove_component(self.player, components.Animation)
                            self.world.add_component(self.player, p.animation)
                        i = self.world.component_for_entity(p.holding, components.Image)
                        s = self.world.component_for_entity(p.holding, components.Size)
                        i.image = pygame.transform.rotate(i.image, -90)
                        tmp = s.width
                        s.width = s.height
                        s.height = tmp
                        self.world.add_component(p.holding, components.Velocity(0,0))
                        p.holding = None
                    
                    else:
                        rect = pygame.Rect(pos.x, pos.y - s.height * s.scale / 2, s.width * s.scale * (1 if p.facing_right else -1), s.height * s.scale)
                        rect.normalize()
                        for ent, (p2, i, s, v) in self.world.get_components(components.Position, components.Image, components.Size, components.Velocity):
                            if self.world.has_component(ent, components.Player):
                                continue
                            if rect.collidepoint(p2.x, p2.y):
                                p.holding = ent
                                if self.world.has_component(self.player, components.Image):
                                    self.world.remove_component(self.player, components.Image)
                                    self.world.add_component(self.player, p.carry_image)
                                elif self.world.has_component(self.player, components.Animation):
                                    self.world.remove_component(self.player, components.Animation)
                                    self.world.add_component(self.player, p.carry_animation)
                                if self.world.has_component(ent, components.RotationalVelocity):
                                    r = self.world.component_for_entity(ent, components.RotationalVelocity)
                                    i.image = r.image
                                    s.width = r.width
                                    s.height = r.height
                                    self.world.remove_component(ent, components.RotationalVelocity)
                                i.image = pygame.transform.rotate(i.image, 90)
                                tmp = s.width
                                s.width = s.height
                                s.height = tmp
                                self.world.remove_component(ent, components.Velocity)
                                if self.world.has_component(ent, components.Audio):
                                    self.world.component_for_entity(ent, components.Audio).sound.play()
                                break
            elif event.type == pygame.MOUSEBUTTONDOWN and p.holding:
                if self.world.has_component(self.player, components.Image):
                    self.world.remove_component(self.player, components.Image)
                    self.world.add_component(self.player, p.image)
                elif self.world.has_component(self.player, components.Animation):
                    self.world.remove_component(self.player, components.Animation)
                    self.world.add_component(self.player, p.animation)
                i = self.world.component_for_entity(p.holding, components.Image)
                s = self.world.component_for_entity(p.holding, components.Size)
                i.image = pygame.transform.rotate(i.image, -90)
                tmp = s.width
                s.width = s.height
                s.height = tmp
                x = event.pos[1] * 1280 / pygame.display.get_surface().get_width()
                y = event.pos[0] * 720 / pygame.display.get_surface().get_height()
                angle = math.atan2(x - pos.y, y - pos.x) % (2 * math.pi)
                self.world.add_component(p.holding, components.Velocity(math.cos(angle)*16 * self.vitality, math.sin(angle)*12 * self.vitality))
                self.world.add_component(p.holding, components.RotationalVelocity(320))
                p.holding = None
                p.throw.sound.play()
            elif event.type == pygame.MOUSEBUTTONDOWN and p.holdingfireball == True:
                
                v = self.world.component_for_entity(self.laser, components.Velocity)
                
                while not v.x == 800:
                    v.x = v.x + 1
                    v = self.world.component_for_entity(self.laser, components.Velocity)

        if p.holding:
            p3 = self.world.component_for_entity(p.holding, components.Position)
            p3.x = pos.x
            p3.y = pos.y - s.height + 10


