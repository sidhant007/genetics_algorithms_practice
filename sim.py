from __future__ import division
import numpy as np
import numpy.matlib as mat
from random import random as rand
import random
import math

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis = 0)

def comparator():
    def compare(x, y):
        if x[1] > y[1]:
            return -1
        elif x[1] < y[1]:
            return 1
        else:
            return x[0].getID() - y[0].getID()
    return compare

class player:
    def __init__(self, name, i):
        self.name = name
        self.money = 0
        self.id = i
        self.rank = i 
        self.sumRank = 0
        self.cardLeft = "N"
        
    def addMoney(self, money):
        self.money += 4 if self.cardLeft == "R" else 0
        self.money += money
        #print('{} has {}'.format(self.name, self.money))

    def updateRank(self, r):
        self.rank = r
        self.sumRank += r

    def getID(self):
        return self.id

class greedy(player):
    def __init__(self, name, i):
        player.__init__(self, name, i)

    def playCard(self):
        self.cardLeft = "R"
        return "B"

class cooperate(player):
    def __init__(self, name, i):
        player.__init__(self, name, i)

    def playCard(self):
        self.cardLeft = "B"
        return "R"

class grudger(player):
    def __init__(self, name, i):
        player.__init__(self, name, i)
        self.beenCheated = False

    def playCard(self):
        self.cardLeft = "R" if self.beenCheated else "B"
        return "R" if self.cardLeft == "B" else "B"

class agent(player):
    num_inputs = 4 
    num_middle = 5
    num_outputs = 2 
    def __init__(self, name):
        player.__init__(self, name, 0)
        self.input_matrix = [] # [total rank, total money, sum of all ranks]
        self.weights1 = np.asarray(mat.rand(agent.num_middle, agent.num_inputs))
        self.bias1 = np.asarray(mat.rand(agent.num_middle, 1))
        self.weights2 = np.asarray(mat.rand(agent.num_outputs, agent.num_middle))
        self.bias2 = np.asarray(mat.rand(agent.num_outputs, 1))

    def playCard(self):
        valB = self.makeChoice()[0] #Probability black is given
        valR = self.makeChoice()[1]
        self.cardLeft = "R" if valB > valR else "B"
        return "R" if self.cardLeft == "B" else "B"

    def setInputMatrix(self, inp_mat):
        self.input_matrix = inp_mat

    def makeChoice(self):
        result = []
        for row in self.weights1:
            result.append(np.asarray(np.dot(self.input_matrix, row)))
        result = np.reshape(np.asarray(np.squeeze(result)), (self.num_middle, 1))
        result = np.asarray(np.add(result, self.bias1))
        result = np.asarray(np.squeeze(result))
        result = softmax(result)
        result2 = []
        for row in self.weights2:
            result2.append(np.asarray(np.dot(result, row)))
        result2 = np.asarray(np.squeeze(np.asarray(np.add(result2, self.bias2))))
        result2 = softmax(result2)
        return [result2[0][0], result2[1][0]]

class game:
    
    def __init__(self):
        self.players = []
        self.a = agent("Agent")
        self.g = grudger("Grudger", 1)

        
    def initialize_game(self, num_players):
        self.a.setInputMatrix([num_players, 0, num_players, 0])
        self.players.append(self.a)
        self.players.append(self.g)
        for i in range(2, num_players // 2 + 1):
            self.players.append(greedy("Greedy" + str(i), i))
        for i in range(num_players // 2 + 1, num_players):
            self.players.append(cooperate("Cooperate" + str(i), i))
            
    def simulate_round(self):
        pool_money = 0 
        num_contributors = 0
        player_scores = []
        for player in self.players:
            play = player.playCard();
            pool_money += 100 if play == "R" else 0
        num_contributors = pool_money / 100
        pool_money /= len(self.players)
        for player in self.players:
            player.addMoney(pool_money)
            player_scores.append((player, player.money))
        player_scores = sorted(player_scores, cmp=comparator())
        for idx, player in enumerate(player_scores):
            #print player[0].getID()
            self.players[player[0].getID()].updateRank(idx + 1)
            print(player[0].name + ' is at rank ' + str(idx + 1) + ' with ' + str(player[0].money))
        return num_contributors

class nn:
    games = []
    inp_mat = []
    fitness = []
    def initialize(self, num_agents):
        for i in range(0, num_agents):
            self.games.append(game())

    def simulate_game(self, num_rounds):
        self.fitness = []
        for idx, game in enumerate(self.games):
            game.initialize_game(6)
            total_money = 0
            total_rank = 0
            print 'Simulating Game ' + str(idx + 1)
            for i in range(0, num_rounds):
                print 'Simulating Round ' + str(i)
                num_cheaters = 6 - game.simulate_round()
                total_money += 24
                total_rank += 6
                game.g.beenCheated = True if num_cheaters >= 3 else False
                game.a.setInputMatrix([game.a.rank / 6, game.a.money / total_money, game.a.sumRank / total_rank, num_cheaters / 6])
            print 'Done simulating game and computing fitness'
            print str(game.a.rank) + ' ' + str(game.a.money)
            self.fitness.append((game.a, game.a.money))
        self.fitness = sorted(self.fitness, cmp=comparator())
        print 'Simulation done. Here is the performance of the agents: '
        print str([x[1] for x in self.fitness])
        lucky_few = random.sample(self.fitness[5:], 2)
        fittest = [self.fitness[0], self.fitness[1], self.fitness[2]] + lucky_few
        self.cbf(fittest)

    def cbf(self, fittest):
        new_agents = []
        for i in range(0, len(fittest)):
            for j in range(i + 1, len(fittest)):
               new_agents.append(self.cross(fittest[i][0], fittest[j][0]))
        for idx in range(0, len(self.games)):
            self.games[idx] = game()
            self.games[idx].a = new_agents[idx]
    
    def cross(self, agent1, agent2):
        new_agent = agent("Agent")
        new_agent.weights1 = self.matrix_cross(agent1.weights1, agent2.weights1)
        new_agent.bias1 = self.matrix_cross(agent1.bias1, agent2.bias1)
        new_agent.weights2 = self.matrix_cross(agent1.weights2, agent2.weights2)
        new_agent.bias2 = self.matrix_cross(agent1.bias2, agent2.bias2)
        return new_agent

    def matrix_cross(self, m1, m2):
        new_mat = []
        for i in range(0, len(m1)):
            new_row = []
            for j in range(0, len(m1[0])):
                new_row.append(random.choice([m1[i][j], m2[i][j]]))
            new_mat.append(new_row)
        new_mat = np.reshape(new_mat, (len(m1), len(m1[0])))
        return new_mat


neural_network = nn()
neural_network.initialize(10)
instr = raw_input("Simulate ?\n")
while(instr != "N"):
    neural_network.simulate_game(10)
    instr = raw_input("Simulate ?\n")
        


