import random
import sys
import os.path
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
import AIPlayerUtils as utils
import unittest
import itertools as itert 
import collections as collect
import operator as operator
from Building import Building

##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "Genetic")
        self.currPop = []     #population 
        self.popSize = 6        #population size
        self.nextGene = 0       #current gene index
        self.fitness = []       #fitness score
        self.currFitness = []   #fitness scores of current gene
        self.currGame = 0
        self.geneGames = 2      #games to test current gene
        self.currentGameState = None   #currentGameState


    def geneInit(self):
        '''
        Description: Initializes first population of genes with random coordinates
        '''
        #init with random values
        for j in range(0, self.popSize):
            numToPlace = 11
            positions = []
            #grass, anthill, tunnel
            for i in range(0, numToPlace):
                pos = None
                while pos == None:
                    pos = self.getAgentSideCoord(positions)
                positions.append(pos)
            #food
            numToPlace = 2
            pos = []
            for i in range(0, numToPlace):
                pos = None
                while pos == None:
                    pos = self.getEnemySideCoord(pos)
                positions.append(pos)
            self.currPop.append(positions)
            self.fitness.append(0)

    def getEnemySideCoord(self, pos):
        '''
        Description: Randomly generates a coordniate that is not occupied on the enemy's side of the board

        Parameters:
            pos - coordinate that has been used 

        Returns: Random, unoccupied coordinate on the enemy's side of the board
        '''
        enemySetup = [(9,9), (9, 8), (8,9), (9,7), (9,6), (8,8), (8,7), (7,9), (7,8), \
            (6,9), (4,8)]

        enemySetup.append(pos)

        while(True):
            #Choose any x location
            x = random.randint(0, 9)
            #Choose any y location on enemy side of the board
            y = random.randint(6, 9)
            #Set the move if this space is empty
            if (x, y) not in enemySetup:
                return (x, y)

    def getAgentSideCoord(self, positions):
        '''
        Description: Randomly generates a coordniate that is not occupied on the agent's side of the board

        Parameters:
            positions - list of coordinates that have been used 

        Returns: Random, unoccupied coordinate on the agent's side of the board
        '''
        while(True):
            #Choose any x location
            x = random.randint(0, 9)
            #Choose any y location on your side of the board
            y = random.randint(0, 3)
            #Set the move if this space is empty
            if (x, y) not in positions:
                return (x, y)

    def checkParent(self, agentSide, enemySide, parent):
        for coord in parent[:11]:
            if len(agentSide) < 11:
                if coord not in agentSide:
                    agentSide.append(coord)
            else:
                break

        for coord in parent[11:]:
            if len(enemySide) < 2:
                if coord not in enemySide:
                    enemySide.append(coord)
            else:
                break

        return (agentSide, enemySide)

    def ensureDifferent(self, child, parent1, parent2):
        #make copy of child
        agentSide = child[:11]
        enemySide = child[11:]

        agentSide = list(set(agentSide))
        enemySide = list(set(enemySide))

        result = self.checkParent(agentSide, enemySide, parent1)
        result = self.checkParent(result[0], result[1], parent2)

        newChild = result[0]
        newChild.append(result[1][0])
        newChild.append(result[1][1])

        return newChild


    def createChildren(self, parent1, parent2):
        '''
        Description: Randomly generates a position to split the parent genes and crossover. Creates
                     two children from two parents and has a probability of having an additional mutation.

        Parameters:
            parent1 - parent to create child with
            parent2 - parent to create child with

        Returns: Two children genes 
        ''' 
        split = random.randint(0,12)

        child1 = parent1[0:split]
        for coord in parent2[split:]:
            child1.append(coord)
        child1 = self.mutate(child1)
        child1 = self.ensureDifferent(child1, parent1, parent2)

        child2 = parent2[0:split]
        for coord in parent1[split:]:
            child2.append(coord)
        child2 = self.mutate(child2)
        child2 = self.ensureDifferent(child2, parent1, parent2)

        return [child1, child2]

    def getCoord(self, pos, child):
        coord = None
        if pos < 11:
            coord = self.getAgentSideCoord(child)
        else:
            coord = self.getEnemySideCoord(child)

        return coord 

    def mutate(self, child):
        '''
        Description: Randomly and legally mutates a child with a probability

        Parameters:
            child - child gene to be mutated or left alone

        Returns:
            child gene which could be mutated or not
        '''
        chance = random.randint(0, 9)
        if chance < 3:
            pos = random.randint(0,len(child)-1)
            coord = None
            
            child[pos] = self.getCoord(pos, child)
        return child

    def printState(self, bestGene):
        ants1 = []
        cons1 = []
        ants2 = []
        cons2 = [] #Booger Player Buildings
        cons3 = [] #FOOD
        
        for i, coord in enumerate(bestGene):
            if i == 0:
                cons1.append(Building((coord), ANTHILL, self.playerId))
            elif i == 1:
                cons1.append(Building((coord), TUNNEL, self.playerId))
            elif i < 11:
                cons1.append(Building((coord), GRASS, self.playerId))
            else:
                cons3.append(Building((coord), FOOD, NEUTRAL))

        newInventories = [Inventory(self.playerId, ants1, cons1, 0),
                        Inventory(abs(self.playerId-1), ants2, cons2, 0),
                        Inventory(NEUTRAL, [], cons3, 0) ]
        dummyState =  GameState(None, newInventories, 2, self.playerId)

        self.asciiPrintState(dummyState)

    def asciiPrintState(self, state):
        file = 'evidence.txt'
        f = None 
        if os.path.isfile(file):
            f = open(file, 'a')
        else:
            f = open(file, 'w')

        f.write("\n")
        #select coordinate ranges such that board orientation will match the GUI
        #for either player
        coordRange = range(0,10)
        colIndexes = " 0123456789"
        if (state.whoseTurn == PLAYER_TWO):
            coordRange = range(9,-1,-1)
            colIndexes = " 9876543210"

        #print the board with a border of column/row indexes
        f.write(str(colIndexes) + "\n")
        index = 0              #row index
        for x in coordRange:
            row = str(x)
            for y in coordRange:
                ant = utils.getAntAt(state, (y, x))
                if (ant != None):
                    row += utils.charRepAnt(ant)
                else:
                    constr = utils.getConstrAt(state, (y, x))
                    if (constr != None):
                        row += utils.charRepConstr(constr)
                    else:
                        row += "."
            f.write(row + str(x) + "\n")
            index += 1
        f.write(str(colIndexes) + "\n")
        f.close()

    def createGeneration(self):
        #put parent genes and score in dictionary
        parents = [dict({'gene':gene, 'score': self.fitness[i]}) for i, gene in enumerate(self.currPop)]
        self.currPop = []

        #sort parents by score descending 
        parents.sort(key=operator.itemgetter('score'), reverse=True)

        #get best half of parent genes
        bestParents = [i.values()[0] for i in parents]
        bestParents = bestParents[:self.popSize/2]

        self.printState(bestParents[0])

        #get all combinations of parents in best half
        parentPairs = itert.combinations(bestParents, 2)

        #get children to fill next population
        for pair in parentPairs:
            children = self.createChildren(pair[0], pair[1])
            self.currPop.append(children[0])
            self.currPop.append(children[1])
            if len(self.currPop) == self.popSize:
                break

    def evalFitness(self, hasWon):
        score = 0
        if self.currentGameState != None:
            total = 19
            agentInv = []
            enemyInv = []

            invOne = self.currentGameState.inventories[0]
            invTwo = self.currentGameState.inventories[1]

            if invOne.player == self.playerId:
                agentInv = invOne
                enemyInv = invTwo
            else:
                agentInv = invTwo
                enemyInv = invOne

            agentPoints = (agentInv.foodCount + agentInv.getQueen().health) / total
            enemyPoints = (enemyInv.foodCount + enemyInv.getQueen().health) / total
            score = (agentPoints - enemyPoints) * .5
                
        if hasWon: 
            score += .5 
        else:
            score -= .5
            
        return score

    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        if self.currPop == []:
            self.geneInit()
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            return self.currPop[self.nextGene][0:11]
        elif currentState.phase == SETUP_PHASE_2:
            return self.currPop[self.nextGene][11:]
    
    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        moves = utils.listAllLegalMoves(currentState)
        selectedMove = moves[random.randint(0,len(moves) - 1)];

        #don't do a build move if there are already 3+ ants
        numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        while (selectedMove.moveType == BUILD and numAnts >= 3):
            selectedMove = moves[random.randint(0,len(moves) - 1)];

        if currentState != None:
            self.currentGameState = currentState 
            
        return selectedMove
    
    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]
  
    ##
    #registerWin
    #Description: The last method, registerWin, is called when the game ends and simply 
    #indicates to the AI whether it has won or lost the game. This is to help with 
    #learning algorithms to develop more successful strategies.
    #
    #Parameters:
    #   hasWon - True if the player has won the game, False if the player lost. (Boolean)
    #
    def registerWin(self, hasWon):
        #give fitness score to current trial of current gene
        self.currFitness.append(self.evalFitness(hasWon))
        #increment to next game trial for current gene
        self.currGame += 1

        #reached number of trials per gene
        if self.currGame == self.geneGames:
            #setting fitness score for gene
            self.fitness.append(self.calcFitness())
            self.nextGene += 1      #incrementing to use next gene
            self.currGame = 0       #reset current game count
            self.currFitness = []   #reset fitness trial scores

        #reached population size
        if self.nextGene == self.popSize:
            self.createGeneration() #create new generation
            self.nextGene = 0       #reset current gene index
            self.fitness = []       #reset fitness score
            self.currFitness = []   #reset fitness scores of current gene
            self.currGame = 0       #reset trials

        pass

    def calcFitness(self):
        total = 0.0
        for score in self.currFitness:
            total += score
        return score / len(self.currFitness)

