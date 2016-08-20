import math
import random

import pygame
from pygame.locals import *


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def distance(point1, point2):
    return math.sqrt((point2[0]-point1[0])**2 + (point2[1]-point1[1])**2)


class Game:
    display_size = (1024, 768)
    difficulty = 4
    caption = 'Asteriods'
    
    def __init__(self):
        self.exit = False
        self.over = False
        self.score = 0
        self.lives = 3
        pygame.init()
        self.score_font_size = 24
        self.score_font = pygame.font.Font(None, self.score_font_size)
        self.display = pygame.display.set_mode(self.display_size, RESIZABLE)
        pygame.display.set_caption(self.caption)
        self.clock = pygame.time.Clock()
        self.fps = 30
        self.player = Rocket((300, 300))
        self.entities = [self.player]
        self.wave = 0
        self.keys_down = []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.exit = True
            if event.type == VIDEORESIZE:
                self.display_size = event.dict['size']
                self.display = pygame.display.set_mode(self.display_size, RESIZABLE)
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

    def handle_asteroid_breakdown(self):
        bullets = self.get_bullets()
        asteroids = self.get_asteroids()
        for asteroid in asteroids:
            for bullet in bullets:
                if distance(bullet.pos, asteroid.pos) < asteroid.radius + bullet.radius:
                    asteroid.break_down(self.entities)
                    self.score += 100
                    try:
                        self.entities.remove(bullet)
                    except ValueError:
                        pass

    def handle_asteroid_rocket_collision(self):
        for point in self.player.get_points():
            for asteroid in self.get_asteroids():
                if distance(point, asteroid.pos) < asteroid.radius:
                    asteroid.break_down(self.entities)
                    self.rocket_death()

    def draw_score(self):
        score_display_margin = 4
        pos = list(self.display_size)
        score_char_len = len(str(self.score))
        score_display_width = score_char_len * self.score_font_size
        score_display_height = self.score_font_size
        pos[0] -= (score_display_width + score_display_margin)
        pos[1] = score_display_margin
        score_text_surface = self.score_font.render(str(self.score), False, WHITE)
        self.display.blit(score_text_surface, pos)

    def rocket_death(self):
        if self.lives < 1:
            self.over = True
        else:
            self.lives -= 1
            self.player.respawn(self.display_size)
        
    def move_entities(self):
        #print(self.entities)
        for entity in self.entities:
            entity.move()
            entity.handle_surface_wrapping(self.display_size)

    def get_asteroids(self):
        asteroids = list()
        for entity in self.entities:
            if isinstance(entity, Asteroid):
                asteroids.append(entity)
        return asteroids

    def get_bullets(self):
        bullets = list()
        for entity in self.entities:
            if isinstance(entity, Bullet):
                bullets.append(entity)
        return bullets

    def handle_spawn_asteroids(self):
        if len(self.get_asteroids()) == 0:
            self.wave += 1
            self.lives += 1
            #print(self.wave)
            for num in range(0, self.wave*self.difficulty):
                self.entities.append(LargeAsteroid(self.display_size))

    def handle_lives(self):
        symbol_pos = [8, 8]
        symbol_margin = 4
        def is_not_lifesymbol(item):
            if isinstance(item, LifeSymbol):
                return False
            else:
                return True
        self.entities = list(filter(is_not_lifesymbol, self.entities))
        lives = self.lives
        while lives:
            new_symbol = LifeSymbol(symbol_pos)
            self.entities.append(new_symbol)
            symbol_pos[0] += new_symbol.width
            symbol_pos[0] += symbol_margin
            lives -= 1

    def handle_game_over(self):
        if self.over:
            self.exit = True

    def draw(self):
        self.display.fill(BLACK)
        self.draw_score()
        for entity in self.entities:
            entity.draw(self.display)
        pygame.display.update()        
    
    def loop(self):
        while not self.exit:
            self.handle_events()
            self.handle_pressed_keys()
            self.handle_spawn_asteroids()
            self.handle_asteroid_breakdown()
            self.handle_asteroid_rocket_collision()
            self.handle_game_over()
            self.move_entities()
            self.handle_despawn_bullets()
            self.handle_lives()
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
    radius = 0
    line_width = 6
    min_speed = 1
    max_speed = 6
    
    def __init__(self, room_size):
        room_width = room_size[0]
        room_height = room_size[1]
        self.direction = random.randint(0, 359)
        self.speed = random.randint(self.min_speed, self.max_speed)
        self.pos = (random.randint(0, room_width), random.randint(0, room_height))

    def break_down(self):
        pass
    
    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, self.pos, self.radius, self.line_width)


class LargeAsteroid(Asteroid):
    radius = 64

    def break_down(self, entity_list):
        try:
            entity_list.remove(self)
        except ValueError:
            pass
        for i in range(0, random.randint(1, 4)):
            fragment = MediumAsteroid((0, 0))
            fragment.pos = self.pos
            entity_list.append(fragment)


class MediumAsteroid(Asteroid):
    radius = 32

    def break_down(self, entity_list):
        entity_list.remove(self)
        for i in range(0, random.randint(1, 4)):
            fragment = SmallAsteroid((0, 0))
            fragment.pos = self.pos
            entity_list.append(fragment)


class SmallAsteroid(Asteroid):
    radius = 16
    
    def break_down(self, entity_list):
        entity_list.remove(self)
            

class Rocket(Entity):
    height = 32
    width = 16
    max_speed = 8
    min_speed = 1
    turn_speed = 4
    speed_change_rate = 1.05
    line_width = 4
    points = ((-32, 8), (0, 0), (-32, -8))
    
    def respawn(self, surface_size):
        self.pos = (int(surface_size[0]/2), int(surface_size[1]/2))
    
    def accelerate(self):
        self.speed = min(self.max_speed, self.speed_change_rate*self.speed)

    def rotate_left(self):
        direction = self.direction + self.turn_speed
        if direction >= 360:
            direction -= 360
        self.direction = direction

    def rotate_right(self):
        direction = self.direction - self.turn_speed
        if direction < 0:
            direction += 360
        self.direction = direction
    
    def decelerate(self):
        self.speed = max(self.min_speed, self.speed/self.speed_change_rate)
        #print(self.speed)

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


class LifeSymbol(Rocket):
    height = 16
    width = 8
    max_speed = 0
    min_speed = 0
    turn_speed = 0
    speed_change_rate = 1
    line_width = 2
    points = ((4, 16), (0, 0), (-4, 16))

class Bullet(Entity):
    radius = 3

    def __init__(self, owner):
        self.life = 32
        self.speed = 32
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
