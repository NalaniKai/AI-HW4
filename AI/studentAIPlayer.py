import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *
import unittest

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
        self.currGenes = []     #population 
        self.popSize = 6        #population size
        self.nextGene = 0       #current gene index
        self.fitness = []       #fitness score
        self.currFitness = []   #fitness scores of current gene
        self.currGame = 0
        self.geneGames = 2      #games to test current gene



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
            self.currGenes.append(positions)
            self.fitness.append(0)

    def getEnemySideCoord(self, pos):
        enemySetup = [(0,0), (5, 1), (0,3), (1,2), (2,1), (3,0), (0,2), (1,1), (2,0), \
            (0,1), (1,0)]

        while(True):
            #Choose any x location
            x = random.randint(0, 9)
            #Choose any y location on enemy side of the board
            y = random.randint(6, 9)
            #Set the move if this space is empty
            if (x, y) not in enemySetup or pos:
                return (x, y)

    def getAgentSideCoord(self, positions):
        while(True):
            #Choose any x location
            x = random.randint(0, 9)
            #Choose any y location on your side of the board
            y = random.randint(0, 3)
            #Set the move if this space is empty
            if (x, y) not in positions:
                return (x, y)

    def createChildren(self, parent1, parent2):
        #Create two children 
        split = random.randint(0,12)

        child1 = parent1[0:split]
        for coord in parent2[split:]:
            child1.append(coord)
        child1 = self.mutate(child1)

        child2 = parent2[0:split]
        for coord in parent1[split:]:
            child2.append(coord)
        child2 = self.mutate(child2)

        return [child1, child2]

    def mutate(self, child):
        chance = random.randint(0, 9)
        if chance < 3:
            pos = random.randint(0,len(child)-1)
            coord = None
            if pos < 11:
                coord = self.getAgentSideCoord(child)
            else:
                coord = self.getEnemySideCoord(child)

            child[pos] = coord 

        return child


    #def createGeneration(self):
        #next generation from the old one

    #def evalFitness(self):

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
        if self.currGenes == []:
            self.geneInit()

        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            return self.currGenes[self.nextGene][0:11]
        elif currentState.phase == SETUP_PHASE_2:
            return self.currGenes[self.nextGene][11:]
    
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
        moves = listAllLegalMoves(currentState)
        selectedMove = moves[random.randint(0,len(moves) - 1)];

        #don't do a build move if there are already 3+ ants
        numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        while (selectedMove.moveType == BUILD and numAnts >= 3):
            selectedMove = moves[random.randint(0,len(moves) - 1)];
            
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
        #Update fitness of currGene
        self.currFitness[self.currGame] = self.evalFitness()


        #Judge whether the current gene eval is complete




        #Create new Pop if all genes have been fully evaluated
        #reset index to the beginning


        pass

class Unit_Tests(unittest.TestCase):

    def testGeneInit(self):
        ai = AIPlayer(0)
        ai.geneInit()
        self.failIf(ai.currGenes is [])
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
        p1 = ai.currGenes[0]
        p2 = ai.currGenes[1]
        children = ai.createChildren(p1, p2)
        self.failIf(type(children) is not list)

    def testMutate(self):
        ai = AIPlayer(0)
        ai.geneInit()
        p1 = ai.currGenes[0]
        p2 = ai.currGenes[1]
        children = ai.createChildren(p1, p2)
        child = ai.mutate(children[0])
        self.assertTrue(type(child) is list)

    '''
    def testCreateGeneration(self):

    def testEvalFitness(self):

    def testGetPlacement(self):
        ai = AIPlayer(0)
        self.state = self.create_state(ai)
        self.failIf()

    def testGetMove(self):
        ai = AIPlayer(0)
        self.state = self.create_state(ai)
        self.failIf()

    def testRegisterWin(self):
    '''

def main():
    unittest.main()

if __name__ == '__main__':
    main()

