import random
from model import Agent, Round, Swordsman, point3
from rl import network
import tqdm


NUM_AGENTS = 2000
NUM_GENERATIONS = 500
STEPS = 50
DT = 0.1

networkLayout = [6, 2]


def run_single_duel(agent: Agent):
    """
        Run a simulation between Agent ``agent`` and a Swordsman
    """
    agent.character.pos = point3(500, 300, 0)
    enemy = Swordsman(point3(random.randint(100, 900), random.randint(
        100, 600), 0), 100, "swordsman", 40, 2, 130, 20)
    # enemy=Swordsman(point3(600,600,0),100,"swordsman",40,2,130,20)
    duel = Round([agent.character, enemy])
    agent.setRound()
    for _ in range(STEPS):
        agent.makeMove()
        for entity in duel.entities:
            entity.step(DT)
    score = agent.character.pos.distance(enemy.pos)
    agent.score = score
    agent.scores.append(score)


agents = [Agent(Swordsman(point3(300, 300, 0), 100, "swordsman",
                40, 1, 130, 20)) for i in range(NUM_AGENTS)]

for a in agents:
    a.setAI(network.emptyNetwork(networkLayout))
    a.AI.randomizeWeights(1)

for i in tqdm.tqdm(range(NUM_GENERATIONS)):
#for i in range(NUM_GENERATIONS):
    # run duels
    for a in agents:
        run_single_duel(a)
    # delete 50% of the worst agents, create new agents that are a bit different from left agents
    agents.sort(key=lambda agent: agent.score)
    # print([a.score for a in agents])
    print(agents[0].score, agents[len(agents)//10].score,
          agents[len(agents)//2].score)
    agents = agents[0:len(agents)//2]
    newAgents = []
    for a in agents:
        newAgent = Agent(Swordsman(point3(300, 300, 300),
                         100, "swordsman", 40, 1, 130, 20))
        newAgent.setAI(network.emptyNetwork(networkLayout))
        newAgent.AI.loadWeights(a.AI.getWeights())
        newAgent.AI.changeRandomWeight(0.02)
        newAgents.append(newAgent)
    agents.extend(newAgents)
    for i in range(10):
        agents[i].saveToFile(f"/home/user/Documents/data{i}.txt")

print(len(agents))
