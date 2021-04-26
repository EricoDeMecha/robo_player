import pygame
import random
from pygame.locals import (K_LEFT, K_RIGHT, KEYDOWN, K_ESCAPE, QUIT)
import time

# initialize pygame
pygame.init()

# screen dimensions
screen_width = 800
screen_height = 640
screen = pygame.display.set_mode((screen_width, screen_height), pygame.SCALED, vsync=1)
brick_poss = list()
# player statuses
player_lives = 194


# game objects
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("assets/player.png")
        self.surf = pygame.transform.scale(self.surf, (50,50))
        #self.surf = pygame.Surface((70, 20))
        #self.surf.fill((255, 0, 255))
        self.rect = self.surf.get_rect(
            center=(
                int(screen_width / 2),
                screen_height - 20
            )
        )

    def update(self, pressed_keys):
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-8, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(8, 0)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super(Ball, self).__init__()
        self.surf = pygame.image.load("assets/ball_small.png")
        self.xpos = int(screen_width / 2)
        self.ypos = screen_height - 40
        self.rect = self.surf.get_rect(
            center=(
                self.xpos,
                self.ypos
            )
        )
        self.vel = [2, -2]

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]

        if (self.rect.x >= screen_width - 10) or self.rect.x <= 0:
            self.vel[0] = -self.vel[0]
        if self.rect.y < 0:
            self.vel[1] = -self.vel[1]
        if self.rect.y > screen_height:
            self.kill()
            global player_lives  # editing a global variable
            player_lives -= 10

    def bounce(self):
        self.vel[0] = -self.vel[0]
        self.vel[1] = self.vel[1]

    def bounceOffGround(self):
        self.vel[1] = -2  # alter the Y velocity


class Brick(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos):
        super(Brick, self).__init__()
        self.surf = pygame.Surface((70, 20))
        self.surf.fill((255, 51, 51))
        self.rect = self.surf.get_rect(
            center=(
                xpos,
                ypos
            )
        )


class Saviour(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos):
        super(Saviour, self).__init__()
        self.surf = pygame.Surface((70, 20))
        self.surf.fill((51, 255, 51))
        self.rect = self.surf.get_rect(
            center=(
                xpos,
                ypos
            )
        )


# game properties
lvl = 1  # level

player = Player()  # player instance
ball = Ball()  # Ball instance
# sprite groups
all_sprites = pygame.sprite.Group()
bricks = pygame.sprite.Group()
saviours = pygame.sprite.Group()
balls = pygame.sprite.Group()
players = pygame.sprite.Group()
# health of the player
player_life = pygame.image.load("assets/health.png")
player_lifeBar = pygame.image.load("assets/healthbar.png")
# score
score = 0


# generate brick positions
def brickPosGen(lev):
    counter = int(lev) * 10
    for i in range(counter):
        brick_poss.append((random.randint(5, screen_width - 5), random.randint(5, int((3 / 4) * screen_height))))


# load game data
def load():
    brickPosGen(lvl)  # level
    saviour_pos = [brick_poss[random.randint(0, int(len(brick_poss)) - 1)] for x in
                   range(lvl)]  # save the middle element as the saviour position
    # generate all the sprites
    balls.add(ball)
    players.add(player)
    all_sprites.add(player)
    all_sprites.add(ball)
    for tup_elem in brick_poss:
        if tup_elem in saviour_pos:
            _saviour = Saviour(tup_elem[0], tup_elem[1])
            saviours.add(_saviour)
            all_sprites.add(_saviour)
        else:
            _brick = Brick(tup_elem[0], tup_elem[1])
            bricks.add(_brick)
            all_sprites.add(_brick)


load()  # load once before  the game loop
# start of the game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False

    pressed_key = pygame.key.get_pressed()
    player.update(pressed_key)

    balls.update()

    screen.fill((51, 153, 255))  # screen's background color
    # rendering
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)
    # player's lives
    life_font = pygame.font.Font(None, 24)
    life_text = life_font.render(str("Lives: ").zfill(2), True, (0, 0, 0))
    life_text_rect = life_text.get_rect()
    screen.blit(life_text, life_text_rect)
    screen.blit(player_lifeBar, (50, 5))
    for life in range(player_lives):
        screen.blit(player_life, (life + 53, 8))
    # player_lives for running
    if player_lives < 5:
        running = False
    # score and level display
    score_font = pygame.font.Font(None, 24)
    score_text = score_font.render(str("Level: " + str(lvl) + "  " + "Score: " + str(score)).zfill(2), True, (0, 0, 0))
    score_text_rect = score_text.get_rect()
    score_text_rect.topright = [635, 5]
    screen.blit(score_text, score_text_rect)
    # collision detection
    for ball_sprite in balls:
        collided_sprite_bricks = pygame.sprite.spritecollideany(ball_sprite, bricks)
        if collided_sprite_bricks:
            score += 1
            ball_sprite.bounce()
            collided_sprite_bricks.kill()
        collided_sprite_saviour = pygame.sprite.spritecollideany(ball_sprite, saviours)
        if collided_sprite_saviour:
            collided_sprite_saviour.kill()
            newBall = Ball()
            balls.add(newBall)
            all_sprites.add(newBall)
        collide_sprite_player = pygame.sprite.spritecollideany(ball_sprite, players)
        if collide_sprite_player:
            ball_sprite.bounceOffGround()
    if len(bricks) == 0 and len(saviours) == 0 and player_lives > 0:
        lvl += 1  # increment the level in case the player is still healthy
        load()  # reload the game sprites
    if len(balls) == 0:
        running = False

    pygame.display.flip()
# end of the game loop

# game over display
gameover = pygame.image.load("assets/gameover.png")
gameover = pygame.transform.scale(gameover, (screen_width, screen_height))
screen.blit(gameover, (0, 0))
pygame.display.flip()
time.sleep(5)
pygame.quit()
