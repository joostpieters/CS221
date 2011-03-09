import capture
from capture import GameState
from game import GameStateData
from game import Configuration
from game import Directions
import ourAgent
import util
import random

class opponentModel():
  def __init__(self,inferenceModel):
    self.iModel = inferenceModel
  
  def updatePositionsBasedOnSensor(self, gameState, ourAgentPos):
    agentdistances = gameState.getAgentDistances()
    ourAgentEaten = (ourAgentPos == gameState.getInitialAgentPosition(self.iModel.index))
    for enemy in self.iModel.enemypositions: #this is iterating over the keys to a map
      enemyPos = gameState.getAgentPosition(enemy)
      if enemyPos:
        self.iModel.enemypositions[enemy] = util.Counter()
        self.iModel.enemypositions[enemy][gameState.getAgentPosition(enemy)] = 1
	self.iModel.lastKnownDistances[enemy] = util.manhattanDistance(enemyPos, ourAgentPos)
      else:
        if (not ourAgentEaten and self.iModel.lastKnownDistances[enemy] <= capture.SIGHT_RANGE - 3): #enemy was eaten, otherwise they'd be observable
          print "We think an enemy was eaten"
  	  self.iModel.enemypositions[enemy] = util.Counter()
          self.iModel.enemypositions[enemy][gameState.getInitialAgentPosition(enemy)] = 1
          self.iModel.lastKnownDistances[enemy] = 99999
        observeddistance = agentdistances[enemy]
        for pos in self.iModel.enemypositions[enemy]:
          if capture.SIGHT_RANGE < util.manhattanDistance(pos,ourAgentPos):
            self.iModel.enemypositions[enemy][pos] = self.iModel.enemypositions[enemy][pos] * gameState.getDistanceProb(util.manhattanDistance(ourAgentPos,pos), observeddistance)
          else:
            self.iModel.enemypositions[enemy][pos] = 0
#          self.enemypositions[enemy] = self.enemypositions[enemy] * gameState.getDistanceProb(1, observeddistance)
      self.iModel.enemypositions[enemy].normalize()
    
  def updatePositionsBasedOnFood(self, agentIndex, gameState):
    if(self.iModel.isRed):
      newGrid = gameState.getRedFood()
    else:
      newGrid = gameState.getBlueFood()
    for i in range(newGrid.width):
      for j in range(newGrid.height):
        if (self.iModel.foodGrid[i][j] != newGrid[i][j]):
          foodPos = (i,j)
          self.iModel.enemypositions[agentIndex] = util.Counter()
          self.iModel.enemypositions[agentIndex][foodPos] = 1
          print "Food eaten by index: " + str(agentIndex)
          break
    self.iModel.foodGrid = newGrid

  def getStateValue(self, gameState, position):
    red = self.iModel.isRed
    if(red):
      foodGrid = gameState.getRedFood()
    else:
      foodGrid = gameState.getBlueFood()
    eatingBonus = 0
    if (foodGrid[position[0]][position[1]]): eatingBonus = 1
    minDistance = 1e10
    for i in range(foodGrid.width):
      for j in range(foodGrid.height):
        if(foodGrid[i][j]):
          distance = self.iModel.distancer.getDistance(position, (i,j))
          if(distance < minDistance):
            minDistance = distance
    return  1e10*eatingBonus +  2**(foodGrid.width + foodGrid.height - minDistance)

  def updateBasedOnMovement(self, agentIndex, gameState): #currently this just assumes our opponents are wandering drunkenly.  Might improve that. Further doesn't reset them based on if they were captured.
    self.iModel.posterior = util.Counter()
    for position in self.iModel.enemypositions[agentIndex]:
      neighbors = []
      for p in self.iModel.legalPositions:  #we might consider optimizing this, but it should be ok.  Right now the process is O(n^2), could be O(n), but its the exponentials that kill ya.
        if util.manhattanDistance(p, position) <=1:
          neighbors.append(p)

      stateValues = []
      for neighbor in neighbors:
        stateValue = self.getStateValue(gameState, neighbor)
        stateValues.append(stateValue)
      total = sum(stateValues)
      for i in range(len(neighbors)):
	neighbor = neighbors[i]
        v = stateValues[i]
        self.iModel.posterior[neighbor] =  self.iModel.posterior[neighbor] + (self.iModel.enemypositions[agentIndex][position]*v/float(total)) 
    self.iModel.enemypositions[agentIndex] = self.iModel.posterior
