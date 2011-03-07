import module
from module import agentModule
import minimaxModule
from minimaxModule import MinimaxModule
import random
import time

class AttackModule(agentModule, minimaxModule.MinimaxModuleDelegate):

  def chooseAction(self, gameState):
      minimaxMod = MinimaxModule(self)
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
      foodDistances = self.distanceToFood(gameState, False) if self.isRed else self.distanceToFood(gameState, True)
      nearestFoodVal = self.heuristicWeights['attackModule_nearestFoodCoeff'] * pow(foodDistances[0], self.heuristicWeights['attackModule_nearestFoodPower'])
      totalFoodVal = self.heuristicWeights['attackModule_totalFoodCoeff'] * foodDistances[1]
      foodCount = self.getFoodCount(gameState, False) if self.isRed else self.getFoodCount(gameState, True)
      numFoodsVal = self.heuristicWeights['attackModule_foodEatenReward'] * (20 - self.getFoodCount(gameState, False))
      distanceApartVal = self.heuristicWeights['attackModule_distanceApartReward'] * self.distanceApart(gameState)
      enemyDistanceVal = self.heuristicWeights['attackModule_distanceToEnemies'] * self.distanceToEnemies(gameState)
      return numFoodsVal - nearestFoodVal - totalFoodVal + distanceApartVal + enemyDistanceVal
            
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

