from typing import List
# import numpy as np
import random
import json


def relu(num):
    """Returns 0 if ``num`` is less than zero, returns 1 if ``num`` is bigger than 1, 
    returns ``num`` otherwise"""
    if num < 0:
        return 0
    if num > 1:
        return 1
    return num


DATA_PATH = "/home/user/Documents/data.txt"


class nconnection:
    def __init__(self, endNode):
        self.weight = 0
        self.endNode = endNode

    def randomizeWeight(self, rang: float):
        self.weight += random.uniform(-rang, rang)

    def randomizeWeightP(self, rang: float):
        if self.weight == 0:
            self.weight = 0.001
        self.weight += random.uniform(-rang, rang)*self.weight


class nnode:
    def __init__(self, value: float):
        self.connections = []
        self.value = value

    def loadWeights(self, weightsList: List[float]):
        if len(self.connections) != len(weightsList):
            raise ValueError("Cannot load weights:number of connections(%d) does not match the number of loaded weights(%d)" % (
                len(self.connections), len(weightsList)))
        for i in range(len(self.connections)):
            self.connections[i].weight = weightsList[i]

    def addWeightedValue(self):
        for connection in self.connections:
            connection.endNode.value += connection.weight*self.value

    def connect(self, node2):
        self.connections.append(nconnection(node2))

    def getWeights(self) -> List[float]:
        weights = []
        for connection in self.connections:
            weights.append(connection.weight)
        return weights

    def randomizeWeights(self, rang: float):
        for connection in self.connections:
            connection.randomizeWeight(rang)


class nlayer:

    @staticmethod
    def emptyLayer(nodesn: int):
        newnodes = []
        for _ in range(nodesn):
            newnodes.append(nnode(0))
        return nlayer(newnodes)

    def __init__(self, nodes: List[nnode]):
        self.nodes = nodes

    def establishConnections(self, layer2):
        for node1 in self.nodes:
            for node2 in layer2.nodes:
                node1.connect(node2)

    def calculateNextLayer(self):
        for node in self.nodes:
            # node.value=math.atan(node.value)
            node.addWeightedValue()

    def loadWeights(self, weightsList: List[List[float]]):
        if len(self.nodes) != len(weightsList):
            raise ValueError("Cannot load weights:number of nodes(%d) does not match the number of loaded nodes(%d)" % (
                len(self.nodes), len(weightsList)))
        for i in range(len(self.nodes)):
            self.nodes[i].loadWeights(weightsList[i])

    def getWeights(self) -> List[List[float]]:
        weights = []
        for node in self.nodes:
            weights.append(node.getWeights())
        return weights

    def randomizeWeights(self, rang):
        for node in self.nodes:
            node.randomizeWeights(rang)

    def resetNodes(self):
        for node in self.nodes:
            node.value = 0


class network:

    def getHighscore(self): return self.__maxscore

    def updateHighscore(self): self.__maxscore = self.score

    @staticmethod
    def emptyNetwork(layerConfig: List[int]):

        newlayers = []
        for config in layerConfig:
            newlayers.append(nlayer.emptyLayer(config))
        newnetwork = network(newlayers)
        newnetwork.establishConnections()
        return newnetwork

    def __init__(self, layers: List[nlayer]):
        self.__maxscore = -float('inf')
        self.score = None
        self.layers = layers
        self.bestState = self.getWeights()

    def loadWeights(self, weightsList: List[List[List[float]]]):
        if len(self.layers) != len(weightsList):
            raise ValueError("Cannot load weights:number of layers(%d) does not match the number of loaded layers(%d)" % (
                len(self.layers), len(weightsList)))
        for i in range(len(self.layers)):
            self.layers[i].loadWeights(weightsList[i])
        self.bestState = self.getWeights()

    def runNetwork(self) -> List[float]:
        for layer in self.layers:
            layer.calculateNextLayer()
        outputNodes = self.layers[-1].nodes
        output = []
        for node in outputNodes:
            output.append(node.value)
        for layer in self.layers:
            layer.resetNodes()
        return output

    def getWeights(self) -> List[List[List[float]]]:
        weights = []
        for layer in self.layers:
            weights.append(layer.getWeights())
        return weights

    def saveToFile(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.bestState, f)

    def loadFromFile(self, path):
        with open(path, "r", encoding="utf_8") as f:
            self.loadWeights(json.load(f))

    def randomizeWeights(self, rang: float):
        for layer in self.layers:
            layer.randomizeWeights(rang)
        self.bestState = self.getWeights()

    def establishConnections(self):
        for i in range(len(self.layers)-1):
            self.layers[i].establishConnections(self.layers[i+1])

    def improveSingleWeight(self, rang):
        # if score is higher than previous, we keep the changed weght and change a new weight
        if self.score is None:
            return
        if self.score >= self.__maxscore:
            self.__maxscore = self.score
            self.bestState = self.getWeights()
            print("improved", self.__maxscore)
            self.changeRandomWeight(rang)
        # if score is lower than previous, we revert changed weight and change a new one
        else:
            self.revertChanges()
            self.changeRandomWeight(rang)

    def insertInputValues(self, values: List[float]):
        if len(self.layers[0].nodes) != len(values):
            raise ValueError("Cannot input values, length of input(%d) does not match length of provided input(%d)" % (
                len(self.layers[0].nodes), len(values)))
        for i in range(len(values)):
            self.layers[0].nodes[i].value = values[i]

    def revertChanges(self):
        self.loadWeights(self.bestState)

    def changeRandomWeight(self, rang):
        changedConnection = random.choice(random.choice(
            self.layers[random.randint(0, len(self.layers)-2)].nodes).connections)
        changedConnection.randomizeWeight(rang)
