import json
import math
from typing import List
from rl import network 

class point3:
    def __str__(self) -> str:
        return f"point3({self.x},{self.y},{self.z})"

    def printcoordinates(self):
        print(self.x,self.y,self.z)
    
    # TODO: decide if immutable class or not    
    def rotatex(self,w):
        yres=self.y*math.cos(w)-self.z*math.sin(w)
        zres=self.y*math.sin(w)+self.z*math.cos(w)
        self.y=yres
        self.z=zres
        
    def rotatez(self,w):
        xres=self.x*math.cos(w)-self.y*math.sin(w)
        yres=self.x*math.sin(w)+self.y*math.cos(w)
        self.x=xres
        self.y=yres


    def __init__(self, x, y, z):
        self.x=x
        self.y=y
        self.z=z
        self.length=math.sqrt(self.x*self.x+self.y*self.y+self.z*self.z)
        
    def add(self, p1):
        return(point3(self.x+p1.x,self.y+p1.y,self.z+p1.z))
        
    def neg(self):
        return point3(-self.x,-self.y,-self.z)
    
    def scale(self, factor):
        x=self.x*factor
        y=self.y*factor
        z=self.z*factor
        return point3(x,y,z)
    
    def distance(self, p):
        return math.sqrt((self.x-p.x)*(self.x-p.x)+(self.y-p.y)*(self.y-p.y))
    
    def ofLength(self, len):
        if self.length == 0:
            raise Exception("In Point3 attepted to normalize a zero vector")
        return(self.scale(len/self.length))

class Entity:
    
    def __init__(self,pos:point3,health,sprite,size,team):
        self.pos=pos
        self._velocity=point3(0,0,0)
        self.health=health
        self.maxhealth=health
        self.isAlive=True
        self.sprite=sprite
        self.team=team
        self.size=size
        self.round=None
        self.maxSpeed = 0

    def setVelocity(self, velocity: point3) -> None:
        if velocity.length==0:
            self._velocity=velocity
            return
        velocity = velocity.ofLength(self.maxSpeed)
        self._velocity = velocity
    
    def setRound(self, round):
        self.round = round
        
    def step(self,time):
        prepos=self.pos

        if not self.isAlive:return
        self.pos = self.pos.add((self._velocity.scale(time)))
        if self.round.entityOutOfBounds(self):
            self.pos=prepos
        if self.health<=0:
            self.death()
        if self.health>self.maxhealth:
            self.health=self.maxhealth
            
    def applyDamage(self,amount):
        self.health-=amount

    
    def death(self):
        self.isAlive=False
        self._velocity=point3(0,0,0)

class Character(Entity):
    pass

class Swordsman(Character):
    MAX_SPEED = 300
    
    def __init__(self,pos,health,sprite,size,team,wrange,damage):
        super().__init__(pos,health,sprite,size,team)
        self.wrange=wrange
        self.damage=damage
        self.cooldowns={"normalAttack":1}
        self.activeCooldowns={"normalAttack":0}
        self.maxSpeed = Swordsman.MAX_SPEED
    
    def step(self,time):
        super().step(time)
        #reset cds
        for skill, cd in self.activeCooldowns.items():
            self.activeCooldowns[skill] -= time
            if self.activeCooldowns[skill]<0:
                self.activeCooldowns[skill]=0

        
    def normalAttack(self):
        if not self.isAlive:return
        if self.activeCooldowns["normalAttack"]>0:
            return

        self.round.addEntity(
            Projectile(self.pos,100,"sword",self.wrange,self.team,self.damage,0.2)
        )

        self.activeCooldowns["normalAttack"]=self.cooldowns["normalAttack"]

class Healer(Character):
    def __init__(self,pos,health,sprite,size,team,healAmount,healRad):
        raise NotImplementedError("Need to review the code")
        super().__init__(pos,health,sprite,size,team)
        self.healAmount=healAmount
        self.healRad=healRad
        self.cooldowns={"smallHeal":4}
        self.activeCooldowns={"smallHeal":0}
        
    def step(self,time):
        super().step(time)
        #reset cds
        for skill, cd in self.activeCooldowns.items():
            self.activeCooldowns[skill] -= time
            if self.activeCooldowns[skill]<0:
                self.activeCooldowns[skill]=0
    
    def smallHeal(self,entities,healPos):
        if not self.isAlive:return   
        if self.activeCooldowns["smallHeal"]!=0:
            return
        
        healProjectile = Projectile(healPos,100,"heal",self.healRad,self.team,-self.healAmount,1)
        healProjectile.isHeal=True
        entities.insert(0,healProjectile)

        self.activeCooldowns["smallHeal"]=self.cooldowns["smallHeal"]

