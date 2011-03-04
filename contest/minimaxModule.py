import capture
import game
import time
from util import Queue

class MinimaxModuleDelegate:
    
  def getStateValue(self, gameState):
      return 0

"""
A self-expanding node for a minimax tree
"""
class MinimaxNode:
  def __init__(self, gameState, agentIndex, delegate, action = None):
      self.state = gameState
      self.index = agentIndex
      self.delegate = delegate
      self.action = action
      self.value = self.delegate.getStateValue(gameState)
      self.children = []
      
  def expand(self):
      if(len(self.children) == 0): #only expand if we haven't already
          nextIndex = (self.index + 1) % self.state.getNumAgents()
          if(self.state.getAgentPosition(self.index) == None): #if we don't know how to expand the state at the given 
              self.children.append(MinimaxNode(self.state, nextIndex, self.delegate, None))
          else:
              actions = self.state.getLegalActions(self.index)
              for action in actions:
                  nextState = self.getSuccessor(self.state, action)
                  self.children.append(MinimaxNode(nextState, nextIndex, self.delegate, action))
    
  def calculateMinimaxValue(self, isRed):
      if(len(self.children) <= 0):
          return self.value
      minimaxValues = [child.calculateMinimaxValue(isRed) for child in self.children]
      takeMax = True
      if ((isRed and self.index in self.state.getBlueTeamIndices()) or ((not isRed) and self.index in self.state.getRedTeamIndices())):
          takeMax = False
      if(takeMax):
          return max(minimaxValues)
      else:
          return min(minimaxValues)

  def getSuccessor(self, gameState, action):
    """
    Convenience method to return the successor state from an action
    """
    successor = gameState.generateSuccessor(self.index, action)
    return successor

"""
A class that handles running minimax
"""
class MinimaxModule:
  
  def __init__(self, delegate):
      self.delegate = delegate

  """
  For a given game state, this hands back the action-value minimax calculated
  pairs in the form (action, value)
  """
  def getMinimaxValues(self, gameState, agentIndex, isRed, expandTimeout):
      startTime = time.time()
      print("Expanding nodes...")
      
      # two queues to deepen minimax
      curExpand = Queue()
      nextExpand = Queue()
      
      # create and enqueue the first node
      rootNode = MinimaxNode(gameState, agentIndex, self.delegate)
      curExpand.push(rootNode)
      nodesExpanded = 1
      
      # bfs expanding nodes
      while(True):
          while(not curExpand.isEmpty()):
              toExpand = curExpand.pop()
              toExpand.expand()
              for child in toExpand.children:
                  nextExpand.push(child)
                  nodesExpanded += 1
              if(time.time() - startTime > expandTimeout):
                  break
          if(time.time() - startTime > expandTimeout):
              break
          curExpand = nextExpand
          nextExpand = Queue()
      
      timeTaken = time.time() - startTime
      print("Expanded " + str(nodesExpanded) + " nodes in " + str(timeTaken) + " seconds.")
      
      print("Calculating Minimax values...")
      minimaxStartTime = time.time()
      minimaxValues = []
      
      for childNode in rootNode.children:
          mmaxValue = childNode.calculateMinimaxValue(isRed)
          minimaxValues.append((childNode.action, mmaxValue))
      
      minimaxTimeTaken = time.time() - minimaxStartTime
      print("Calculated Minimax in " + str(minimaxTimeTaken) + " seconds.")
      
      return minimaxValues
