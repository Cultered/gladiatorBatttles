from typing import List, Callable, Iterable
#import numpy as np
import random
import json
import math
import tqdm


def relu(x):
    if x<0: return 0
    if x>1: return 1
    return x



DATA_PATH="/home/user/Documents/data.txt"
"""
def dot(a,b):

    return sum([a[i]*b[i] for i in range(len(a))])

def relu(x):
    if x<0: return 0
    if x>1: return 1
    return x

    

class Node:
    def __init__(self, size: int , inputs: List ,  activation_function: Callable[[float],float] = relu, weights: List[float] = None):
        self.activation_function = activation_function
        self.links = inputs
        self.size = size
        self.weights = weights
        if self.weights is None:
            self.weights = [0.5]*self.size

    def value(self):
        return dot(self.weights, [self.activation_function( i.value() ) for i in self.links] )

class DenseInputNode(Node):
    def __init__(self, arr: Iterable[float], activation_function: Callable[[float],float] = relu):
        self.weights = [0.5]*len(arr)
        self.size = len(arr)
        self.arr = arr
        self.activation_function = activation_function

    def value(self):
        return dot(self.weights, [self.activation_function( i ) for i in self.arr] )

inputs = [0.1, 0.2, 0.3]
input_layer = [DenseInputNode(arr=inputs, activation_function=math.atan) for i in range(2)]
final_layer = [Node(size = len(input_layer), inputs=input_layer) ]

print( [
    node.value ()
    for node in final_layer
])

exit(0)
"""        




class nconnection:
    def __init__(self,endNode):
        self.weight=0
        self.endNode=endNode

    def randomizeWeight(self,rang:float):
        self.weight+=random.uniform(-rang,rang)
    
    def randomizeWeightP(self,rang:float):
        if self.weight==0:
            self.weight=0.001
        self.weight+=random.uniform(-rang,rang)*self.weight

class nnode:
    def __init__(self,value:float):
        self.connections=[]
        self.value=value

    def loadWeights(self,weightsList:List[float]):
        if len(self.connections) != len(weightsList):
            raise Exception("Cannot load weights:number of connections(%d) does not match the number of loaded weights(%d)" %(len(self.connections),len(weightsList)))
        for i in range(len(self.connections)):
            self.connections[i].weight=weightsList[i]

    def addWeightedValue(self):
        for connection in self.connections:
            connection.endNode.value+=connection.weight*self.value
        
    def connect(self,node2):
        self.connections.append(nconnection(node2))
    
    def getWeights(self) -> List[float]:
        weights=[]
        for connection in self.connections:
            weights.append(connection.weight)
        return weights

    def randomizeWeights(self,rang:float):
        for connection in self.connections:
            connection.randomizeWeight(rang)

class nlayer:

    @staticmethod
    def emptyLayer(nodesn:int):
        newnodes=[]
        for i in range(nodesn):
            newnodes.append(nnode(0))
        return nlayer(newnodes)

    def __init__(self,nodes:List[nnode]):
        self.nodes=nodes

    def establishConnections(self,layer2):
        for node1 in self.nodes:
            for node2 in layer2.nodes:
                node1.connect(node2)

    def calculateNextLayer(self):
        for node in self.nodes:
            #node.value=math.atan(node.value)
            node.addWeightedValue()

    def loadWeights(self,weightsList:List[List[float]]):
        if len(self.nodes) != len(weightsList):
            raise Exception("Cannot load weights:number of nodes(%d) does not match the number of loaded nodes(%d)" %(len(self.nodes),len(weightsList)))
        for i in range(len(self.nodes)):
            self.nodes[i].loadWeights(weightsList[i])

    def getWeights(self) -> List[List[float]]:
        weights=[]
        for node in self.nodes:
            weights.append(node.getWeights())
        return weights

    def randomizeWeights(self,rang):
        for node in self.nodes:
            node.randomizeWeights(rang)

    def resetNodes(self):
        for node in self.nodes:
            node.value=0