class Wizard(Character):
    MAX_SPEED = 300
    def __init__(self,pos,health,sprite,size,team,shootRadius,damage):
        super().__init__(pos,health,sprite,size,team)
        self.shootRadius=shootRadius
        self.damage=damage
        self.cooldowns={"shoot":2}
        self.activeCooldowns={"shoot":0}
        self.maxSpeed = Wizard.MAX_SPEED
        
    def step(self,time):
        super().step(time)
        #reset cds
        for skill, cd in self.activeCooldowns.items():
            self.activeCooldowns[skill] -= time
            if self.activeCooldowns[skill]<0:
                self.activeCooldowns[skill]=0
                
    def shoot(self,shootPos):
        if not self.isAlive:return
        if self.activeCooldowns["shoot"]!=0:
            return
        
        explosProjectile = Projectile(self.pos,30,"shoot",self.shootRadius,self.team,self.damage,1)
        explosProjectile.shoot(shootPos,1000)
        self.round.addEntity(explosProjectile)
                    
        self.activeCooldowns["shoot"]=self.cooldowns["shoot"]

class Projectile(Entity):
    MAX_SPEED = 2000

    def __init__(self,pos,health,sprite,size,team,damage,life):
        super().__init__(pos,health,sprite,size,team)
        self.damage=damage
        self.life=life
        self.hits=1
        self.isHeal=False
        self.maxSpeed = Projectile.MAX_SPEED

    def shoot(self, target: point3, speed: float):
        if speed>Projectile.MAX_SPEED:
            raise Exception("in Projectile.shoot MAX_SPEED exceeded")
        self.setVelocity(
            target.add(self.pos.neg()).ofLength(speed)
        )

    def step(self,time):
        super().step(time)

        if self.life<0:return

        self.life-=time
        
        if self.hits<=0:return
        
        for target in self.round.entities:
            if target==self:
                continue
            if not entitiesCollide(self,target):
                continue
            if self.isHeal and target.team == self.team:
                target.applyDamage(self.damage)
                self.hits-=1
            if not self.isHeal and target.team != self.team:
                target.applyDamage(self.damage)
                self.hits-=1

class Round:
    def __init__(self, initialEntities: List[Entity]):
        self.__entities = initialEntities
        for e in self.__entities:
            e.setRound(self)
        self.max_x = 1280
        self.max_y = 720

    @property
    def entities(self) -> List[Entity]:
        return self.__entities
    
    def addEntity(self, entity: Entity):
        # TODO: make a Z buffer
        self.__entities = [entity] + self.__entities
        entity.setRound(self)

    def entityOutOfBounds(self, e1:Entity) -> bool:
        return e1.pos.x<0 or e1.pos.x > self.max_x or  e1.pos.y<0 or e1.pos.y>self.max_y

    def removeExpired(self)->None:
        self.__entities = [e for e in self.__entities if not (type(e)==Projectile and e.life<0 ) ]

def entitiesCollide(e1:Entity,e2:Entity) -> bool:
    return e1.size+e2.size>e1.pos.distance(e2.pos)

class Agent:
    def __init__(self, character: Entity):
        self.character = character
        self.AI:network=None
        self.m = [0]
        self.scores=[]

    def setRound(self):
        self.round=self.character.round

    def setAI(self,AI:network):
        self.AI=AI
        self.score=None
        self.highscore=-float("inf")
    
    def makeMove(self):
        # TODO take closest instead first
        enemy = [ en for en in self.round.entities if isinstance(en, Character) and en.team != self.character.team ] [0]
        # calculate actions
        if self.AI is None:
            return
        
        if type(self.character) == Swordsman:
            self.AI.insertInputValues(
                [
                    self.character.pos.x,
                    self.character.pos.y,
                    list(self.character.activeCooldowns.values())[0],
                    enemy.pos.x,
                    enemy.pos.y,
                    list(enemy.activeCooldowns.values())[0]
                ]
            )
            self.character.normalAttack()
            desiredPosition = self.AI.runNetwork()
            self.character.setVelocity(point3(desiredPosition[0],desiredPosition[1],0))

    def saveToFile(self, path):
        with open(path, "w") as f:
            json.dump(self.AI.getWeights(), f)

    def loadFromFile(self, path):
        with open(path, "r") as f:
            weights=json.load(f)
            config = [len(layer) for layer in weights]
            self.AI = network.emptyNetwork(config)
            self.AI.loadWeights(weights)

    def improveAI(self,rang):
        self.AI.score=self.score
        self.AI.updateHighscore()
        self.AI.improveSingleWeight(rang)

    def avgScore(self):
        sum=0
        for i in self.scores:
            sum+=i
        return sum/len(self.scores)






