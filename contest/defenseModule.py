import capture
import module
def avg(list):
  return float(sum(list)) / len(list)

class defenseModule(module.agentModule):
  def chooseAction(self, gameState, defensiveMatching,attackingEnemies):
    actions = gameState.getLegalActions(self.index)

    bestaction = None
    bestranking = -1e10
    besttiebreaker = -1e10
    enemyPositions = self.inferenceModule.getEnemyMLEs().values()
    for action in actions:
      newState=gameState.generateSuccessor(self.index,action)
      if not self.inferenceModule.isOnOurSide(self.whereAreWe(newState)):
        continue
      actionranking = self.evaluateBoard([newState.getAgentPosition(p) for p in defensiveMatching],self.getOurFood(newState), self.inferenceModule.getEnemyMLEs().values())
      if actionranking>bestranking:
        bestaction = action
        bestranking = actionranking

    #print "For best action " + str(bestaction) + " we do utility " + str(action)
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
  
  def getAverageMinDistance(self, ourpositions, enemypositions):
    totaldistance = 0
    for p in ourpositions:
     totaldistance += min([self.getOurSideMazeDistance(p,enemyp) for enemyp in enemypositions])
    return totaldistance / float(len(ourpositions))
 
  def getNumWhereWeAreCloser(self,ourD, theirD):
    total = 0
    for i in range(len(ourD)):
      if ourD[i]<theirD[i]:
        total+=1
    return total 

  def evaluateBoard(self, ourPositions, ourFood,enemyPositions):
    enemyAttackers =[pos for pos in enemyPositions if self.inferenceModule.isOnOurSide(pos)] 
    for ourP in ourPositions:
      for enemyP in enemyPositions:
        if ourP == enemyP:
          return 1e10
    
    ourMinDistances = self.getMinDistanceToEachSquare(ourPositions, ourFood,True)
    theirMinDistances = self.getMinDistanceToEachSquare(enemyPositions, ourFood,False)

    numSafeFoodPleasure = self.getNumWhereWeAreCloser(ourMinDistances,theirMinDistances)

    ourAvgDistances = self.getAvgDistanceToEachSquare(ourPositions, ourFood,True)

    maxMinViolation = self.getMaxDelta(ourMinDistances, theirMinDistances)
    maxMinViolationOrZero = max(maxMinViolation, 0)


    avgMinViolations = self.getAvgDelta(ourMinDistances, theirMinDistances)

    averageOurSideDistanceBetweenGhosts = self.getAverageMinDistance(ourPositions,enemyAttackers)

    protectionViolation =  maxMinViolationOrZero*10 + 2*maxMinViolation + avgMinViolations + .3 * avg(ourAvgDistances)

    threatToThemViolation =  13*averageOurSideDistanceBetweenGhosts

#    return -protectionViolation
    return -threatToThemViolation
    return numSafeFoodPleasure-threatToThemViolation-protectionViolation
  def showListofPositions(self, list):
    weights = util.Counter()
    for pos in list:
      weights[pos] = 1
    weights.normalize()
    self.displayDistributionsOverPositions([weights])
