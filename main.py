import sys
import math
import pygame
# from moviepy.editor import VideoFileClip # library to add video in proj
import random as rd
import PIL
from PIL import Image
import threading
import time

window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
info_object = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info_object.current_w, info_object.current_h
constx = SCREEN_WIDTH / 1366
consty = SCREEN_HEIGHT / 768

# Add intro in game
# pygame.display.set_caption('Intro')
# intro = VideoFileClip('assets/videos/intro.mp4')
# intro.preview()

pygame.init()
shoot_sound = pygame.mixer.Sound('assets/sounds/shoot3.ogg')
shoot_sound.set_volume(0.1)

damage_sound = []
for snd in ['assets/sounds/damage1.ogg', 'assets/sounds/damage2.ogg']:
    damage_sound.append(pygame.mixer.Sound(snd))

rev_sound = pygame.mixer.Sound('assets/sounds/rev.ogg')
rev_sound.set_volume(1.5)

collision_sound = pygame.mixer.Sound('assets/sounds/collision.ogg')

buulet_to_brick_sound = pygame.mixer.Sound('assets/sounds/bullet_to_brick.ogg')

notshoot_sound = pygame.mixer.Sound('assets/sounds/notshoot.ogg')
reload_sound = pygame.mixer.Sound('assets/sounds/reload.ogg')


from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_w,
    K_a,
    K_s,
    K_d,
    KEYDOWN,
    QUIT,
    K_SPACE,
    K_m,
    K_n,
    K_r,
)

class Menu:
    def __init__(self):
        self.punkts = [
            (1000*constx, 520*consty, u'Играть', (250, 97, 3), (255, 165, 0), 0),
            (1000*constx, 610*consty, u'Выбор персонажа', (250, 97, 3), (255, 165, 0), 1),
            (1000*constx, 700*consty, u'Выйти', (250, 97, 3), (255, 165, 0),  2)
        ]

    def render(self, screen, font, num_punkt):
        for i in self.punkts:
            if num_punkt == i[5]:
                screen.blit(font.render(i[2], 2, i[4]), (i[0], i[1]))
            else:
                screen.blit(font.render(i[2], 2, i[3]), (i[0], i[1]))

    def menu(self):
        done = True
        self.menu_back = pygame.image.load('assets/images/background1.png')
        img = Image.open( 'assets/images/background1.png')
        img = img.resize((SCREEN_WIDTH, SCREEN_HEIGHT), PIL.Image.ANTIALIAS)
        img.save('assets/images/backgroundResize.png')
        self.menu_back = pygame.image.load('assets/images/backgroundResize.png')

        pygame.init()
        pygame.mixer.music.load('assets/music/menu.mp3')
        pygame.mixer.music.play(loops=-1)

        font_menu = pygame.font.Font(None, 50)
        pygame.key.set_repeat(0,0)
        pygame.mouse.set_visible(True)
        punkt = None
        while done:
            screen.blit(self.menu_back, (0, 0))
            mp = pygame.mouse.get_pos()
            self.render(screen, font_menu, punkt)
            
            for i in self.punkts:
                if mp[0]>=i[0] and mp[0]<i[0]+130 and mp[1]>=i[1]-180*consty and mp[1]<i[1]-155*consty:
                    punkt = 0
                elif  mp[0]>=i[0] and mp[0]<i[0]+330 and mp[1]>=i[1]-83*consty and mp[1]<i[1]-70*consty:
                    punkt = 1  
                elif mp[0]>=i[0] and mp[0]<i[0]+110 and mp[1]>=i[1] and mp[1]<i[1]+100*consty:
                    punkt = 2   
                else :
                    punkt = None
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                       sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 :
                         if punkt == 0:
                             self.game = Game()
                             self.game.main()  
                         elif punkt == 2:
                               exit()
     
            pygame.display.flip()

