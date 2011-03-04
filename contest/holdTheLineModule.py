import capture
import module

class holdTheLineModule(module.agentModule):
  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)

    bestaction = None
    bestranking = -1e10
    besttiebreaker = -1e10
    for action in actions:
      newState=gameState.generateSuccessor(self.index,action)
      if not self.inferenceModule.isOnOurSide(self.whereAreWe(newState)):
        continue
      actionranking,tiebreaker = self.evaluateBoard(newState)
      if actionranking>bestranking or (actionranking==bestranking and besttiebreaker>tiebreaker):
        bestaction = action
        besttiebreaker = tiebreaker
        bestranking = actionranking

    #print 'Our action ' + str(action) + ' our score ' + str(bestranking) + ' our tiebreaker ' + str(besttiebreaker)
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
  
  def matchUp(self, theirpos, ourpos,gameState):
    return min([self.getMazeDistance(theirpos,pos) - self.getOurSideMazeDistance(ourpos,pos) for pos in self.getOurFood(gameState)+self.inferenceModule.edge])

  def findWeakestLink(self, enemyPositions, ourPositions,gameState):
    if len(enemyPositions) == 0:
      return 0
    bestvalue = -1e10
    for i in range(0,len(ourPositions)):
      newOurPos = ourPositions[:]
      newOurPos.remove(ourPositions[i]) #this is ok even if two pacmen are hanging out on same square
      thisstrat = min(self.findWeakestLink(enemyPositions[1:], newOurPos,gameState), self.matchUp(enemyPositions[0],ourPositions[i],gameState))
      if thisstrat > bestvalue:
        bestvalue = thisstrat
    return bestvalue

  def distanceToSquares(self,ourpositions,squares):
    totalcost = 0
    for border in squares:
      totalcost = totalcost + min([self.getOurSideMazeDistance(border,p) for p in ourpositions]) + sum([self.getOurSideMazeDistance(border,p) for p in ourpositions])/5.0
    return totalcost

  def evaluateBoard(self, gameState):
    enemyPositions = self.inferenceModule.getEnemyMLEs()
    ourPositions = [gameState.getAgentPosition(index) for index in self.friends]
    #return self.findWeakestLink(enemyPositions.values(), ourPositions), self.distanceToSquares(ourPositions,self.inferenceModule.edge)
    return self.findWeakestLink(enemyPositions.values(), ourPositions,gameState), self.distanceToSquares(ourPositions,self.inferenceModule.edge)

  def showListofPositions(self, list):
    weights = util.Counter()
    for pos in list:
      weights[pos] = 1
    weights.normalize()
    self.displayDistributionsOverPositions([weights])
