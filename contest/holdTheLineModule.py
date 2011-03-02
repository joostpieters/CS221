class holdTheLineModule(agentModule):
    weights.normalize()
    self.displayDistributionsOverPositions([weights])

  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)

    #draw me a picture
    if self.isRed:
      self.displayDistributionsOverPositions(self.inferenceModule.enemypositions.values())

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

    print 'Our action ' + str(action) + ' our score ' + str(bestranking) + ' our tiebreaker ' + str(besttiebreaker)
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
  
    def matchUp(self, theirpos, ourpos):
    return min([self.getMazeDistance(theirpos,pos) - self.getOurSideMazeDistance(ourpos,pos) for pos in self.infer
enceModule.edge])
  def findWeakestLink(self, enemyPositions, ourPositions):
    if len(enemyPositions) == 0:
      return 1e10
    bestvalue = -1e10
    for i in range(0,len(ourPositions)):
      newOurPos = ourPositions[:]
      newOurPos.remove(ourPositions[i]) #this is ok even if two pacmen are hanging out on same square
      thisstrat = min(self.findWeakestLink(enemyPositions[1:], newOurPos), self.matchUp(enemyPositions[0],ourPosit
ions[i]))
      if thisstrat > bestvalue:
        bestvalue = thisstrat
    return bestvalue

  def distanceToEdge(self,ourpositions):
    totalcost = 0
    for border in self.inferenceModule.edge:
      totalcost = totalcost + min([self.getOurSideMazeDistance(border,p) for p in ourpositions]) + sum([self.getOu
rSideMazeDistance(border,p) for p in ourpositions])/10.0
    return totalcost

  def evaluateBoard(self, gameState):
    enemyPositions = self.inferenceModule.getEnemyMLEs()
    ourPositions = [gameState.getAgentPosition(index) for index in self.friends]
    return self.findWeakestLink(enemyPositions.values(), ourPositions), self.distanceToEdge(ourPositions)

  def showListofPositions(self, list):
    weights = util.Counter()
    for pos in list:
      weights[pos] = 1
    weights.normalize()
    self.displayDistributionsOverPositions([weights])
