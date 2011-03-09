import boardExtractor
import kMeansClassifier
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
import minimaxModule
from minimaxModule import MinimaxModule
import module
import attackModule
from util import nearestPoint
import particleSwarmOptimizer
from particleSwarmOptimizer import ParticleSwarmOptimizable
import weightsConfig
import knownWeights
import cellLayout

def zeros(k):
  zeros = ''
  for i in range(k):
    zeros += '0'
  return zeros

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
      

    self.distancer = distanceCalculator.Distancer(layout)
    self.distancer.getMazeDistances()
    self.ourSideDistancer = distanceCalculator.Distancer(ourSideLayout)
    self.ourSideDistancer.getMazeDistances()

    ourborder = []
    for pos in self.ourside:
      if len([p for p in self.theirside if util.manhattanDistance(p, pos)==1]):
        ourborder.append(pos)

    return ourborder

  def initialize(self, gameState, isRed, enemies, index):
    if self.hasBeenInitialized:
      return
    self.legalPositions = [p for p in gameState.getWalls().asList(False) if p[1] >0]
    self.edge = self.analyzeMap(isRed,self.legalPositions,gameState.data.layout)
    self.hasBeenInitialized = True
    self.index = index
    self.enemypositions = {}
    self.isRed = isRed
    if(isRed):
      self.foodGrid = gameState.getRedFood()
    else:
      self.foodGrid = gameState.getBlueFood()
    self.lastKnownDistances = { self.index : gameState.getInitialAgentPosition(self.index) }
    for enemy in enemies:
       self.enemypositions[enemy] = util.Counter()
       self.enemypositions[enemy][gameState.getInitialAgentPosition(enemy)] = 1
       self.lastKnownDistances[enemy] = 999999


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
    self.opponentModel.updatePositionsBasedOnSensor(gameState, ourAgentPos) 

  def updateBasedOnMovement(self, agentIndex, gameState): 
    self.opponentModel.updateBasedOnMovement(agentIndex, gameState)
    self.opponentModel.updatePositionsBasedOnFood(agentIndex, gameState)

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

class ourAgent(CaptureAgent,minimaxModule.MinimaxModuleDelegate, ParticleSwarmOptimizable):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  
  ######################################
  #####ParticleSwarmOptimizable#########
  ######################################
  def getDefaultWeights(self):
      return weightsConfig.WeightsMap
  
  def getWeightMin(self, weightName):
      return weightsConfig.WeightsRangeMap[weightName][0]
  
  def getWeightMax(self, weightName):
      return weightsConfig.WeightsRangeMap[weightName][1]
  
  def setWeights(self, weights):
      self.heuristicWeights = weights
  ######################################
  
  def whereAreWe(self, gameState):
    return gameState.getAgentState(self.index).getPosition()

  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self,gameState)
    self.distancer.getMazeDistances()
    if self.isRed:
      self.friends = gameState.getRedTeamIndices()
      self.enemies = gameState.getBlueTeamIndices()
    else:
      self.friends = gameState.getBlueTeamIndices()
      self.enemies = gameState.getRedTeamIndices()

    self.inferenceModule.initialize(gameState, self.isRed, self.enemies, self.index)#infModule checks to make sure we don't do this twice
    self.cellLayout = cellLayout.CellLayout(gameState.data.layout, self.distancer) # pass one of these guys around
    thisLayoutInfo = boardExtractor.vectorize(gameState.data.layout,self.cellLayout)
    boardValues = knownWeights.ClusteringValues
    boardValues['thisone'] = thisLayoutInfo
   
    clusters, clusterElements =kMeansClassifier.kMeans(boardValues,4)

    ourCluster =None
    for cluster in clusterElements:
      if 'thisone' in clusterElements[cluster]:
        ourCluster =cluster
    
    cellmates = list(clusterElements[ourCluster])
    cellmates.remove('thisone')

    playingWeights = util.Counter()
    for mate in cellmates:
      for key in knownWeights.WeightsMap[mate]:
        playingWeights[key] += knownWeights.WeightsMap[mate][key]
    
    playingWeights.divideAll(float(len(cellmates)))
 
    #print playingWeights
      

