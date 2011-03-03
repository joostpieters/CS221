import capture
import module
def avg(list):
  return float(sum(list)) / len(list)
class defenseModule(module.agentModule):
  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)

    bestaction = None
    bestranking = -1e10
    besttiebreaker = -1e10
    enemyPositions = self.inferenceModule.getEnemyMLEs().values()
    for action in actions:
      newState=gameState.generateSuccessor(self.index,action)
      if not self.inferenceModule.isOnOurSide(self.whereAreWe(newState)):
        continue
      actionranking = self.evaluateBoard(newState)
      if actionranking>bestranking:
        bestaction = action
        bestranking = actionranking
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
  
  def getMinDistanceToEachSquare(self,ourpositions,squares):
    distances = []
    for border in squares:
      distances.append(min([self.getMazeDistance(border,p) for p in ourpositions]))
    return distances

  def getAvgDistanceToEachSquare(self,ourpositions,squares):
    distances = []
    for border in squares:
      distances.append(avg([self.getMazeDistance(border,p) for p in ourpositions]))
    return distances

  def getMaxDelta(self, ourD, theirD):
    violations=[]
    for i in range(len(ourD)):
      violations.append(ourD[i]-theirD[i])
    return min(violations)
  
  def getAvgDelta(self, ourD, theirD):
    return avg(ourD)-avg(theirD)

  def evaluateBoard(self, gameState):
    enemyPositions = self.inferenceModule.getEnemyMLEs().values()
      
    ourPositions = [gameState.getAgentPosition(index) for index in self.friends]
    
    for ourP in ourPositions:
      for enemyP in enemyPositions:
        if ourP == enemyP:
          return 1e10
    
    ourMinDistances = self.getMinDistanceToEachSquare(ourPositions, self.getOurFood(gameState))
    theirMinDistances = self.getMinDistanceToEachSquare(enemyPositions, self.getOurFood(gameState))
    ourAvgDistances = self.getAvgDistanceToEachSquare(ourPositions, self.getOurFood(gameState))
    theirAvgDistances = self.getAvgDistanceToEachSquare(enemyPositions, self.getOurFood(gameState))

    maxMinViolation = self.getMaxDelta(ourMinDistances, theirMinDistances)
    maxAvgViolation = self.getMaxDelta(ourAvgDistances, theirAvgDistances)
    avgMinViolations = self.getAvgDelta(ourMinDistances, theirMinDistances)
    avgAvgViolation = self.getAvgDelta(ourAvgDistances, theirAvgDistances)
     
    return maxMinViolation*3 + maxAvgViolation+avgMinViolations+avgAvgViolation

  def showListofPositions(self, list):
    weights = util.Counter()
    for pos in list:
      weights[pos] = 1
    weights.normalize()
    self.displayDistributionsOverPositions([weights])
