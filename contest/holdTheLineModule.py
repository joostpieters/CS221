import capture
import module

def secondMin(list):
  try:
    return sorted(list)[1]
  except:
    return 0

class holdTheLineModule(module.agentModule):
  def chooseAction(self, gameState, ourIndices,ourEnemies):
    actions = gameState.getLegalActions(self.index)

    bestaction = None
    bestranking = -1e10
    for action in actions:
      newState=gameState.generateSuccessor(self.index,action)
      if not self.inferenceModule.isOnOurSide(self.whereAreWe(newState)):
        continue
      actionranking = self.evaluateBoard(newState, ourIndices, ourEnemies)
      if actionranking>bestranking:
        bestaction = action
        bestranking = actionranking

    #print 'Our action ' + str(action) + ' our score ' + str(bestranking)
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
  
  def maxMinDistanceToSquares(self, ourpositions, squares):
    currentworst = -1e10
    for square in squares:
      thissquarevalue = min([self.getOurSideMazeDistance(square,p) for p in ourpositions])
      if thissquarevalue>currentworst:
        currentworst =thissquarevalue 
    return currentworst
 
  def getMinDistanceToSquares(self,agentPositions, squares,isUs):
    distances = []
    for square in squares: 
      if isUs:
        distances.append(min([self.getOurSideMazeDistance(square,p) for p in agentPositions]))
      else:
        distances.append(min([self.getMazeDistance(square,p) for p in agentPositions]))
    return distances
  
  def getSecondMinDistanceToSquares(self,agentPositions, squares,isUs):
    distances = []
    for square in squares:
      if isUs:
        distances.append(secondMin([self.getOurSideMazeDistance(square,p) for p in agentPositions]))
      else:
        distances.append(secondMin([self.getMazeDistance(square,p) for p in agentPositions]))
    return distances
  
  def avgDistanceToSquares(self,ourpositions,squares):
    totalcost = 0
    for border in squares:
      for p in ourpositions:
        totalcost = totalcost + self.getOurSideMazeDistance(border,p)
    return totalcost/float(len(squares)*len(ourpositions))
  
  def maxAmountWorse(self,ours, theirs):
    amountWorse = -1e10
    for i in range(len(ours)):
      thisViolation = ours[i]-theirs[i]
      if thisViolation>amountWorse:
        amountWorse =thisViolation
    return amountWorse

  def ourAvgAvgDistanceToSquares(self,ourP, squares):
    cost = 0
    for p in ourP:
      for square in squares:
        cost +=self.getOurSideMazeDistance(p, square)
    return cost / float(len(ourP)*len(squares))
 
  def averageSquaredViolation(self,ours, theirs):
    violation = 0
    for i in range(len(ours)):
      violation = violation+max(0,ours[i]-theirs[i])**2
    return violation/float(len(ours))

  def evaluateBoard(self, gameState,ourIndices,enemyPositions):
    ourPositions = [gameState.getAgentPosition(index) for index in ourIndices]

    relevantSquares = self.inferenceModule.edge # + self.getOurFood(gameState)
  
    ourAvgAvgDistanceToEdgeViolation = self.ourAvgAvgDistanceToSquares(ourPositions,relevantSquares)
    
    ourDistancesToSquares = self.getMinDistanceToSquares(ourPositions,relevantSquares,True)
    theirDistancesToSquares = self.getMinDistanceToSquares(enemyPositions,relevantSquares,False)
    
    teamavgMinDistanceToEdgeViolation = sum(ourDistancesToSquares)/len(ourDistancesToSquares)

    opponentMaxViolation = self.maxAmountWorse(ourDistancesToSquares,theirDistancesToSquares)
    opponentAverageSquaredViolation = self.averageSquaredViolation(ourDistancesToSquares,theirDistancesToSquares)

    ourSecondDistancesToSquares = self.getSecondMinDistanceToSquares(ourPositions,relevantSquares,True)
    theirSecondDistancesToSquares = self.getSecondMinDistanceToSquares(enemyPositions,relevantSquares,False)
   
    opponentSecondMaxViolation = self.maxAmountWorse(ourSecondDistancesToSquares,theirSecondDistancesToSquares) 
  
    ourMaxDistance = max(ourDistancesToSquares)

    ourAverageDistanceToSquaresViolation = self.avgDistanceToSquares(ourPositions,relevantSquares)
    return - 2*ourAverageDistanceToSquaresViolation-5*opponentMaxViolation- 2*max(0,opponentSecondMaxViolation)- ourMaxDistance-.5*teamavgMinDistanceToEdgeViolation

  def showListofPositions(self, list):
    weights = util.Counter()
    for pos in list:
      weights[pos] = 1
    weights.normalize()
    self.displayDistributionsOverPositions([weights])