class Mob(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        super(Mob, self).__init__()
        self.game = game
        self.surf = pygame.image.load("assets/images/mob2.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(center = (x, y))
        pygame.mixer.Channel(2).play(rev_sound, -1)
        
    def update(self):
        temp_x = rd.randint(-5, 5)
        temp_y = rd.randint(-5, 5)
        self.rect.move_ip(0, temp_x)
        self.rect.move_ip(temp_y, 0)
        if pygame.sprite.spritecollideany(self, self.game.bricks):
            self.rect.move_ip(0, -temp_x)
            self.rect.move_ip(-temp_y, 0)
        if pygame.sprite.spritecollideany(self.game.player, self.game.mobs):#spritecollide(self, self.game.player, 0):
            self.rect.move_ip(0, -temp_x)
            self.rect.move_ip(-temp_y, 0)
            self.game.player.rect.move_ip(0, 50)
            self.game.player.rect.move_ip(50, 0)
            self.game.player.health -= 1
            pygame.mixer.Channel(1).play(collision_sound)
            print("player mob collision") 
            
        # Keep mobs on the screen
        elif self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > self.game.SCREEN_WIDTH:
            self.rect.right = self.game.SCREEN_WIDTH
        elif self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= self.game.SCREEN_HEIGHT:
            self.rect.bottom = self.game.SCREEN_HEIGHT
          

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, x1, y1,game):
        super(Bullet, self).__init__()
        self.bullet_img = pygame.image.load('assets/images/arrow.png')
        self.bullet_img.set_colorkey((255, 255, 255), RLEACCEL)
        self.game = game
        self.x = x  
        self.y = y  
        self.speed = 8
        self.speed_x1 = x1
        self.speed_y1 = y1
        self.rect = self.bullet_img.get_rect(center = (x, y))
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                    self.m_x, self.m_y = event.pos
                    l = math.sqrt((self.m_x - self.x)**2 + (self.m_y - self.y)**2)
                    if l > 0:
                        self.speed_x1 = (self.m_x - self.x) / l
                        self.speed_y1 = (self.m_y - self.y) / l

    def update(self):   
        self.x += self.speed * self.speed_x1
        self.y += self.speed * self.speed_y1
        self.rect.move_ip(0, self.speed_y1*self.speed)
        self.rect.move_ip(self.speed_x1*self.speed,0)   
        if pygame.sprite.spritecollideany(self, self.game.bricks):  
            self.kill()    
            pygame.mixer.Channel(3).play(buulet_to_brick_sound) 
        if pygame.sprite.groupcollide(self.game.mobs, self.game.bullets, True, True):
           pygame.mixer.Channel(1).play(rd.choice(damage_sound))
           self.kill()              
           print("bullet killed mob")            


# Define a player object by extending pygame.sprite.Sprite
# The surface drawn on the screen is now an attribute of 'player'
class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super(Player, self).__init__()
        self.game = game # reference to Game object in which player is playing
        #self.surf = pygame.Surface((75, 75))
        self.orig_img = pygame.image.load("assets/images/player2.png")
        self.surf = pygame.image.load("assets/images/player2.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        # create rect from surface and set initial coords
        self.rect = self.surf.get_rect(center = (self.game.SCREEN_WIDTH / 2, (self.game.SCREEN_HEIGHT / 2)+20))
        self.dir_x = 0
        self.dir_y = 1
        self.health = 3
        self.bullets_num = 15
        self.state = 'WAIT'
    # Move the sprite based on user keypresses
    def update(self, pressed_keys):
        if pressed_keys[K_UP] or pressed_keys[K_w]:
            self.rect.move_ip(0, -5)
            if pygame.sprite.spritecollideany(self, self.game.bricks):
                self.rect.move_ip(0, 5)
            if pygame.sprite.spritecollideany(self, self.game.mobs):
                print("He's crashed")
                self.rect.move_ip(0, 100)
                self.health -= 1
                pygame.mixer.Channel(1).play(collision_sound)
        if pressed_keys[K_DOWN] or pressed_keys[K_s]:
            self.rect.move_ip(0, 5)
            if pygame.sprite.spritecollideany(self, self.game.bricks):
                self.rect.move_ip(0, -5)
            if pygame.sprite.spritecollideany(self, self.game.mobs):
                print("He's crashed")
                self.rect.move_ip(0, -100)
                self.health -= 1
                pygame.mixer.Channel(1).play(collision_sound)
        if pressed_keys[K_LEFT] or pressed_keys[K_a]:
            self.rect.move_ip(-5, 0)
            if pygame.sprite.spritecollideany(self, self.game.bricks):
                self.rect.move_ip(5, 0)
            if pygame.sprite.spritecollideany(self, self.game.mobs):
                print("Game over! He's crashed")
                self.rect.move_ip(100, 0)
                self.health -= 1
                pygame.mixer.Channel(1).play(collision_sound)
        if pressed_keys[K_RIGHT] or pressed_keys[K_d]:
            self.rect.move_ip(5, 0)
            if pygame.sprite.spritecollideany(self, self.game.bricks):
                self.rect.move_ip(-5, 0)
            if pygame.sprite.spritecollideany(self, self.game.mobs):
                print("Game over! He's crashed")
                self.rect.move_ip(-100, 0)
                self.health -= 1
                pygame.mixer.Channel(1).play(collision_sound)
        if pygame.sprite.groupcollide(self.game.mobs, self.game.bullets, True, True):
           pygame.mixer.Channel(1).play(rd.choice(damage_sound))
           self.kill()              
           print("bullet killed mob")
        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.game.SCREEN_WIDTH:
            self.rect.right = self.game.SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= self.game.SCREEN_HEIGHT:
            self.rect.bottom = self.game.SCREEN_HEIGHT

    def point_at(self, x, y):
        direction = pygame.math.Vector2(x, y) - self.rect.center
        angle = direction.angle_to((1, 0))
        self.surf = pygame.transform.rotate(self.orig_img, angle)
        self.rect = self.surf.get_rect(center=self.rect.center)
    
    def shoot(self):
            if self.state == 'RELOADING':
                return
            if self.bullets_num >= 1:
                self.bullets_num -= 1
                bullet = Bullet(self.rect.x+15,self.rect.y+15,self.dir_x,self.dir_y,self.game)
                self.game.bullets.add(bullet)
                pygame.mixer.Channel(0).play(shoot_sound)
            else:
                pygame.mixer.Channel(0).play(notshoot_sound)

    def reload(self):

        def reload_bullets(self):
            for _ in range(15):
                if self.bullets_num == 15:
                    break
                self.bullets_num = min(15, self.bullets_num + 5)
                time.sleep(1)
            self.state = 'WAIT'

        x = threading.Thread(target=reload_bullets, args=(self,))

        if self.state == 'WAIT':
            self.state = 'RELOADING'
            x.start()
            

class Map():
    def __init__(self):
        self.rows = None
        self.cols = None
        self.path = None
        self.matrix = None
        self.cell_size = 72

    def load_from(self, filepath = 'assets/maps/map2.txt'):
        self.path = filepath
        f = open(filepath)
        self.matrix = f.read().split('\n')
        self.rows = len(self.matrix)
        self.cols = len(self.matrix[0])

    def cell(self, row, col):
        return self.matrix[row][col]        


class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Brick, self).__init__()
        self.surf = pygame.image.load("assets/images/brick1.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(topleft = (x, y))

class TerrainBlock(pygame.sprite.Sprite):
    def __init__(self, x, y, block_type = 1):
        super(TerrainBlock, self).__init__()
        self.surf = pygame.image.load("assets/images/gross.png" if block_type == 1 else "assets/images/terrain2.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(topleft = (x, y))

class House(pygame.sprite.Sprite):
    def __init__(self, x, y, block_type):
        super(House, self).__init__()
        for i in range(0,10):
            if block_type == str(i):
                st = "assets/images/house/house" + str(i) + ".png"
                self.surf = pygame.image.load(st)
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(topleft = (x, y))

class Tree(pygame.sprite.Sprite):
    def __init__(self, x, y, block_type):
        super(Tree, self).__init__()
        if block_type == 'T':
            self.surf = pygame.image.load("assets/images/tree/tree1.png") 
        elif block_type == 'O':
            self.surf = pygame.image.load("assets/images/tree/tree2.png") 
        elif block_type == 'X':
            self.surf = pygame.image.load("assets/images/tree/tree3.png") 
        elif block_type == 'A':
            self.surf = pygame.image.load("assets/images/tree/tree4.png")             
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(topleft = (x, y))        

class Water(pygame.sprite.Sprite):
    def __init__(self, x, y, block_type):
        super(Water, self).__init__()
        if block_type == 'W':
            self.surf = pygame.image.load("assets/images/water/water3.png") 
        elif block_type == 'H':
            self.surf = pygame.image.load("assets/images/water/water4.png")           
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(topleft = (x, y)) 

class Game():
    def __init__(self):
        surface = pygame.display.get_surface()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = size = surface.get_width(), surface.get_height()
        self.FPS = 60
        self.map = Map()
        self.map.load_from('assets/maps/map2.txt')
        self.mapSpawn = Map()
        self.mapSpawn.load_from('assets/maps/spawnMobMap2.txt')
        self.running = False
        
        pygame.init()

        #info_object = pygame.display.Info()
        #self.SCREEN_WIDTH, self.SCREEN_HEIGHT = info_object.current_w, info_object.current_h
        
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT)) #, flags = pygame.FULLSCREEN )
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)
         # Create a player - Sprite
        self.player = Player(self)
         # Create a set of mobs - Sprite
        self.mobs = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.bricks = pygame.sprite.Group()
        self.terrain_blocks = pygame.sprite.Group()
        #self.all_sprites = pygame.sprite.Group()
        #self.all_sprites.add(self.player)

    def draw_map(self):
        for i in range(self.map.rows):
            for j in range(self.map.cols):
                cell = self.map.cell(i, j)
                if cell == '#':
                    new_brick = Brick(j*self.map.cell_size, i*self.map.cell_size)
                    self.bricks.add(new_brick)
                elif cell == '.':
                    new_terrain_block = TerrainBlock(j*self.map.cell_size, i*self.map.cell_size)
                    self.terrain_blocks.add(new_terrain_block)
                elif cell == '1':
                    house1 = House(j*self.map.cell_size, i*self.map.cell_size, cell)
                    self.bricks.add(house1)
                elif cell == '2':
                    house2 = House(j*self.map.cell_size, i*self.map.cell_size, cell)
                    self.bricks.add(house2)    
                elif cell == '3':
                    house3 = House(j*self.map.cell_size, i*self.map.cell_size, cell)
                    self.bricks.add(house3)             
                elif cell == '4':
                    house4 = House(j*self.map.cell_size, i*self.map.cell_size, cell)
                    self.bricks.add(house4)                 
                elif cell == '5':
                    house5 = House(j*self.map.cell_size, i*self.map.cell_size, cell)
                    self.bricks.add(house5)  
                elif cell == '6':
                    house6 = House(j*self.map.cell_size, i*self.map.cell_size, cell)
                    self.bricks.add(house6)  
                elif cell == '7':
                    most1 = House(j*self.map.cell_size, i*self.map.cell_size, cell)
                    self.terrain_blocks.add(most1)  
                elif cell == '8':
                    most2 = House(j*self.map.cell_size, i*self.map.cell_size, cell)
                    self.terrain_blocks.add(most2)     
                elif cell == '9':
                    most3 = House(j*self.map.cell_size, i*self.map.cell_size, cell)
                    self.terrain_blocks.add(most3)  
                elif cell == '0':
                    most4 = House(j*self.map.cell_size, i*self.map.cell_size, cell)
                    self.terrain_blocks.add(most4) 
                elif cell == 'T':
                    tree1 = Tree(j*self.map.cell_size, i*self.map.cell_size, cell)
                    self.bricks.add(tree1) 
                elif cell == 'O':
                    tree2 = Tree(j*self.map.cell_size, i*self.map.cell_size, cell)
                    self.bricks.add(tree2) 
                elif cell == 'A':
                    tree3 = Tree(j*self.map.cell_size, i*self.map.cell_size, cell)
                    self.bricks.add(tree3) 
                elif cell == 'X':
                    tree4 = Tree(j*self.map.cell_size, i*self.map.cell_size, cell)
                    self.bricks.add(tree4)   
                elif cell == 'W':
                    water1 = Water(j*self.map.cell_size, i*self.map.cell_size, cell)
                    self.bricks.add(water1) 
                elif cell == 'H':
                    water2 = Water(j*self.map.cell_size, i*self.map.cell_size, cell)
                    self.bricks.add(water2)                                     
                else:
                    print('map error: incorrect cell type')
    
    def draw_spawnMobMap(self):
        for i in range(self.mapSpawn.rows):
            for j in range(self.mapSpawn.cols):
                cell = self.mapSpawn.cell(i, j)
                if cell == '@':
                    new_mob = Mob(j*self.mapSpawn.cell_size, i*self.mapSpawn.cell_size, self)
                    self.mobs.add(new_mob)
                    #self.all_sprites.add(new_mob)
                    

    def main(self):
        pygame.mixer.music.load('assets/music/2_level.mp3')
        pygame.mixer.music.play(loops=-1)
        self.running = True # flag that show is game running or not
        pygame.event.set_grab(True)

        self.draw_map()
        self.draw_spawnMobMap()
        while self.player.health > 0 and self.running: # this cicle defines health of our player
            self.clock.tick(self.FPS)  # delay according to fps

            for event in pygame.event.get(): # check events
                if event.type == pygame.KEYDOWN:         # when user hits some button
                    if event.key == pygame.K_ESCAPE:     # Esc -> quit
                        self.running = False  
                    elif event.key == pygame.K_m:     
                        pygame.mixer.music.pause() 
                    elif event.key == pygame.K_n:     
                        pygame.mixer.music.unpause()     
                    elif event.key == pygame.K_r:
                        if self.player.bullets_num <= 5:
                            pygame.mixer.Channel(0).play(reload_sound)
                            self.player.reload()

       
                elif event.type == pygame.MOUSEBUTTONDOWN:         
                    if event.button == 1:
                        self.player.shoot()
                elif event.type == pygame.MOUSEMOTION:
                    m_x, m_y = event.pos
                    l = math.sqrt((m_x - self.player.rect.x)**2 + (m_y - self.player.rect.y)**2)
                    if l > 0:
                        self.player.dir_x = (m_x - self.player.rect.x) / l
                        self.player.dir_y = (m_y - self.player.rect.y) / l
                elif event.type == pygame.QUIT:   # if user closes the widow -> quit
                    self.running = False

                #else:
                #    print(event.type, pygame.mouse.get_pos())

            # Get all the keys currently pressed
            pressed_keys = pygame.key.get_pressed()
            # Rotating sprite depending on mouse motion
            self.player.point_at(*pygame.mouse.get_pos())
            # Update the player sprite based on user keypresses
            self.player.update(pressed_keys)
            # Update mobs movement
            self.mobs.update()
            self.bullets.update()
            #self.screen.fill((0, 0, 0))
            
            for entity in self.terrain_blocks:
                self.screen.blit(entity.surf, entity.rect)

            for entity in self.bricks:
                self.screen.blit(entity.surf, entity.rect)
            # Draw mobs on the screen
            for entity in self.mobs:
                self.screen.blit(entity.surf, entity.rect)

            # Draw the player on the screen
            self.screen.blit(self.player.surf, self.player.rect)
            
            for entity in self.bullets:
                if entity.x <= SCREEN_WIDTH:
                    screen.blit(entity.bullet_img, (entity.x, entity.y))

            #pygame.draw.line(self.screen, (0, 30, 225), 
            #        [self.player.rect.x + 36, self.player.rect.y + 38], 
            #        [self.player.rect.x + 300*self.player.dir_x, self.player.rect.y + 300*self.player.dir_y], 2)

            # Draw fps ounter
            fps = self.font.render('FPS: ' + str(int(self.clock.get_fps())) + '   Health :  ' + str(self.player.health)  + '  Bullets : '+ str(self.player.bullets_num), True, pygame.Color('white'))
            self.screen.blit(fps, (50, 30))
            # Update the display
            pygame.display.flip()
        # check status of player's health 
        if self.player.health <= 0:
            self.screen.blit(self.font.render("Game over!", True, pygame.Color('white')), (self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2))
            print('0 hp - Game over!')
            self.running = False
            
        pygame.quit()
        sys.exit()

pygame.font.init()     

if __name__ == "__main__":
    menu = Menu()
    menu.menu()
