from model import Agent,Round,Swordsman,point3
from rl import network
import tqdm
import random


numAgents=2000
numGenerations=500
steps=50
dt=0.1

networkLayout=[6,2]

def runSingleDuel(agent:Agent):
    agent.character.pos=point3(500,300,0)
    enemy=Swordsman(point3(random.randint(100,900),random.randint(100,600),0),100,"swordsman",40,2,130,20)
    #enemy=Swordsman(point3(600,600,0),100,"swordsman",40,2,130,20)
    round=Round([agent.character,enemy])
    agent.setRound()
    for i in range(steps):
        agent.makeMove()
        for e in round.entities:
            e.step(dt)
    score=agent.character.pos.distance(enemy.pos)
    agent.score=score
    agent.scores.append(score)
    



agents=[Agent(Swordsman(point3(300,300,0),100,"swordsman",40,1,130,20)) for i in range(numAgents)]

for a in agents:
    a.setAI(network.emptyNetwork(networkLayout))
    a.AI.randomizeWeights(1)

#for i in tqdm.tqdm(range(numGenerations)):
for i in range(numGenerations):
    #run duels
    for a in agents:
        runSingleDuel(a)
    #delete 50% of the worst agents, create new agents that are a bit different from left agents
    agents.sort(key=lambda agent:agent.score)
    #print([a.score for a in agents])
    print(agents[0].score, agents[len(agents)//10].score, agents[len(agents)//2].score)
    agents=agents[0:len(agents)//2]
    newAgents=[]
    for a in agents:
        newAgent=Agent(Swordsman(point3(300,300,300),100,"swordsman",40,1,130,20))
        newAgent.setAI(network.emptyNetwork(networkLayout))
        newAgent.AI.loadWeights(a.AI.getWeights())
        newAgent.AI.changeRandomWeight(0.02)
        newAgents.append(newAgent)
    agents.extend(newAgents)
    for i in range(10):
        agents[i].saveToFile("/home/user/Documents/data%d.txt"%(i))

print(len(agents))