from captureAgents import AgentFactory
from captureAgents import CaptureAgent
import distanceCalculator
import operator
import random, time, util
from game import Directions
import game
from util import nearestPoint


class inferenceModule():
  def __init__(self):
    self.hasBeenInitialized = False
  
  def isOnOurSide(self,pos):
    if pos in self.ourside:
      return True
    return False
    
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
   
  def restrictBasedOnSensor(self,gameState, ourAgentpos):
    agentdistances = gameState.getAgentDistances()
    for enemy in self.enemypositions: #this is iterating over the keys to a map
      if gameState.getAgentPosition(enemy):
        self.enemypositions[enemy] = util.Counter()
        self.enemypositions[enemy][gameState.getAgentPosition(enemy)] = 1
      else:
        observeddistance = agentdistances[enemy]
        for pos in self.enemypositions[enemy]:
          self.enemypositions[enemy][pos] = self.enemypositions[enemy][pos] * gameState.getDistanceProb(util.manhattanDistance(ourAgentpos,pos), observeddistance)
#          self.enemypositions[enemy] = self.enemypositions[enemy] * gameState.getDistanceProb(1, observeddistance)
      self.enemypositions[enemy].normalize()
 
  def getInfoOnEnemyAgent(self, agentNumber):
    return self.enemypositions[agentNumber]

  def getEnemyMLEs(self):
    MLEestimators = {}
    for enemy in self.enemypositions:
      MLEestimators[enemy] = self.enemypositions[enemy].argMax()
    
    return MLEestimators      
        
  def updateBasedOnMovement(self, agentIndex, gameState): #currently this just assumes our opponents are wandering drunkenly.  Might improve that. Further doesn't reset them based on if they were captured.
    self.posterior = util.Counter()
    for position in self.enemypositions[agentIndex]:
      neighbors = []
      for p in self.legalPositions:  #we might consider optimizing this, but it should be ok.  Right now the process is O(n^2), could be O(n), but its the exponentials that kill ya.
        if util.manhattanDistance(p, position) <=1:
          neighbors.append(p)
 
      for neighbor in neighbors:
        self.posterior[neighbor] =  self.posterior[neighbor] + (self.enemypositions[agentIndex][position]/float(len(neighbors)))
    self.enemypositions[agentIndex] = self.posterior
      
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
 
  def initialize(self, iModel, isRed):
    self.inferenceModule = iModel
    self.isRed = isRed
  
  def getOurSideMazeDistance(self, posa, posb):
    return self.inferenceModule.ourSideDistancer.getDistance(posa,posb)
  def getWhoMovedLast(self, gameState): #this is buggy since we might be first to move.
    return (self.index-1) % (len(self.friends) + len(self.enemies))
  
  def updateInference(self, gameState):
    self.inferenceModule.updateBasedOnMovement(self.getWhoMovedLast(gameState), gameState)
    self.inferenceModule.restrictBasedOnSensor(gameState, self.whereAreWe(gameState))

  def matchUp(self, theirpos, ourpos):
    return min([self.getMazeDistance(theirpos,pos) - self.getOurSideMazeDistance(ourpos,pos) for pos in self.inferenceModule.edge])   
  def findWeakestLink(self, enemyPositions, ourPositions):
    if len(enemyPositions) == 0:
      return 1e10
    bestvalue = -1e10
    for i in range(0,len(ourPositions)):
      newOurPos = ourPositions[:]
      newOurPos.remove(ourPositions[i]) #this is ok even if two pacmen are hanging out on same square
      thisstrat = min(self.findWeakestLink(enemyPositions[1:], newOurPos), self.matchUp(enemyPositions[0],ourPositions[i]))
      if thisstrat > bestvalue:
        bestvalue = thisstrat
    return bestvalue

  def distanceToEdge(self,ourpositions):
    totalcost = 0
    for border in self.inferenceModule.edge:
      totalcost = totalcost + min([self.getOurSideMazeDistance(border,p) for p in ourpositions]) + sum([self.getOurSideMazeDistance(border,p) for p in ourpositions])/10.0
    return totalcost

  def evaluateBoard(self, gameState):
    enemyPositions = self.inferenceModule.getEnemyMLEs()
    ourPositions = [gameState.getAgentPosition(index) for index in self.friends]
    return self.findWeakestLink(enemyPositions.values(), ourPositions), self.distanceToEdge(ourPositions)
    
  def showListofPositions(self, list):
    weights = util.Counter()
    for pos in list:
      weights[pos] = 1
    weights.normalize()
    self.displayDistributionsOverPositions([weights])

  def chooseAction(self, gameState):
    self.updateInference(gameState)
    map = util.Counter()
    map[(30,14)] =1
    map[(16,1)]=1
    self.displayDistributionsOverPositions([map])
    actions = gameState.getLegalActions(self.index)

    bestaction = None
    bestranking = -1e10
    besttiebreaker = -1e10
    for action in actions:
      newState=gameState.generateSuccessor(self.index,action)
      if not self.inferenceModule.isOnOurSide(self.whereAreWe(newState)):
        continue
      actionranking,tiebreaker = self.evaluateBoard(newState)
      if actionranking>bestranking or (actionranking==bestranking and besttiebreaker>tiebreaker):
        bestaction = action
        besttiebreaker = tiebreaker
        bestranking = actionranking

    print 'Our action ' + str(action) + ' our score ' + str(bestranking) + ' our tiebreaker ' + str(besttiebreaker)
    return bestaction

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

