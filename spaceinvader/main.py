# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 20:12:19 2020

@author: Harshwardhan
"""

import pygame
import random
from pygame import mixer

# Initialize the pygame
pygame.init()

#System speed factor
X_FACTOR = 1

# Creating screen
screen = pygame.display.set_mode((800, 600))

# Background
background = pygame.image.load('background.jpg')

# Background Sound
mixer.music.load('background.wav')
mixer.music.play(-1)

# Caption and Icon
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load('spaceship.png')
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load('ship.png')
player_x = 370
player_y = 480
player_x_change = 0

# Enemy
enemyImg = [pygame.image.load('enemy.ico')] 
enemy_x = []
enemy_y = []
enemy_x_change = []
enemy_y_change = []
num_of_enemies = 6

for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load('enemy.ico'))
    enemy_x.append(random.randint(0, 735))
    enemy_y.append(random.randint(50, 150))
    enemy_x_change.append(1 * X_FACTOR)
    enemy_y_change.append(40)

# Bullet
bulletImg = pygame.image.load('bullet.png')
bullet_x = 0
bullet_y = 480
bullet_x_change = 0
bullet_y_change = 2.5 * X_FACTOR
bullet_state = "ready"

# Score

score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)

text_x = 10
text_y = 10

# Game over text
over_font = pygame.font.Font('freesansbold.ttf', 64)
game_over = False

def show_score(x, y):
    score = font.render("Score :" + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x,y))

def game_over_text():
    over_text = over_font.render('GAME OVER', True, (255, 255, 255))
    screen.blit(over_text, (200, 200))
    
def player(x = player_x , y = player_y):
    screen.blit(playerImg, (x, y))

def enemy(x , y, i):
    screen.blit(enemyImg[i], (x, y))

def fire_bullet(x = player_x , y = player_y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, ( x + 16 , y + 10 ))

def isCollision(enemy_x, enemy_y, bullet_x, bullet_y):
    distance_squared = (enemy_x - bullet_x)**2 + (enemy_y - bullet_y)**2
    if distance_squared < 27*27:
        return True
    return False
    
# Game Loop
running = True
while(running):
    
    # RGB background
    screen.fill((0, 0, 0))
    # Background image
    screen.blit(background, (0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.display.quit()
            break
    
    # if key is pressed
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            player_x_change = -1 * X_FACTOR
        if event.key == pygame.K_RIGHT:
            player_x_change = 1 * X_FACTOR
        if event.key == pygame.K_SPACE:
            if bullet_state == 'ready':
                bullet_sound = mixer.Sound('laser.wav')
                bullet_sound.play()
                bullet_x = player_x
                fire_bullet(bullet_x, bullet_y)
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_LEFT:
            player_x_change = 0
        if event.key == pygame.K_RIGHT:
            player_x_change = 0
        if game_over:
            running = False
            mixer.music.stop()
            pygame.display.quit()
            break
    
    player_x += player_x_change
    if player_x < 0:
        player_x = 0
    elif player_x > 736:
        player_x = 736
        
        
    # Enemy movement
    for i in range(num_of_enemies):
        
        # Game Over
        if enemy_y[i] > 440:
            for j in range(num_of_enemies):
                enemy_y[j] = 2000
            game_over_text()
            game_over = True
            break
        
        enemy_x[i] += enemy_x_change[i]
        if enemy_x[i] <= 0:
            enemy_x_change[i] = 2 * X_FACTOR
            enemy_y[i] += enemy_y_change[i]
        if enemy_x[i] > 736:
            enemy_x_change[i] = -2 * X_FACTOR
            enemy_y[i] += enemy_y_change[i]
            
        # Collision
        collision = isCollision(enemy_x[i], enemy_y[i], bullet_x, bullet_y)   
        if collision:
            explosion_sound = mixer.Sound('explosion.wav')
            explosion_sound.play()
            bullet_state  = 'ready'
            bullet_y = 480
            score_value += 1
            #print(score_value)
            enemy_x[i] = random.randint(0, 735)
            enemy_y[i] = random.randint(50, 150)
        
        enemy(enemy_x[i], enemy_y[i], i)
        
    # Bullet movement
    if bullet_y <= 0:
        bullet_y = 480
        bullet_state = 'ready'
    if bullet_state == 'fire':
        fire_bullet(bullet_x , bullet_y)
        bullet_y -= bullet_y_change
        
    
    player(player_x, player_y)
    show_score(text_x, text_y)
    pygame.display.update()
