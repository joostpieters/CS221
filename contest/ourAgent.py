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
import attackModule
from util import nearestPoint

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

    self.inferenceModule.initialize(gameState, self.isRed, self.enemies, self.index)#infModule checks to make sure we don't do this twice
    #self.agentModule = module.agentModule(self.friends, self.enemies, self.isRed, self.index,self.inferenceModule)
    self.holdTheLineModule = holdTheLineModule.holdTheLineModule( self.friends, self.enemies, self.isRed,self.index, self.inferenceModule,self.distancer)
    self.defenseModule = defenseModule.defenseModule( self.friends, self.enemies, self.isRed,self.index, self.inferenceModule,self.distancer)
    self.attackModule = attackModule.AttackModule( self.friends, self.enemies, self.isRed,self.index, self.inferenceModule,self.distancer)
  def initialize(self, iModel, isRed):
    self.inferenceModule = iModel
    self.isRed = isRed

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
    print "Best set we can find is " + str(maxSet) + " with value " + str(maxValue) + " and converse set " + str(maxConverseSet)
    return maxSet, maxConverseSet

  def classifyNotAttackEnemies(self, gameState, notAttackingEnemies):
    sparringEnemies = []
    farEnemies = []
    
    edge = self.inferenceModule.edge

    
    for enemy in notAttackingEnemies:
      if min([self.distancer.getDistance(enemy, e) for e in edge]) > 5:
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
    print "number of defenders we think we need " + str(numberDefenders)
    for key in hltorAttackMatching:
      if key in hltKeys:
        hltMatching[key] = hltorAttackMatching[key]
      else:
        attackMatching[key] =hltorAttackMatching[key]
    return hltMatching,attackMatching
 
    
   

  def chooseAction(self,gameState):
    self.updateInference(gameState)
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
    print "Our current agent position is " + str(ourPositions[self.index])
    if not self.inferenceModule.isOnOurSide(ourPositions[self.index]):
      print "Attacking because we're on their side"
      return self.attackModule.chooseAction(gameState)
    for key in ourPositions.keys():
      if not self.inferenceModule.isOnOurSide(ourPositions[key]):
        del ourPositions[key]
    defensiveMatching,hltorAttackMatching = self.findDefensiveAndHLTMatchings(ourPositions,attackingEnemies,gameState)

    print "Close enemies " + str(sparringEnemies) + " far enemies " + str(farEnemies)
    hltMatching, attackMatching = self.findhltAttack(hltorAttackMatching, sparringEnemies,farEnemies)

    print "This is our attacker list " + str(attackMatching)

    if self.index in defensiveMatching: #this means one of them is on our side
      print "Our agent " + str(self.index) + " is playing defense" + str(defensiveMatching.keys()) + " against " + str(attackingEnemies)
      return self.defenseModule.chooseAction(gameState,defensiveMatching.keys(), attackingEnemies)
    elif self.index in attackMatching:
      print "Begin to attack"
      return self.attackModule.chooseAction(gameState)
    else:
      print "Our agent " + str(self.index) + " is playing HLT with " + str(hltMatching.keys()) + "against " + str(notAttackingEnemies)
      self.displayDistributionsOverSquares(enemyMLEs)
      return self.holdTheLineModule.chooseAction(gameState,hltMatching.keys(), notAttackingEnemies)
#      return self.holdTheLineModule.chooseAction(gameState,defensiveMatching, attackingEnemies)
  
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
