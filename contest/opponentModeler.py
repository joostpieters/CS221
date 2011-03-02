import capture
import ourAgent
import util
class opponentModel():
  def __init__(self,inferenceModel):
    self.iModel = inferenceModel
  
  def updatePositionsBasedOnSensor(self, gameState,ourAgentPos):
    agentdistances = gameState.getAgentDistances()
    for enemy in self.iModel.enemypositions: #this is iterating over the keys to a map
      if gameState.getAgentPosition(enemy):
        self.iModel.enemypositions[enemy] = util.Counter()
        self.iModel.enemypositions[enemy][gameState.getAgentPosition(enemy)] = 1
      else:
        observeddistance = agentdistances[enemy]
        for pos in self.iModel.enemypositions[enemy]:
          if capture.SIGHT_RANGE < util.manhattanDistance(pos,ourAgentPos):
            self.iModel.enemypositions[enemy][pos] = self.iModel.enemypositions[enemy][pos] * gameState.getDistanceProb(util.manhattanDistance(ourAgentPos,pos), observeddistance)
          else:
            self.iModel.enemypositions[enemy][pos] = 0
#          self.enemypositions[enemy] = self.enemypositions[enemy] * gameState.getDistanceProb(1, observeddistance)
      self.iModel.enemypositions[enemy].normalize()

  def updateBasedOnMovement(self, agentIndex, gameState): #currently this just assumes our opponents are wandering drunkenly.  Might improve that. Further doesn't reset them based on if they were captured.
    self.iModel.posterior = util.Counter()
    for position in self.iModel.enemypositions[agentIndex]:
      neighbors = []
      for p in self.iModel.legalPositions:  #we might consider optimizing this, but it should be ok.  Right now the process is O(n^2), could be O(n), but its the exponentials that kill ya.
        if util.manhattanDistance(p, position) <=1:
          neighbors.append(p)

      for neighbor in neighbors:
        self.iModel.posterior[neighbor] =  self.iModel.posterior[neighbor] + (self.iModel.enemypositions[agentIndex][position]/float(len(neighbors)))
    self.iModel.enemypositions[agentIndex] = self.iModel.posterior
