import module
from module import agentModule
import minimaxModule
from minimaxModule import MinimaxModule
import random
import time
import cellLayout

class AttackModule(agentModule, minimaxModule.MinimaxModuleDelegate):

  def chooseAction(self, gameState):
      print("Agent " + str(self.index) + " choosing an action")
      minimaxMod = MinimaxModule(self)
      minimaxMod.setImpatience(float(self.heuristicWeights['attackModule_percentImpatience'])/100.0)
      minimaxVals = minimaxMod.getMinimaxValues(gameState, self.index, self.isRed, 0.1)
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

  def getStateValue(self, gameState):
      foodDistances = self.distanceToFood(gameState, not self.isRed)
      nearestFoodVal = self.heuristicWeights['attackModule_nearestFoodCoeff'] * pow(foodDistances[0], self.heuristicWeights['attackModule_nearestFoodPower'])
      totalFoodVal = self.heuristicWeights['attackModule_totalFoodCoeff'] * foodDistances[1]
      nearestCapsuleVal = self.heuristicWeights['attackModule_nearestCapsuleCoeff'] * self.nearestCapsule(gameState)
      foodCount = self.getFoodCount(gameState, not self.isRed)
      numFoodsVal = self.heuristicWeights['attackModule_foodEatenReward'] * self.getFoodCount(gameState, not self.isRed)
      distanceApartVal = self.heuristicWeights['attackModule_distanceApartReward'] * self.distanceApart(gameState)
      enemyDistanceVal = self.heuristicWeights['attackModule_distanceToEnemies'] * self.distanceToEnemies(gameState)
      trappedPenaltyVal = self.heuristicWeights['attackModule_trappedPenaltyCoeff'] *self.trappedPenalty(gameState)
      return -numFoodsVal - nearestFoodVal - totalFoodVal - nearestCapsuleVal + distanceApartVal + enemyDistanceVal + trappedPenaltyVal
            
  def getFoodCount(self, gameState, red):
      foodCounter = 0
      if(red):
          foodGrid = gameState.getRedFood()
      else:
          foodGrid = gameState.getBlueFood()
      for foodRow in foodGrid:
          for foodItem in foodRow:
              if(foodItem): foodCounter += 1
      return foodCounter

  """
  Returns our distance to the nearest food and the total distance to all foods as tuple
  """
  def distanceToFood(self, gameState, red):
      ourPos = gameState.getAgentPosition(self.index)
      if(ourPos == None): #if we can't find ourself, it is time to panic
          return -1
      
      if(red):
          foodGrid = gameState.getRedFood()
      else:
          foodGrid = gameState.getBlueFood()
          
      
      minDistance = 1e10
      totalDistance = 0
      for i in range(foodGrid.width):
          for j in range(foodGrid.height):
              if(foodGrid[i][j]):
                  distance = self.distancer.getDistance(ourPos, (i,j))
                  totalDistance += distance
                  if(distance < minDistance):
                      minDistance = distance
      
      return (minDistance, totalDistance)
  
  """
  Returns the net distance between our agents
  """
  def distanceApart(self, gameState):
      ourPos = gameState.getAgentPosition(self.index)
      if(ourPos == None): #if we can't find ourself, it is time to panic
          return -1
      
      if(self.isRed):
          agents = gameState.getRedTeamIndices()
      else:
          agents = gameState.getBlueTeamIndices()
      
      totalDist = 0
      
      for agentIndex in agents:
          if(agentIndex != self.index):
              agentPos = gameState.getAgentPosition(agentIndex)
              if(agentPos == None):
                  continue # we can't deal with it
              totalDist += self.inferenceModule.distancer.getDistance(ourPos, agentPos)
              
      return totalDist
  
  def distanceToEnemies(self, gameState):
      ourPos = gameState.getAgentPosition(self.index)
      if(ourPos == None): #if we can't find ourself, it is time to panic
          return -1
      
      if(self.isRed):
          agents = gameState.getBlueTeamIndices()
      else:
          agents = gameState.getRedTeamIndices()
      
      totalDist = 0
      
      for agentIndex in agents:
          if(agentIndex != self.index):
              agentPos = gameState.getAgentPosition(agentIndex)
              if(agentPos == None):
                  totalDist += 5
              else:
                  totalDist += self.inferenceModule.distancer.getDistance(ourPos, agentPos)
              
      return totalDist
  
  def nearestCapsule(self, gameState):
      ourPos = gameState.getAgentPosition(self.index)
      if(ourPos == None):
          return -1
      
      if(self.isRed):
          capsules = gameState.getBlueCapsules()
      else:
          capsules = gameState.getRedCapsules()
          
      if(len(capsules) == 0):
          return 0
          
      minDist = 1e10
      
      for capsule in capsules:
          distToCapsule = self.inferenceModule.distancer.getDistance(ourPos, capsule)
          if(distToCapsule < minDist):
              minDist = distToCapsule
      
      return minDist
  
  def trappedPenalty(self, gameState):
      ourPos = gameState.getAgentPosition(self.index)
      if(ourPos == None):
          return -1
      
      if(self.isRed):
          agents = gameState.getBlueTeamIndices()
      else:
          agents = gameState.getRedTeamIndices()
      
      minVal = 0
      
      for agentIndex in agents:
          if(agentIndex != self.index):
              agentPos = gameState.getAgentPosition(agentIndex)
              if(agentPos != None):
                  canTrap = self.cellLayout.canTrap(agentPos, ourPos, 2)
                  if(canTrap[0]):
                      curVal = -10.0/float(len(canTrap[1])) # we are less trapped if it is a bigger space we are trapped in
                      if(curVal < minVal):
                          minVal = curVal
                  
      return minVal
      
      