class network:
    
    def getHighscore(self):return self.__maxscore

    def updateHighscore(self):self.__maxscore=self.score

    def emptyNetwork(layerConfig:List[int]):

        newlayers=[]
        for config in layerConfig:
            newlayers.append(nlayer.emptyLayer(config))
        newnetwork = network(newlayers)
        newnetwork.establishConnections()
        return newnetwork

    def __init__(self,layers:List[nlayer]):
        self.__maxscore=-float('inf')
        self.score=None
        self.layers=layers
        self.bestState=self.getWeights()
    
    def loadWeights(self,weightsList:List[List[List[float]]]):
        if len(self.layers) != len(weightsList):
            raise Exception("Cannot load weights:number of layers(%d) does not match the number of loaded layers(%d)" %(len(self.layers),len(weightsList)))
        for i in range(len(self.layers)):
            self.layers[i].loadWeights(weightsList[i])
        self.bestState=self.getWeights()

    def runNetwork(self) -> List[float]:
        for layer in self.layers:
            layer.calculateNextLayer()
        outputNodes=self.layers[-1].nodes
        output=[]
        for node in outputNodes:
            output.append(node.value)
        for layer in self.layers:layer.resetNodes()
        return output

    def getWeights(self) -> List[List[List[float]]]:
        weights=[]
        for layer in self.layers:
            weights.append(layer.getWeights())
        return weights

    def saveToFile(self, path):
        with open(path, "w") as f:
            json.dump(self.bestState, f)

    def loadFromFile(self, path):
        with open(path, "r") as f:
            self.loadWeights(json.load(f))

    def randomizeWeights(self,rang:float):
        for layer in self.layers:
            layer.randomizeWeights(rang)
        self.bestState=self.getWeights()

    def establishConnections(self):
        for i in range(len(self.layers)-1):
            self.layers[i].establishConnections(self.layers[i+1])

    def improveSingleWeight(self, rang):
        #if score is higher than previous, we keep the changed weght and change a new weight
        if self.score is None:
            return
        if self.score >= self.__maxscore:
            self.__maxscore=self.score
            self.bestState=self.getWeights()
            print("improved",self.__maxscore)
            self.changeRandomWeight(rang)
        #if score is lower than previous, we revert changed weight and change a new one
        else:
            a=1
            self.revertChanges()
            self.changeRandomWeight(rang)
            
    def insertInputValues(self,values:List[float]):
        if len(self.layers[0].nodes)!=len(values):
            raise Exception("Cannot input values, length of input(%d) does not match length of provided input(%d)"%(len(self.layers[0].nodes),len(values)))
        for i in range(len(values)):
            self.layers[0].nodes[i].value=values[i]

    def revertChanges(self):
        self.loadWeights(self.bestState)

    def changeRandomWeight(self,rang):
        changedConnection=random.choice(random.choice(self.layers[random.randint(0,len(self.layers)-2)].nodes).connections)
        changedConnection.randomizeWeight(rang)
'''
swordsmanNetwork=network.emptyNetwork([6,2])
#swordsmanNetwork.loadFromFile(DATA_PATH)
swordsmanNetwork.randomizeWeights(1)
swordsman=Swordsman(point3(300,300,0),100,"swordsman",40,1,130,20)


wizard=Wizard(point3(900,300,0),100,"wizard",40,2,30,20)

duel = Round([swordsman,wizard])
for j in range(100):
    swordsmanNetwork.insertInputValues(
        [
            swordsman.pos.x,
            swordsman.pos.y,
            swordsman.activeCooldowns["normalAttack"],
            wizard.pos.x,
            wizard.pos.y,
            wizard.activeCooldowns["shoot"]
        ]
    )
    desiredPosition = swordsmanNetwork.runNetwork()
    swordsman.setVelocity(point3(desiredPosition[0],desiredPosition[1],0))

    for entity in duel.entities:
        entity.step(0.1)
    duel.removeExpired()

swordsmanNetwork.score=-swordsman.pos.distance(wizard.pos)
swordsmanNetwork.updateHighscore()
desiredPosition=[]

#play other rounds
for i in tqdm.tqdm(range(10000)):
    swordsman.pos=point3(300,300,0)
    for j in range(100):
        swordsmanNetwork.insertInputValues(
            [
                swordsman.pos.x,
                swordsman.pos.y,
                swordsman.activeCooldowns["normalAttack"],
                wizard.pos.x,
                wizard.pos.y,
                wizard.activeCooldowns["shoot"]
            ]
        )
        swordsman.normalAttack()
        desiredPosition = swordsmanNetwork.runNetwork()
        swordsman.setVelocity(point3(desiredPosition[0],desiredPosition[1],0))

        for entity in duel.entities:
            entity.step(0.1)
        duel.removeExpired()
    
    swordsmanNetwork.score=-swordsman.pos.distance(wizard.pos)
    swordsmanNetwork.improveSingleWeight(1)

swordsmanNetwork.revertChanges()
print("final score:",swordsmanNetwork.getHighscore())
print(swordsmanNetwork.getWeights())
swordsmanNetwork.saveToFile(DATA_PATH)
'''