#    self.setWeights(playingWeights)
    self.setWeights(weightsConfig.WeightsMap)
    
    self.holdTheLineModule = holdTheLineModule.holdTheLineModule( self.friends, self.enemies, self.isRed,self.index, self.heuristicWeights, self.inferenceModule, self.cellLayout, self.distancer)
    self.defenseModule = defenseModule.defenseModule( self.friends, self.enemies, self.isRed,self.index, self.heuristicWeights, self.inferenceModule, self.cellLayout, self.distancer)
    self.attackModule = attackModule.AttackModule( self.friends, self.enemies, self.isRed,self.index, self.heuristicWeights, self.inferenceModule, self.cellLayout, self.distancer)
    
  def initialize(self, iModel, isRed):
    self.inferenceModule = iModel
    self.isRed = isRed
    self.setWeights(self.getDefaultWeights())

  def getOurPositionMapping(self,gameState):
    mapping = {}
    for friend in self.friends:
      mapping[friend] = gameState.getAgentPosition(friend)
    return mapping

  def findDefensiveAndHLTMatchings(self,ourPositions, attackingEnemies,gameState):
    numberDefendersToSelect = len(attackingEnemies)
    if numberDefendersToSelect == 0:
      return {},ourPositions
    if numberDefendersToSelect > len(ourPositions):
      return ourPositions,{}
    ourGuysIndices = ourPositions.keys()

    maxValue = -1e10
    maxSet = {}
    for i in range(2**len(ourPositions)):
      bits = bin(i)[2:]
      bits = zeros(len(ourPositions)-len(bits)) + bits
      thisSetup = {}
      converseSetup = {}
      for index in range(len(ourGuysIndices)):
        if int(bits[index]) ==1:
          thisSetup[ourGuysIndices[index]]= ourPositions[ourGuysIndices[index]]
        else:
          converseSetup[ourGuysIndices[index]]= ourPositions[ourGuysIndices[index]]
      if len(thisSetup.keys()) != numberDefendersToSelect:
        continue
      else:
        value = self.defenseModule.evaluateBoard(thisSetup.values(),self.defenseModule.getOurFood(gameState) , attackingEnemies)
        if value > maxValue:
          maxValue= value
          maxSet = thisSetup
          maxConverseSet = converseSetup
    return maxSet, maxConverseSet

  def classifyNotAttackEnemies(self, gameState, notAttackingEnemies):
    sparringEnemies = []
    farEnemies = []
    
    edge = self.inferenceModule.edge

    
    for enemy in notAttackingEnemies:
      if min([self.distancer.getDistance(enemy, e) for e in edge]) > self.heuristicWeights['ourAgent_theyCanBeAttackingThreshold']:
        farEnemies.append(enemy)
      else:
        sparringEnemies.append(enemy)

    return sparringEnemies, farEnemies

  def findhltAttack(self,hltorAttackMatching, attackingEnemies,notAttackingEnemies): #this is embarressingly bad
    hltMatching = {}
    attackMatching = {}
   
    numberDefenders = len(attackingEnemies)
  
    if len(hltorAttackMatching.keys()) <= numberDefenders:
      return hltorAttackMatching, {}

    hltKeys = hltorAttackMatching.keys()[:numberDefenders]
    for key in hltorAttackMatching:
      if key not in hltKeys and min([self.distancer.getDistance(hltorAttackMatching[key], e) for e in self.inferenceModule.edge])<self.heuristicWeights['ourAgent_canBeAttackingThreshold']:
        attackMatching[key] =hltorAttackMatching[key]
      else:
        hltMatching[key] = hltorAttackMatching[key]
    return hltMatching,attackMatching
 
  def getStateValue(self,gameState):
    enemyMLEs =self.inferenceModule.getEnemyMLEs().values()
    enemiesAttacking =[self.inferenceModule.isOnOurSide(enemyMLE) for enemyMLE in enemyMLEs]
    attackingEnemies = []
    notAttackingEnemies = []
    for i in range(len(enemyMLEs)):
      if enemiesAttacking[i]:
        attackingEnemies.append(enemyMLEs[i])
      else:
        notAttackingEnemies.append(enemyMLEs[i])
    
    sparringEnemies, farEnemies = self.classifyNotAttackEnemies(gameState,notAttackingEnemies)
    ourPositions = self.getOurPositionMapping(gameState)
    #we've classified the map into three components, attacking enemies, sparring enemies and farenemies

    defensiveMatching = {}
    hltMatching = {}
    attackingMatching = {}

    for index in ourPositions.keys():
      if not self.inferenceModule.isOnOurSide(ourPositions[index]):
        attackingMatching[index] = ourPositions[index]
        del ourPositions[index]

    #now all of the people who are attacking won't be reassigned.
    defensiveMatching,hltorAttackMatching = self.findDefensiveAndHLTMatchings(ourPositions,attackingEnemies,gameState)
    hltMatching, additionalAttackMatching = self.findhltAttack(hltorAttackMatching, sparringEnemies,farEnemies)

    attackingMatching = dict(attackingMatching.items() + additionalAttackMatching.items())


    #what do we evaluate
    hltScore = self.holdTheLineModule.evaluateBoard(gameState,hltMatching.keys(), notAttackingEnemies) 
    dScore = self.defenseModule.evaluateBoard(defensiveMatching.values(), self.defenseModule.getOurFood(gameState),attackingEnemies)
    attackScore = self.attackModule.getStateValue(gameState)
    
    countAttackModule = 1
    if self.index not in attackingMatching.keys():
        countAttackModule=0
    return self.heuristicWeights['ourAgent_hltWeight'] * hltScore \
      +self.heuristicWeights['ourAgent_dWeight']*dScore\
      +countAttackModule*self.heuristicWeights['ourAgent_attackWeight']*attackScore

  def chooseAction(self, gameState):
    self.updateInference(gameState)

    minimaxMod = MinimaxModule(self)
    minimaxMod.setImpatience(0.1)
    minimaxVals = minimaxMod.getMinimaxValues(gameState, self.index, self.isRed, 0.8)

    bestActions = []
    bestVal = 0
    for pair in minimaxVals:
      if(bestVal < pair[1]):
        bestActions = []
      if(len(bestActions) == 0 or (bestVal == pair[1])):
        bestActions.append(pair[0])
        bestVal = pair[1]

    if(len(bestActions) == 0):
      return gameState.getLegalActions(self.index)[0]
    return random.choice(bestActions)

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

  def getWhoMovedLast(self, gameState): #this is buggy since we might be first to move.    
    return (self.index-1) % (len(self.friends) + len(self.enemies))

  def displayDistributionsOverSquares(self, squares):
    map = util.Counter()
    for square in squares:
      map[square] = 1
    self.displayDistributionsOverPositions([map]) 
 
  def updateInference(self, gameState):
    self.inferenceModule.updateBasedOnMovement(self.getWhoMovedLast(gameState), gameState)
    self.inferenceModule.restrictBasedOnSensor(gameState, self.whereAreWe(gameState))
    #self.displayDistributionsOverSquares(self.inferenceModule.getEnemyMLEs().values())