class Unit_Tests(unittest.TestCase):

    def testGeneInit(self):
        ai = AIPlayer(0)
        ai.geneInit()
        self.failIf(ai.currPop is [])
        self.failIf(ai.fitness is [])

    def testGetEnemySideCoord(self):
        ai = AIPlayer(0)
        pos = ai.getEnemySideCoord((0,0))
        self.assertTrue(type(pos) is tuple)

    def testGetAgentSideCoord(self):
        ai = AIPlayer(0)
        pos = ai.getAgentSideCoord([(0,0),(2,0),(6,8)])
        self.assertTrue(type(pos) is tuple)

    def testCreateChildren(self):
        ai = AIPlayer(0)
        ai.geneInit()
        p1 = ai.currPop[0]
        p2 = ai.currPop[1]
        children = ai.createChildren(p1, p2)
        self.failIf(type(children) is not list)

    def testMutate(self):
        ai = AIPlayer(0)
        ai.geneInit()
        p1 = ai.currPop[0]
        p2 = ai.currPop[1]
        children = ai.createChildren(p1, p2)
        child = ai.mutate(children[0])
        self.assertTrue(type(child) is list)

    def testCreateGeneration(self):
        ai = AIPlayer(0)
        ai.geneInit()
        ai.createGeneration()

def main():
    unittest.main()

if __name__ == '__main__':
    main()

