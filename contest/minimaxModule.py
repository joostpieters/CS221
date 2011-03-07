import capture
import game
import time
from util import Queue

DETECT_CYCLES = True
PRINTDEBUG = True

class MinimaxModuleDelegate:
    
  def getStateValue(self, gameState):
      return 0

"""
A self-expanding node for a minimax tree
"""
class MinimaxNode:
  def __init__(self, parent, gameState, agentIndex, delegate, ignoreIndices, action = None):
      self.parent = parent
      self.state = gameState
      self.index = agentIndex
      self.delegate = delegate
      self.action = action
      self.ignoreIndices = ignoreIndices
      self.value = self.delegate.getStateValue(gameState)
      self.children = []
      
  def expand(self):
      if(len(self.children) == 0): #only expand if we haven't already
          if(DETECT_CYCLES):
              curNode = self.parent
              cycle = False
              for i in range(2 * self.state.getNumAgents()):
                  if(not DETECT_CYCLES or curNode == None):
                      break
                  curNode = curNode.parent
              if(curNode != None):
                  redIndex = (self.index in self.state.getRedTeamIndices())
                  curNodeFood = curNode.state.getBlueFood() if redIndex else curNode.state.getRedFood()
                  selfNodeFood = self.state.getBlueFood() if redIndex else curNode.state.getRedFood()
                  if(curNode.state.getAgentPosition(self.index) == self.state.getAgentPosition(self.index) and curNodeFood == selfNodeFood):
                      cycle = True
          if(not (DETECT_CYCLES and cycle)): # don't expand cyclic graphs
              numAgents = self.state.getNumAgents()
              nextIndex = (self.index + 1) % numAgents
              while(nextIndex in self.ignoreIndices):
                  if(nextIndex == self.index): break # avoid infinite loops
                  nextIndex = (nextIndex + 1) % numAgents
              if(self.state.getAgentPosition(self.index) == None): #if we don't know how to expand the state at the given 
                  self.children.append(MinimaxNode(self, self.state, nextIndex, self.delegate, self.ignoreIndices, None))
              else:
                  actions = self.state.getLegalActions(self.index)
                  for action in actions:
                      nextState = self.getSuccessor(self.state, action)
                      self.children.append(MinimaxNode(self, nextState, nextIndex, self.delegate, self.ignoreIndices, action))
    
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
  
  def __init__(self, delegate, ignoreIndices = []):
      self.delegate = delegate
      self.ignoreIndices = ignoreIndices

  """
  For a given game state, this hands back the action-value minimax calculated
  pairs in the form (action, value)
  """
  def getMinimaxValues(self, gameState, agentIndex, isRed, expandTimeout):
      startTime = time.time()
      if(PRINTDEBUG): print("Expanding nodes...")
      
      # two queues to deepen minimax
      curExpand = Queue()
      nextExpand = Queue()
      
      # create and enqueue the first node
      rootNode = MinimaxNode(None, gameState, agentIndex, self.delegate, self.ignoreIndices)
      curExpand.push(rootNode)
      nodesExpanded = 1
      depthExpanded = 0
      
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
          depthExpanded += 1
          curExpand = nextExpand
          nextExpand = Queue()
      
      timeTaken = time.time() - startTime
      if(PRINTDEBUG): print("Expanded " + str(nodesExpanded) + " nodes to a depth of " + str(depthExpanded) + "in " + str(timeTaken) + " seconds.")
      
      if(PRINTDEBUG): print("Calculating Minimax values...")
      minimaxStartTime = time.time()
      minimaxValues = []
      
      for childNode in rootNode.children:
          mmaxValue = childNode.calculateMinimaxValue(isRed)
          minimaxValues.append((childNode.action, mmaxValue))
      
      minimaxTimeTaken = time.time() - minimaxStartTime
      if(PRINTDEBUG): print("Calculated Minimax in " + str(minimaxTimeTaken) + " seconds.")
      
      return minimaxValues
