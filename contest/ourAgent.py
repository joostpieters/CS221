from captureAgents import AgentFactory
from captureAgents import CaptureAgent
import distanceCalculator
import defenseModule
import holdTheLineModule
import operator
import opponentModeler
import random, time, util
from game import Directions
import game
import module
from util import nearestPoint


class inferenceModule():
  def __init__(self):
    self.hasBeenInitialized = False
    self.opponentModel = opponentModeler.opponentModel(self)
  
  def isOnOurSide(self,pos):
    return pos in self.ourside
    
  def analyzeMap(self, isRed, legalpositions, layout):
    self.width = max([p[0] for p in legalpositions])
    otherwidth = layout.width
    
    self.halfway = self.width/2
    self.ourside = [p for p in legalpositions if  operator.xor(p[0]>self.halfway, isRed)]
    self.theirside = [p for p in legalpositions if not operator.xor(p[0]>self.halfway, isRed)]

    ourSideLayout = layout.deepCopy()
    x=-1
    if(isRed):
      x=1
    sideToWallOff = self.halfway + x
    for i in range(layout.height):
      ourSideLayout.walls[sideToWallOff][i]=True

    self.ourSideDistancer = distanceCalculator.Distancer(ourSideLayout)
    self.ourSideDistancer.getMazeDistances()

    ourborder = []
    for pos in self.ourside:
      if len([p for p in self.theirside if util.manhattanDistance(p, pos)==1]):
        ourborder.append(pos)

    return ourborder

  def initialize(self, gameState, isRed, enemies):
    if self.hasBeenInitialized:
      return
    self.legalPositions = [p for p in gameState.getWalls().asList(False) if p[1] >0]
    self.edge = self.analyzeMap(isRed,self.legalPositions,gameState.data.layout)
    self.hasBeenInitialized = True

    self.enemypositions = {}

    for enemy in enemies:
       self.enemypositions[enemy] = util.Counter()
       self.enemypositions[enemy][gameState.getInitialAgentPosition(enemy)] = 1

  def getOurSideDistances(self, posa, posb):
    return self.ourSideDistancer.getDistance(posa, posb)
  
  def getInfoOnEnemyAgent(self, agentNumber):
    return self.enemypositions[agentNumber]

  def getEnemyMLEs(self):
    MLEestimators = {}
    for enemy in self.enemypositions:
      MLEestimators[enemy] = self.enemypositions[enemy].argMax()
    
    return MLEestimators      
  
  def restrictBasedOnSensor(self,gameState, ourAgentPos):
    self.opponentModel.updatePositionsBasedOnSensor(gameState,ourAgentPos)
      
  def updateBasedOnMovement(self, agentIndex, gameState): 
    self.opponentModel.updateBasedOnMovement(agentIndex, gameState)

class ourFactory(AgentFactory):
  "Returns one keyboard agent and offensive reflex agents"

  def __init__(self, isRed, first='offense', second='defense', rest='offense'):
    AgentFactory.__init__(self, isRed)
    self.isRed = isRed
    self.agents = [first, second]
    self.rest = rest

    self.iModel = inferenceModule()

  def getAgent(self, index):
    curAgent = ourAgent(index, timeForComputing=1)
    curAgent.initialize(self.iModel, self.isRed)
    return curAgent

def createTeam(firstIndex, secondIndex, isRed):
  agents = [ourAgent(firstIndex), ourAgent(secondIndex)]

  iModel = inferenceModule()

  for i in range(0, len(agents)): #rather than iterate in case you're making big changes
	agents[i].initialize(iModel, isRed)

  return agents
 
class ourAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def whereAreWe(self, gameState):
    return gameState.getAgentState(self.index).getPosition()

  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self,gameState)
    if self.isRed:
      self.friends = gameState.getRedTeamIndices()
      self.enemies = gameState.getBlueTeamIndices()
    else:
      self.friends = gameState.getBlueTeamIndices()
      self.enemies = gameState.getRedTeamIndices()
 
    self.inferenceModule.initialize(gameState, self.isRed, self.enemies) #infModule checks to make sure we don't do this twice
    #self.agentModule = module.agentModule(self.friends, self.enemies, self.isRed, self.index,self.inferenceModule)
    self.holdTheLineModule = holdTheLineModule.holdTheLineModule( self.friends, self.enemies, self.isRed,self.index, self.inferenceModule,self.distancer)
    self.defenseModule = defenseModule.defenseModule( self.friends, self.enemies, self.isRed,self.index, self.inferenceModule,self.distancer)

  def initialize(self, iModel, isRed):
    self.inferenceModule = iModel
    self.isRed = isRed

  def chooseAction(self,gameState):
    self.updateInference(gameState)
    enemyMLEs =self.inferenceModule.getEnemyMLEs().values()
    #self.displayDistributionsOverSquares(enemyMLEs)
    enemiesAttacking =[self.inferenceModule.isOnOurSide(enemyMLE) for enemyMLE in enemyMLEs]
    if max(enemiesAttacking): #this means one of them is on our side
      print "They're attacking man the stockade " + str(enemyMLEs)
      return self.defenseModule.chooseAction(gameState)
    else:
      return self.holdTheLineModule.chooseAction(gameState)
  
  def getWhoMovedLast(self, gameState): #this is buggy since we might be first to move.    
    return (self.index-1) % (len(self.friends) + len(self.enemies))

  def displayDistributionsOverSquares(self, squares):
    map = util.Counter()
    for square in squares:
      map[square] = 1
    #print "Squares we're showing are " + str(squares)
    self.displayDistributionsOverPositions([map]) 
 
  def updateInference(self, gameState):
    self.inferenceModule.updateBasedOnMovement(self.getWhoMovedLast(gameState), gameState)
    self.inferenceModule.restrictBasedOnSensor(gameState, self.whereAreWe(gameState))
    self.displayDistributionsOverSquares(self.inferenceModule.getEnemyMLEs().values())
