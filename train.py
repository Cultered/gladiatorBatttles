"""module providing methods to calculate random numbers"""
import random
from typing import List
from model import Agent, Round, Swordsman, point3, Wizard
from rl import network
import tqdm


NUM_AGENTS = 2000
NUM_GENERATIONS = 500
STEPS = 100
DT = 0.1
SAMPLE_CHARACTER=Wizard(point3(300, 300, 0), 100, "wizard", 40, 1, 1, 10)



networkLayout = [12, 4]

def load_top_ai_from_file(agent_list:List[Agent]):
    """loads AI weights for top 10 agents from last run from /home/user/Documents"""
    for num_agent in range(10):
        agent_list[num_agent].loadFromFile(f"/home/user/Documents/data{num_agent}.txt")

def run_single_duel(agent: Agent):
    """
        Run a simulation between Agent ``agent`` and an enemy
    """
    sample_enemy=Swordsman(point3(0,0,0), 100, "swordsman", 40, 2, 130, 20)
    enemy_ai=Agent(sample_enemy)
    enemy_ai.AI=network.emptyNetwork(networkLayout)
    enemy_ai.AI.randomizeWeights(1)
    agent.character.pos = point3(500, 300, 0)
    enemy = sample_enemy
    enemy.pos=point3(random.randint(100, 900), random.randint(100, 600), 0)
    duel = Round([agent.character, enemy])
    agent.setRound()
    enemy_ai.setRound()
    for _ in range(STEPS):
        agent.makeMove()
        #enemy_ai.makeMove()
        for entity in duel.entities:
            entity.step(DT)
    score = enemy.health
    agent.score = score
    agent.scores.append(score)


agents = [Agent(SAMPLE_CHARACTER) for i in range(NUM_AGENTS)]

for a in agents:
    a.setAI(network.emptyNetwork(networkLayout))
    a.AI.randomizeWeights(1)

#load_top_ai_from_file(agents)

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
        newAgent = Agent(SAMPLE_CHARACTER)
        newAgent.setAI(network.emptyNetwork(networkLayout))
        newAgent.AI.loadWeights(a.AI.getWeights())
        newAgent.AI.changeRandomWeight(0.02)
        newAgents.append(newAgent)
    agents.extend(newAgents)
    for j in range(10):
        agents[j].saveToFile(f"/home/user/Documents/data{j}.txt")

print(len(agents))
