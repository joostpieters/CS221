# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
  """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
  """


  def getAction(self, gameState):
    """
    You do not need to change this method, but you're welcome to.

    getAction chooses among the best options according to the evaluation function.

    Just like in the previous project, getAction takes a GameState and returns
    some Directions.X for some X in the set {North, South, West, East, Stop}
    """
    # Collect legal moves and successor states
    legalMoves = gameState.getLegalActions()

    # Choose one of the best actions
    scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
    bestScore = max(scores)
    bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
    chosenIndex = random.choice(bestIndices) # Pick randomly among the best

    "Add more of your code here if you want to"

    return legalMoves[chosenIndex]

  def evaluationFunction(self, currentGameState, action):
    """
    Design a better evaluation function here.

    The evaluation function takes in the current and proposed successor
    GameStates (pacman.py) and returns a number, where higher numbers are better.

    The code below extracts some useful information from the state, like the
    remaining food (oldFood) and Pacman position after moving (newPos).
    newScaredTimes holds the number of moves that each ghost will remain
    scared because of Pacman having eaten a power pellet.

    Print out these variables to see what you're getting, then combine them
    to create a masterful evaluation function.
    """
    # Useful information you can extract from a GameState (pacman.py)
    successorGameState = currentGameState.generatePacmanSuccessor(action)
    newPos = successorGameState.getPacmanPosition()
    oldFood = currentGameState.getFood()
    newGhostStates = successorGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

    return successorGameState.getScore()
	
	
	

def scoreEvaluationFunction(currentGameState):
  """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
  """
  return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
  """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
  """

  def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
    self.index = 0 # Pacman is always agent index 0
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
  """
    Your minimax agent (question 2)
  """

  def getMinMaxAction(self, gameState, currentActor, depthtogo):
    if (currentActor == gameState.getNumAgents()) and depthtogo>1:
      return self.getMinMaxAction(gameState, 0, depthtogo-1)
    if (currentActor == gameState.getNumAgents()) and depthtogo==1:
      return [None, self.evaluationFunction(gameState)]

    actions = gameState.getLegalActions(currentActor)
    if len(actions)==0:
      return [None, self.evaluationFunction(gameState)]
    minactionvalue=float("Inf")
    maxactionvalue=float("-Inf")
    minaction = None
    maxaction = None
    for action in actions:
      [newaction, value] = self.getMinMaxAction(gameState.generateSuccessor(currentActor, action), currentActor+1, depthtogo)
      if value<minactionvalue:
        minactionvalue=value
        minaction = action
      if value>maxactionvalue:
        maxactionvalue=value
        maxaction = action

    if currentActor!=0:
      return [minaction, minactionvalue]
    else:
      return [maxaction, maxactionvalue]

  def getAction(self, gameState):
    """
      Returns the minimax action from the current gameState using self.depth
      and self.evaluationFunction.

      Here are some method calls that might be useful when implementing minimax.

      gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

      Directions.STOP:
        The stop direction, which is always legal

      gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

      gameState.getNumAgents():
        Returns the total number of agents in the game
    """
    currentActor = 0
    [action, value] = self.getMinMaxAction(gameState, currentActor, self.depth)
    print("we think value is " + str(value))
    return action
class AlphaBetaAgent(MultiAgentSearchAgent):
  """
    Your minimax agent with alpha-beta pruning (question 3)
  """
  def getMinMaxAction(self, gameState, currentActor, depthtogo, bestguarenteed, worstguarenteed):
    if (currentActor == gameState.getNumAgents()) and depthtogo>1:      
      return self.getMinMaxAction(gameState, 0, depthtogo-1,bestguarenteed, worstguarenteed)
    if (currentActor == gameState.getNumAgents()) and depthtogo==1:
      return [None, self.evaluationFunction(gameState)]

    actions = gameState.getLegalActions(currentActor)
    if len(actions)==0:
      return [None, self.evaluationFunction(gameState)]
    minactionvalue=float("Inf")
    maxactionvalue=float("-Inf")
    minaction = None
    maxaction = None
    for action in actions:
      [newaction, value] = self.getMinMaxAction(gameState.generateSuccessor(currentActor, action), currentActor+1, depthtogo,bestguarenteed, worstguarenteed)
      if (currentActor != 0 and bestguarenteed>value) or (currentActor == 0 and worstguarenteed<value):
        return [action, value]
      if value<minactionvalue:
        minactionvalue=value
        minaction = action
      if value>maxactionvalue:
        maxactionvalue=value
        maxaction = action
      if (currentActor==0 and value>bestguarenteed):
        bestguarenteed == value 
      if (currentActor!=0 and value<worstguarenteed):
        worstguarenteed == value

    if currentActor!=0:
      return [minaction, minactionvalue]
    else:
      return [maxaction, maxactionvalue]
  def getAction(self, gameState):
    """
      Returns the minimax action using self.depth and self.evaluationFunction
    """
    currentActor = 0
    bestgiven = float("-Inf")
    worstgiven = float("Inf")
    [action, value] = self.getMinMaxAction(gameState, currentActor, self.depth, bestgiven, worstgiven)
    print("we think value is " + str(value))
    return action


class ExpectimaxAgent(MultiAgentSearchAgent):
  """
    Your expectimax agent (question 4)
  """

  def getExpectiMaxAction(self, gameState, currentActor, depthtogo):
    if (currentActor == gameState.getNumAgents()) and depthtogo>1:
      return self.getExpectiMaxAction(gameState, 0, depthtogo-1)
    if (currentActor == gameState.getNumAgents()) and depthtogo==1:
      return [None, self.evaluationFunction(gameState)]

    actions = gameState.getLegalActions(currentActor)
    if len(actions)==0:
      return [None, self.evaluationFunction(gameState)]
    maxactionvalue=float("-Inf")
    maxaction = None
    runningsumofvalue = 0
    for action in actions:
      [newaction, value] = self.getExpectiMaxAction(gameState.generateSuccessor(currentActor, action), currentActor+1, depthtogo)
      runningsumofvalue = runningsumofvalue + value
      if value>maxactionvalue:
        maxactionvalue=value
        maxaction = action

    if currentActor!=0:
      return [None, runningsumofvalue/len(actions)]
    else:
      return [maxaction, maxactionvalue]

  def getAction(self, gameState):
    """
      Returns the minimax action from the current gameState using self.depth
      and self.evaluationFunction.

      Here are some method calls that might be useful when implementing minimax.

      gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

      Directions.STOP:
        The stop direction, which is always legal

      gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

      gameState.getNumAgents():
        Returns the total number of agents in the game
    """
    currentActor = 0
    [action, value] = self.getExpectiMaxAction(gameState, currentActor, self.depth)
    print("we think value is " + str(value))
    return action

def betterEvaluationFunction(currentGameState):
  """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
  """
  "*** YOUR CODE HERE ***"
  util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction

