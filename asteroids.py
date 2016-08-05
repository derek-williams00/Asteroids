import random
import math

import pygame
from pygame.locals import *


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Game:
    display_size = (600, 600)
    caption = 'Asteriods'
    
    def __init__(self):
        self.exit = False
        pygame.init()
        self.display = pygame.display.set_mode(self.display_size)
        pygame.display.set_caption(self.caption)
        self.clock = pygame.time.Clock()
        self.fps = 30
        self.player = Rocket((300, 300))
        self.entities = [self.player]
        self.keys_down = []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.exit = True
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    self.keys_down.append(K_UP)
                if event.key == K_LEFT:
                    self.keys_down.append(K_LEFT)
                if event.key == K_RIGHT:
                    self.keys_down.append(K_RIGHT)
                if event.key == K_DOWN:
                    self.keys_down.append(K_DOWN)
                if event.key == K_SPACE:
                    self.player.shoot(self.entities)
            if event.type == KEYUP:
                if event.key == K_UP:
                    try:
                        self.keys_down.remove(K_UP)
                    except ValueError:
                        pass
                if event.key == K_LEFT:
                    try:
                        self.keys_down.remove(K_LEFT)
                    except ValueError:
                        pass
                if event.key == K_RIGHT:
                    try:
                        self.keys_down.remove(K_RIGHT)
                    except ValueError:
                        pass
                if event.key == K_DOWN:
                    try:
                        self.keys_down.remove(K_DOWN)
                    except ValueError:
                        pass

    def handle_pressed_keys(self):
        if K_UP in self.keys_down:
            self.player.accelerate()
        if K_LEFT in self.keys_down:
            self.player.rotate_left()
        if K_RIGHT in self.keys_down:
            self.player.rotate_right()
        if K_DOWN in self.keys_down:
            self.player.decelerate()

    def handle_despawn_bullets(self):
        dead_bullets = list()
        for entity in self.entities:
            if type(entity) == Bullet:
                if entity.life <= 0:
                    dead_bullets.append(entity)
                else:
                    entity.life -= 1
        for bullet in dead_bullets:
            try:
                self.entities.remove(bullet)
            except ValueError:
                pass

    def move_entities(self):
        #print(self.entities)
        for entity in self.entities:
            entity.move()
            entity.handle_surface_wrapping(self.display_size)

    def draw(self):
        self.display.fill(BLACK)
        for entity in self.entities:
            entity.draw(self.display)
        pygame.display.update()        
    
    def loop(self):
        while not self.exit:
            self.handle_events()
            self.handle_pressed_keys()
            self.move_entities()
            self.handle_despawn_bullets()
            self.draw()
            self.clock.tick(self.fps)


class Entity:
    def __init__(self, pos):
        self.direction = 0
        self.speed = 1
        self.pos = tuple(pos)

    def get_inverse_direction(self):
        inv_direc = self.direction - 180
        if inv_direc < 0:
            inv_direc += 360
        return inv_direc
    
    def get_next_pos(self):
        direction = 360 - self.direction
        run = int(self.speed*math.cos(math.radians(direction)))
        rise = int(self.speed*math.sin(math.radians(direction)))
        next_pos = [self.pos[0]+run, self.pos[1]+rise]
        return tuple(next_pos)

    def move(self):
        self.pos = self.get_next_pos()

    def handle_surface_wrapping(self, display_size):
        pos = list(self.pos)
        if pos[0] > display_size[0]:
            pos[0] -= display_size[0]
        elif pos[0] < 0:
            pos[0] += display_size[0]
        if pos[1] > display_size[1]:
            pos[1] -= display_size[1]
        elif pos[1] < 0:
            pos[1] += display_size[1]
        self.pos = tuple(pos)

    def draw(self, surface):
        pass
        

class Asteroid(Entity):
    def __init__(self, room_size):
        room_width = room_size[0]
        room_height = room_size[1]
        self.pos = (random.randint(0, room_width), random.randint(0, room_height))


class LargeAsteroid(Asteroid):
    def break_down(self, entity_list):
        entity_list.remove(self)
        for i in range(0, random.randint(1, 4)):
            entity_list.append(MediumAsteroid(self.pos))


class MediumAsteroid(Asteroid):
    def break_down(self, entity_list):
        entity_list.remove(self)
        for i in range(0, random.randint(1, 4)):
            entity_list.append(SmallAsteroid(self.pos))


class SmallAsteroid(Asteroid):
    def break_down(self, entity_list):
        for i in range(0, random.randint(1, 4)):
            entity_list.remove(self)
            

class Rocket(Entity):
    height = 32
    width = 16
    max_speed = 8
    min_speed = 1
    speed_change_rate = 1.05
    line_width = 4
    #turn_speed = 8
    points = ((-32, 8), (0, 0), (-32, -8))
    
    def is_hit(self):
        pass
    
    def accelerate(self):
        self.speed = min(self.max_speed, self.speed_change_rate*self.speed)

    def rotate_left(self):
        direction = self.direction + self.speed
        if direction >= 360:
            direction -= 360
        self.direction = direction

    def rotate_right(self):
        direction = self.direction - self.speed
        if direction < 0:
            direction += 360
        self.direction = direction
    
    def decelerate(self):
        self.speed = max(self.min_speed, self.speed/self.speed_change_rate)

    def get_points(self):
        direction = math.radians(360-self.direction)
        points = list()
        for point in self.points:
            x = point[0]
            y = point[1]
            new_x = (x*math.cos(direction)) - (y*math.sin(direction))
            new_y = (x*math.sin(direction)) + (y*math.cos(direction))
            new_point = (new_x+self.pos[0], new_y+self.pos[1])
            points.append(new_point)
        return tuple(points)

    def shoot(self, entity_list):
        entity_list.append(Bullet(self))

    def draw(self, surface):
        pygame.draw.polygon(surface, WHITE, self.get_points(), self.line_width)


class Bullet(Entity):
    radius = 3

    def __init__(self, owner):
        self.life = 32
        self.speed = 16
        self.direction = owner.direction
        self.pos = owner.pos
        self.owner = owner
    
    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, self.pos, self.radius, 2)


if __name__ == '__main__':
    game = Game()
    game.loop()
    pygame.quit()
    quit()