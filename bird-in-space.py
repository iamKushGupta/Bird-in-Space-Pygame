import pygame
from pygame.locals import *
import random

# Initializes all imported pygame modules
pygame.init()

# Creates a clock object that will help us control
# the frame rate of our game
clock = pygame.time.Clock()
fps = 60  # Sets the frame rate to 60 FPS
"""
If frame rate not set, then the game will try to run all the codes as soon as possible.
As in, the ground would end before the could end.
FPS sets the game's speed for all speeds. 
"""


# Set screen display size
screen_width = 864
screen_height = 900
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Bird In Space')  # Set window caption

# define font
font = pygame.font.SysFont('Bauhaus 93', 60) # 60 = font size
# define colours
white = (255, 255, 255)

# define game variables
ground_scroll = 0  # ground scroll speed
scroll_speed = 4  # the scrolling speed
flying = False # setting the game start event via this variable
game_over = False  
pipe_gap = 200  # Distance between 2 obstacles on same vertical axis
pipe_frequency = 1500  # milliseconds 
last_pipe = pygame.time.get_ticks() - pipe_frequency # time when last pipe was created. none at start
# also, pipes get started creating rights from the beginning
score = 0  # Intialises score fom Zero
pass_pipe = False  # Collision


# Load images
bg = pygame.image.load('img/bg1.jpg')  # Game Background
ground_img = pygame.image.load('img/ground5.png')  # Ground image
button_img = pygame.image.load('img/restart.png')  # Restart button image


# function for outputting text onto the screen | Score Counter
def draw_text(text, font, text_col, x, y): # Func. called in run loop
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y)) # render on screen

# This function resets the game
def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score

# Bird game using Pygame's Sprite classes
class Bird(pygame.sprite.Sprite):

    def __init__(self, x, y):
        # update and draw already pre-build into Sprite classes
        pygame.sprite.Sprite.__init__(self)
        self.images = []  # the image that the sprite is going to be assigned
        self.index = 0
        self.counter = 0  # controls the animatoin speed (bird's flutter)
        # the loop appends the images one after other, to create an animation in the bird
        for num in range(1, 4):
            img = pygame.image.load(f"img/bird{num}.png")
            self.images.append(img)  # appends images in the list made before
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]  # decides the location of the bird
        self.vel = 0 # bird does not translate horizontally for the scene
        self.clicked = False
    
    # Update the Bird. Sets gravity and flutter 
    def update(self):
        if flying == True:
            # Gravity implemetation
            self.vel += 0.5
            if self.vel > 8: # limits velocity
                self.vel = 8 # caps vel to 8
            if self.rect.bottom < 768: # ground coordinate=768, limits
                self.rect.y += int(self.vel)

        if game_over == False:
            # Fly the bird (JUMP)
            # self.clicked ensures that we can't hold onto the button, and keep going up.
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:  
                self.clicked = True
                self.vel = -10 # jumps by 2 (opposite to gravity)
            if pygame.mouse.get_pressed()[0] == 0: # ie, holding onto the mouse-click would get registered as only 1 click
                self.clicked = False

            # handle the animation
            flap_cooldown = 5
            self.counter += 1

            if self.counter > flap_cooldown:
                self.counter = 0 # reset to zero
                self.index += 1 # move to the next bird image to make flutter
                if self.index >= len(self.images): # if it comes to the end of list (3), we reset 
                    self.index = 0 # resets to index=0
                self.image = self.images[self.index]

            # Rotate the bird
            self.image = pygame.transform.rotate(
                self.images[self.index], self.vel * -2) # rotation wrt to velocity
            # * (-2) points the bird up once we click.
        else:
            # point the bird at the ground
            self.image = pygame.transform.rotate(self.images[self.index], -90)
            # rotates bird 90 degrees clockwise. (This is the condition for collision/game_over)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position): # initialisation
        pygame.sprite.Sprite.__init__(self) 
        self.image = pygame.image.load("img/pipe3.png")
        self.rect = self.image.get_rect() # image loaded and made a rectangle from it
        # position variable determines if the pipe is coming from the bottom or top
        # position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True) # false=Xaxis,True=yaxis
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        elif position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed # scroll speed for the pipes, towards left
        if self.rect.right < 0: # when the x coordinates goes off screen
            self.kill() # kills pipes once they off the screen. Saves memory and compute


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        # draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action


pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group() 

flappy = Bird(100, int(screen_height / 2))

bird_group.add(flappy)

# create restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

# make the game run. continuous loop until the break condition happens
run = True
while run:
    clock.tick(fps)

    # draw background
    screen.blit(bg, (0, 0))  # sets the background.

    pipe_group.draw(screen)
    bird_group.draw(screen)
    bird_group.update()

    # draw and scroll the ground
    # ground_scroll sets the scroll speed for the ground, to the left
    screen.blit(ground_img, (ground_scroll, 768)) # 768 = y-coordinate of ground

    # check the score
    if len(pipe_group) > 0: # giving the values in the pipeGrp
        
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
                and pass_pipe == False:
            # if the left side of the bird has gone past the rect.left of Pipe
            # and if the right side of the bird has gone past the rect.right of Pipe
            # and pass_pipe == False
            pass_pipe = True
        if pass_pipe == True: ## This below is the exit condition for score increment
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1 # scores increases
                pass_pipe = False
    draw_text(str(score), font, white, int(screen_width / 2), 20) # Draw the score on screen

    # look for collision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0: # also, if bird goes over the screen top, it's gameover
        game_over = True # if any element form birdGrp collides with any element from pipeGrp >> GameOver
    # once the bird has hit the ground it's game over and no longer flying
    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False # game over when bird hits ground

    if flying == True and game_over == False: # if flying is happening, and not gameover, we render pipes
        # generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100) # random pipe heights
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1) 
            top_pipe = Pipe(screen_width, int(
                screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe) # adds bottomPipe to pipeGrp
            pipe_group.add(top_pipe) # adds topPipe to pipeGrp
            last_pipe = time_now 

        pipe_group.update() # updates the pipe group with the newly generated pipes

        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 30:
            ground_scroll = 0

    # check for game over and reset
    if game_over == True:
        if button.draw():
            game_over = False
            score = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True

    pygame.display.update() # keeps window dynamically updating

pygame.quit()
