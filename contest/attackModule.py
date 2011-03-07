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
      if(self.isRed):
          foodDistances = self.distanceToFood(gameState, False)
          return 100 - 5000 * self.getFoodCount(gameState, False) - pow(foodDistances[0], 2.0) - foodDistances[1] + 7 * self.distanceApart(gameState) - 100 * pow(1/self.distanceToEnemies(gameState), 2.0)
      else:
          foodDistances = self.distanceToFood(gameState, True)
          return 100 - 5000 * self.getFoodCount(gameState, True) - pow(foodDistances[0], 2.0) - foodDistances[1] + 7 * self.distanceApart(gameState), 10 - 100 * pow(1/self.distanceToEnemies(gameState), 2.0)
      
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
                  distance = self.inferenceModule.distancer.getDistance(ourPos, (i,j))
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

