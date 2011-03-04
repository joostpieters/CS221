class agentModule():
  def __init__(self, friends, enemies, isRed, index,inferenceModule,distancer=None):
    self.friends=friends
    self.enemies=enemies
    self.isRed=isRed
    self.index=index
    self.distancer = distancer
    self.inferenceModule = inferenceModule

  def getOurFood(self,gameState):
    if self.isRed:
      return gameState.getRedFood().asList(True)
    return gameState.getBlueFood().asList(True)

  def whereAreWe(self, gameState):
    return gameState.getAgentState(self.index).getPosition()

  def getOurSideMazeDistance(self, posa, posb):
    return self.inferenceModule.ourSideDistancer.getDistance(posa,posb)

  def getMazeDistance(self,posa,posb):
    return self.distancer.getDistance(posa,posb)
 
  def getWhoMovedLast(self, gameState): #this is buggy since we might be first to move.    
    return (self.index-1) % (len(self.friends) + len(self.enemies))

  def chooseAction(self,gameState):
    return gameState.getLegalActions(self.index)[0]
