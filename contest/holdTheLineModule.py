import capture
import module

class holdTheLineModule(module.agentModule):
  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)

    bestaction = None
    bestranking = -1e10
    for action in actions:
      newState=gameState.generateSuccessor(self.index,action)
      if not self.inferenceModule.isOnOurSide(self.whereAreWe(newState)):
        continue
      actionranking = self.evaluateBoard(newState)
      if actionranking>bestranking:
        bestaction = action
        bestranking = actionranking

    print 'Our action ' + str(action) + ' our score ' + str(bestranking)
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
  
  def avgMinDistanceToSquares(self,ourpositions,squares):
    totalcost = 0
    for border in squares:
      totalcost = totalcost + min([self.getOurSideMazeDistance(border,p) for p in ourpositions])
    return totalcost/float(len(squares))

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

  def averageSquaredViolation(self,ours, theirs):
    violation = 0
    for i in range(len(ours)):
      violation = violation+max(0,ours[i]-theirs[i])**2
    return violation/float(len(ours))

  def evaluateBoard(self, gameState):
    enemyPositions = self.inferenceModule.getEnemyMLEs().values()
    ourPositions = [gameState.getAgentPosition(index) for index in self.friends]

    relevantSquares = self.inferenceModule.edge # + self.getOurFood(gameState)
  
    teamavgMinDistanceToEdgeViolation = self.avgMinDistanceToSquares(ourPositions,relevantSquares)
    
    ourDistancesToSquares = self.getMinDistanceToSquares(ourPositions,relevantSquares,True)
    theirDistancesToSquares = self.getMinDistanceToSquares(enemyPositions,relevantSquares,False)
    opponentMaxViolation = self.maxAmountWorse(ourDistancesToSquares,theirDistancesToSquares)
    opponentAverageSquaredViolation = self.averageSquaredViolation(ourDistancesToSquares,theirDistancesToSquares)

    ourAverageDistanceToSquaresViolation = self.avgDistanceToSquares(ourPositions,relevantSquares)

    print opponentAverageSquaredViolation 
    
    return   -2*opponentMaxViolation - 1*opponentAverageSquaredViolation-teamavgMinDistanceToEdgeViolation-3*max(ourDistancesToSquares) - .5*teamavgMinDistanceToEdgeViolation - .5 * ourAverageDistanceToSquaresViolation

  def showListofPositions(self, list):
    weights = util.Counter()
    for pos in list:
      weights[pos] = 1
    weights.normalize()
    self.displayDistributionsOverPositions([weights])
