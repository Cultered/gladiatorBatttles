import pygame
import random
from model import Agent, Swordsman, Round, Wizard, point3, Projectile
from rl import network
from typing import List

AGENT_DATA_PATH = "/home/user/1.txt"


# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

sprites={"swordsman":"gray30","sword":"grey","wizard":"purple","shoot":"orange","healer":"red","heal":"green"}

player=Wizard(point3(500,500,0),100,"wizard",40,1,30,30)
swordBot=Swordsman(point3(600,300,0),100,"swordsman",40,2,130,20)
wizardBot=Wizard(point3(600,600,0),100,"wizard",40,3,40,30)

round = Round([wizardBot,swordBot])

swordBotAgent=Agent(swordBot)
swordBotAgent.setRound()
swordBotAgent.loadFromFile("/home/user/Documents/swordsman_data.txt")
swordBotAgent.AI=network.emptyNetwork([12,4])

wizardBotAgent=Agent(wizardBot)
wizardBotAgent.setRound()
wizardBotAgent.loadFromFile("/home/user/Documents/data0.txt")
agents= [swordBotAgent,wizardBotAgent]
swordBotAgent.AI.getHighscore()

swordBotAgent.character.pos = point3(random.randint(
    0, 1200), random.randint(0, 700), 0)
wizardBot.pos = point3(random.randint(0, 1200), random.randint(0, 700), 0)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for agent in agents:
        agent.makeMove()

    # player moves
    keys = pygame.key.get_pressed()
    vx = 0
    vy = 0
    if keys[pygame.K_w]:
        vy-=300
    if keys[pygame.K_s]:
        vy+=300
    if keys[pygame.K_a]:
        vx-=300
    if keys[pygame.K_d]:
        vx+=300
    swordBot.setVelocity(point3(vx,vy,0))
    if pygame.mouse.get_pressed()[0]:
        player.shoot(
            point3(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1],0)
        )

    # physics
    for entity in round.entities:
        entity.step(dt)

    round.removeExpired()

    # draw game
    screen.fill("white")
    for entity in round.entities:
        if entity.isAlive==False:
            pygame.draw.circle(screen, "black", [entity.pos.x,entity.pos.y], entity.size)
            continue
        if entity.sprite in sprites:
            pygame.draw.circle(screen,sprites[entity.sprite],[entity.pos.x,entity.pos.y],entity.size)
            pygame.draw.circle(screen,pygame.Color(0,int(entity.health/entity.maxhealth*255),0),[entity.pos.x,entity.pos.y],4)
        else:
            pygame.draw.circle(screen,"yellow",[entity.pos.x,entity.pos.y],entity.size)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000
    
pygame.quit()
'''

def loadcoefs(name,coefs):
    with open(name, "wb") as f:
        pickle.dump(coefs, f)

def savecoefs(name):
    with open(name, "rb") as f:
        unpickled_array = pickle.load(f)
        return(repr(unpickled_array))

asworsman=Swordsman(point3(0,0,))


#health,x,y,cd,size  x2 ->angle
swordsmancoefs=[]
wizardcoefs=[]

for i in range(8):
    swordsmancoefs.append(random.uniform(-100,100))
    wizardcoefs.append(random.uniform(-100,100))

psworsmancoefs=swordsmancoefs 
pwizardcoefs=wizardcoefs

pswordsmanres=[0,100]
pwizardres=[0,100]

for i in range(100000):
    for j in range(1000):
'''