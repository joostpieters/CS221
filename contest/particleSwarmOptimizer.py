import capture
import game

DETECT_CYCLES = True
PRINTDEBUG = True

class ParticleSwarmOptimizable:
  
  # Return a dictionary
  def getDefaultWeights(self):
      return {}
  
  def getWeightMin(self, weightName):
      return -10
  
  def getWeightMax(self, weightName):
      return 10
  
  def setWeights(self, weights):
      self.weights = weights

"""
A self-expanding node for a minimax tree
"""
class ParticleSwarmOptimizer:
  def __init__(self):
      print "Do Nothing here"