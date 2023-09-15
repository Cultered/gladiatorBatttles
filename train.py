"""module providing methods to calculate random numbers"""
import random
from typing import List
from model import Agent, Round, Swordsman, point3, Wizard, Projectile
from rl import network
import tqdm


NUM_AGENTS = 100
NUM_GENERATIONS = 200
STEPS = 20
DT = 0.1
SAMPLE_CHARACTER = Wizard(point3(300, 300, 0), 100, "wizard", 40, 1, 30, 1)
DEATH_RATE=0.5
LEARNING_RATE=0.2


networkLayout = [6, 4]


def load_top_ai_from_file(agent_list: List[Agent]):
    """loads AI weights for top 10 agents from last run from /home/user/Documents"""
    for num_agent in range(10):
        agent_list[num_agent].loadFromFile(
            f"/home/user/Documents/data{num_agent}.txt")


def run_single_duel(agent: Agent):
    """
        Run a simulation between Agent ``agent`` and an enemy
    """
    min_distances_to_enemies = {}
    sample_enemy = Swordsman(point3(0, 0, 0), 100, "swordsman", 40, 2, 130, 20)
    enemy_ai = Agent(sample_enemy)
    enemy_ai.loadFromFile("/home/user/Documents/swordsman_data.txt")
    enemy_ai.AI.randomizeWeights(1)
    agent.character.pos = point3(random.randint(
        0, 1200), random.randint(0, 700), 0)
    sample_enemy.pos = point3(random.randint(0, 1200), random.randint(0, 700), 0)
    duel = Round([agent.character, sample_enemy])
    agent.setRound()
    enemy_ai.setRound()
    for _ in range(STEPS):
        agent.makeMove()
        #enemy_ai.makeMove()
        for entity in duel.entities:
            entity.step(DT)
            if isinstance(entity, Projectile):
                min_distances_to_enemies[entity] = entity.min_distance_enemy

    score = sample_enemy.health
    agent.score += score
    agent.scores.append(score)


agents = [Agent(SAMPLE_CHARACTER) for i in range(NUM_AGENTS)]

for a in agents:
    a.setAI(network.emptyNetwork(networkLayout))
    a.AI.randomizeWeights(1)

#load_top_ai_from_file(agents)

for i in range(NUM_GENERATIONS):
    # run duels
    for a in agents:
        a.score=0
        for _ in range(100):
            run_single_duel(a)
    # delete 50% of the worst agents, create new agents that are a bit different from left agents
    agents.sort(key=lambda agent: agent.score)
    # print([a.score for a in agents])
    print(agents[-1].score, agents[-len(agents)//10].score,
          agents[len(agents)//2].score,agents[0].score)
    to_kill = int(len(agents)*DEATH_RATE)
    agents = agents[0:len(agents)-to_kill]
    newAgents = []
    for num_agent in range(to_kill):
        newAgent = Agent(SAMPLE_CHARACTER)
        newAgent.setAI(network.emptyNetwork(networkLayout))
        newAgent.AI.loadWeights(agents[num_agent%len(agents)].AI.getWeights())
        newAgent.AI.changeEveryWeight(LEARNING_RATE)
        newAgents.append(newAgent)
    agents.extend(newAgents)
    for j in range(10):
        agents[j].saveToFile(f"/home/user/Documents/data{j}.txt")

print(len(agents))
