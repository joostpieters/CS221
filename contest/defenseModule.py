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
      print action
      newState=gameState.generateSuccessor(self.index,action)
      if not self.inferenceModule.isOnOurSide(self.whereAreWe(newState)):
        continue
      actionranking = self.evaluateBoard(newState)
      print "action " + str(action) + " gives utility " + str(actionranking)
      if actionranking>bestranking:
        bestaction = action
        bestranking = actionranking
    import random
    if random.random()<.1:
      return action

    print "For best action " + str(bestaction) + " we do utility " + str(action)
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
  
  def getMinDistanceToEachSquare(self,ourpositions,squares,isUs):
    distances = []
    for border in squares:
      if not isUs:
      	distances.append(min([self.getMazeDistance(border,p) for p in ourpositions]))
      else:
        distances.append(min([self.getOurSideMazeDistance(border,p) for p in ourpositions]))
    return distances

  def getAvgDistanceToEachSquare(self,ourpositions,squares,isUs):
    distances = []
    for border in squares:
      if not isUs:
        distances.append(avg([self.getMazeDistance(border,p) for p in ourpositions]))
      else:
        distances.append(avg([self.getOurSideMazeDistance(border,p) for p in ourpositions]))
    return distances

  def getMaxDelta(self, ourD, theirD):
    violations=[]
    for i in range(len(ourD)):
      violations.append(ourD[i]-theirD[i])
    return max(violations)
  
  def getAvgDelta(self, ourD, theirD):
    return avg(ourD)-avg(theirD)
  
  def getAverageDistance(self, ourpositions, enemypositions):
    totaldistance = 0
    for p in ourpositions:
     for enemyp in enemypositions:
       totaldistance += self.getOurSideMazeDistance(p,enemyp)
    return totaldistance / float(len(ourpositions)*len(enemypositions))

  def evaluateBoard(self, gameState):
    enemyPositions = self.inferenceModule.getEnemyMLEs().values()
    enemyAttackers =[pos for pos in enemyPositions if self.inferenceModule.isOnOurSide(pos)] 
    ourPositions = [gameState.getAgentPosition(index) for index in self.friends]
    
    for ourP in ourPositions:
      for enemyP in enemyPositions:
        if ourP == enemyP:
          return 1e10
    
    ourMinDistances = self.getMinDistanceToEachSquare(ourPositions, self.getOurFood(gameState),True)
    theirMinDistances = self.getMinDistanceToEachSquare(enemyPositions, self.getOurFood(gameState),False)
    ourAvgDistances = self.getAvgDistanceToEachSquare(ourPositions, self.getOurFood(gameState),True)
    theirAvgDistances = self.getAvgDistanceToEachSquare(enemyPositions, self.getOurFood(gameState),False)

    maxMinViolation = self.getMaxDelta(ourMinDistances, theirMinDistances)
    maxMinViolationOrZero = max(maxMinViolation, 0)

    print maxMinViolationOrZero

    maxAvgViolation = self.getMaxDelta(ourAvgDistances, theirAvgDistances)
    avgMinViolations = self.getAvgDelta(ourMinDistances, theirMinDistances)
    avgAvgViolation = self.getAvgDelta(ourAvgDistances, theirAvgDistances)

    averageOurSideDistanceBetweenGhosts = self.getAverageDistance(ourPositions,enemyAttackers)

    

    protectionViolation =  maxMinViolationOrZero*8 + maxMinViolation + maxAvgViolation+avgMinViolations+avgAvgViolation
    threatToThemViolation =  6*averageOurSideDistanceBetweenGhosts

    return -threatToThemViolation-protectionViolation
  def showListofPositions(self, list):
    weights = util.Counter()
    for pos in list:
      weights[pos] = 1
    weights.normalize()
    self.displayDistributionsOverPositions([weights])
