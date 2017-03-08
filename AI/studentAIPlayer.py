import random
import sys
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
        print(enemySetup)

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

        child2 = parent2[0:split]
        for coord in parent1[split:]:
            child2.append(coord)
        child2 = self.mutate(child2)

        return [child1, child2]

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
            if pos < 11:
                coord = self.getAgentSideCoord(child)
            else:
                coord = self.getEnemySideCoord(child)

            child[pos] = coord 

        return child

    def printState(self, bestGene):
        ai = AIPlayer(0)
        self.state = self.create_state(ai)

    def setup_state(self):
        board = [[Location((col, row)) for row in xrange(0,c.BOARD_LENGTH)] for col in xrange(0,c.BOARD_LENGTH)]
        p1Inventory = Inventory(c.PLAYER_ONE, [], [], 0)
        p2Inventory = Inventory(c.PLAYER_TWO, [], [], 0)
        neutralInventory = Inventory(c.NEUTRAL, [], [], 0)
        return GameState(board, [p1Inventory, p2Inventory, neutralInventory], c.SETUP_PHASE_1, c.PLAYER_ONE)

    def place_items(self, piece, constrsToPlace, state):
        #translate coords to match player
        piece = state.coordLookup(piece, state.whoseTurn)
        #get construction to place
        constr = constrsToPlace.pop(0)
        #give constr its coords
        constr.coords = piece
        #put constr on board
        state.board[piece[0]][piece[1]].constr = constr
        if constr.type == c.ANTHILL or constr.type == c.TUNNEL:
            #update the inventory
            state.inventories[state.whoseTurn].constrs.append(constr)
        else:  #grass and food
            state.inventories[c.NEUTRAL].constrs.append(constr)

    def setup_play(self, state):
        p1inventory = state.inventories[c.PLAYER_ONE]
        p2inventory = state.inventories[c.PLAYER_TWO]
        #get anthill coords
        p1AnthillCoords = p1inventory.constrs[0].coords
        p2AnthillCoords = p2inventory.constrs[0].coords
        #get tunnel coords
        p1TunnelCoords = p1inventory.constrs[1].coords
        p2TunnelCoords = p2inventory.constrs[1].coords
        #create queen and worker ants
        p1Queen = Ant(p1AnthillCoords, c.QUEEN, c.PLAYER_ONE)
        p2Queen = Ant(p2AnthillCoords, c.QUEEN, c.PLAYER_TWO)
        p1Worker = Ant(p1TunnelCoords, c.WORKER, c.PLAYER_ONE)
        p2Worker = Ant(p2TunnelCoords, c.WORKER, c.PLAYER_TWO)
        #put ants on board
        state.board[p1Queen.coords[0]][p1Queen.coords[1]].ant = p1Queen
        state.board[p2Queen.coords[0]][p2Queen.coords[1]].ant = p2Queen
        state.board[p1Worker.coords[0]][p1Worker.coords[1]].ant = p1Worker
        state.board[p2Worker.coords[0]][p2Worker.coords[1]].ant = p2Worker
        #add the queens to the inventories
        p1inventory.ants.append(p1Queen)
        p2inventory.ants.append(p2Queen)
        p1inventory.ants.append(p1Worker)
        p2inventory.ants.append(p2Worker)
        #give the players the initial food
        p1inventory.foodCount = 1
        p2inventory.foodCount = 1
        #change to play phase
        state.phase = c.PLAY_PHASE

    def create_state(self, ai):
        self.state = self.setup_state()
        players = [c.PLAYER_ONE, c.PLAYER_TWO]

        for player in players:
            self.state.whoseTurn = player
            constrsToPlace = []
            constrsToPlace += [Building(None, c.ANTHILL, player)]
            constrsToPlace += [Building(None, c.TUNNEL, player)]
            constrsToPlace += [Construction(None, c.GRASS) for i in xrange(0,9)]

            setup = ai.getPlacement(self.state)

            for piece in setup:
                self.place_items(piece, constrsToPlace, self.state)

            self.state.flipBoard()

        self.state.phase = c.SETUP_PHASE_2

        for player in players:
            self.state.whoseTurn = player
            constrsToPlace = []
            constrsToPlace += [Construction(None, c.FOOD) for i in xrange(0,2)]

            setup = ai.getPlacement(self.state)

            for food in setup:
                self.place_items(food, constrsToPlace, self.state)

            self.state.flipBoard()

        self.setup_play(self.state)
        self.state.whoseTurn = c.PLAYER_ONE
        return self.state
        '''

    def createGeneration(self):
        #put parent genes and score in dictionary
        parents = [dict({'gene':gene, 'score': self.fitness[i]}) for i, gene in enumerate(self.currPop)]
        self.currPop = []

        #sort parents by score descending 
        parents.sort(key=operator.itemgetter('score'), reverse=True)

        #get best half of parent genes
        bestParents = [i.values()[0] for i in parents]
        bestParents = bestParents[:self.popSize/2]

        #self.printState(bestParents[0])

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

    '''def testGeneInit(self):
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
        self.assertTrue(type(child) is list)'''

    def testCreateGeneration(self):
        ai = AIPlayer(0)
        ai.geneInit()
        ai.createGeneration()
        

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

