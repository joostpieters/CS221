import capture
import game
import random
import sys

PHI_P = 1
PHI_G = 1
OMEGA = 1

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


class Particle:
    
    def __init__(self, swarm):
        self.swarm = swarm
        self.optimizableDelegate = swarm.optimizableDelegate
        self.position = self.getRandomPosition()
        self.velocity = self.getRandomVelocity()
        self.bestKnown = self.position.copy()
        self.bestKnownVal = 0
        
    def getRandomPosition(self):
        pos = {}
        for key in self.optimizableDelegate.getDefaultWeights():
            min = self.optimizableDelegate.getWeightMin(key)
            max = self.optimizableDelegate.getWeightMax(key)
            newVal = random.uniform(min, max)
            pos[key] = newVal
        return pos
    
    def getRandomVelocity(self):
        vel = {}
        for key in self.position:
            min = self.optimizableDelegate.getWeightMin(key)
            max = self.optimizableDelegate.getWeightMax(key)
            speed = random.uniform(min - max, max - min)
            vel[key] = speed
        return vel
        
    def updateVelocity(self):
        rp = random.random()
        rg = random.random()
        for key in self.velocity:
            self.velocity[key] = OMEGA * self.velocity[key] + PHI_P * rp * (self.bestKnown[key] - self.position[key]) + PHI_G * rg * (self.swarm.bestKnown[key] - self.position[key])
            
    def updatePosition(self):
        for key in self.position:
            min = self.optimizableDelegate.getWeightMin(key)
            max = self.optimizableDelegate.getWeightMax(key)
            self.position[key] = self.position[key] + self.velocity[key]
            if(self.position[key] > max):
                self.position[key] = max
            if(self.position[key] < min):
                self.position[key] = min
                
        
        
        
class ParticleSwarm:
    
    def __init__(self, optimizableDelegate, numParticles, initFunction):
        self.optimizableDelegate = optimizableDelegate
        self.particles = [Particle(self) for i in range(numParticles)]
        for particle in self.particles:
            particle.bestKnownVal = initFunction(particle)
        bestVals = [p.bestKnownVal for p in self.particles]
        self.bestKnownVal = max(bestVals)
        potentialBests = [p for p in self.particles if p.bestKnownVal == self.bestKnownVal]
        self.bestKnown = potentialBests[0].bestKnown.copy()
        if(len(potentialBests) > 1):
            print "Tie in init, so set up default player as best"
            self.bestKnownVal += 100 # tiebreak, for swarm consistency
            potentialBests[0].bestKnown = optimizableDelegate.getDefaultWeights().copy()
            potentialBests[0].bestKnownVal = self.bestKnownVal
            self.bestKnown = potentialBests[0].bestKnown.copy()
        

"""
A self-expanding node for a minimax tree
"""
class ParticleSwarmOptimizer:
  def __init__(self, optimizableDelegate, numParticles, flags, fitnessFunction = None):
      self.flags = flags
      opts = capture.readCommand(flags)
      self.verbose = opts['verbose']
      self.optimizableDelegate = optimizableDelegate
      self.numParticles = numParticles
      if(fitnessFunction == None):
          self.fitnessFunction = ParticleSwarmOptimizer.fitnessBattle
          self.fitnessInitializer = lambda x: 0
      else:
          self.fitnessFunction = fitnessFunction
          self.fitnessInitializer = fitnessFunction
      self.swarm = ParticleSwarm(optimizableDelegate, numParticles, self.fitnessInitializer)
      
  def optimize(self, numIterations):
      if(self.verbose):
          print("STARTING OPTIMIZE!")
      for i in range(numIterations):
          curCount = 0
          for particle in self.swarm.particles:
              curCount += 1
              if(self.verbose): print("Currently on particle " + str(curCount) +"/" + str(len(self.swarm.particles)) + " in round " + str(i+1) + "/" + str(numIterations))
              particle.updateVelocity()
              particle.updatePosition()
              particleVal = self.fitnessFunction(self, particle)
              if(self.verbose):
                  print("Particle with velocity:")
                  print(particle.velocity)
                  print(" and position: ")
                  print(particle.position)
                  print("assigned a value of ")
                  print(particleVal)
              if(particle.bestKnownVal < particleVal):
                  particle.bestKnownVal = particleVal
                  particle.bestKnown = particle.position.copy()
                  if(self.verbose):
                      self.printBestKnown(particle)
                  if(self.swarm.bestKnownVal < particleVal):
                      self.swarm.bestKnownVal = particleVal
                      self.swarm.bestKnown = particle.position.copy()
                      if(self.verbose):
                          self.printNewSwarmBestKnown()
          if(self.verbose):
              self.printSwarmBestKnown(i)
      return self.swarm.bestKnown
              
  def printBestKnown(self, particle):
      print("====================================================================")
      print("New Particle Best Known:")
      print(particle.bestKnown)
      print("====================================================================")
              
  def printNewSwarmBestKnown(self):
      print("====================================================================")
      print("New Swarm Best Known:")
      print(self.swarm.bestKnown)
      print("====================================================================")
              
  def printSwarmBestKnown(self, i):
      print("====================================================================")
      print("====================================================================")
      print("====================================================================")
      print("After iteration " + str(i) + " we have the following best known position:")
      print(self.swarm.bestKnown)
      print("====================================================================")
      print("====================================================================")
      print("====================================================================")

  def fitnessBattle(self, particle):
      options = capture.readCommand(self.flags)
      verbose = options.pop('verbose') # pop it off since runGame can't handle it
      #options['display'] = None
      options['numGames'] = 1
      options['record'] = False
      options['numTraining'] = False
      for agent in options['agents']:
          agent.setWeights(particle.position if agent.isRed else particle.bestKnown)
      games = capture.runGames(**options)
      assert(len(games) == 1)
      if(games[0].state.data.score < 0): #Blue wins
          return particle.bestKnownVal - 1
      
      options = capture.readCommand(self.flags)
      verbose = options.pop('verbose') # pop it off since runGame can't handle it
      #options['display'] = None
      options['numGames'] = 1
      options['record'] = False
      options['numTraining'] = False
      for agent in options['agents']:
          agent.setWeights(particle.bestKnown if agent.isRed else particle.position)
      games = capture.runGames(**options)
      assert(len(games) == 1)
      if(games[0].state.data.score > 0): #Red wins
          return particle.bestKnownVal - 1
      
      bestSwarm = True
      
      options = capture.readCommand(self.flags)
      verbose = options.pop('verbose') # pop it off since runGame can't handle it
      #options['display'] = None
      options['numGames'] = 1
      options['record'] = False
      options['numTraining'] = 0
      for agent in options['agents']:
          agent.setWeights(particle.position if agent.isRed else particle.swarm.bestKnown)
      games = capture.runGames(**options)
      assert(len(games) == 1)
      if(games[0].state.data.score < 0): #Blue wins
          return particle.swarm.bestKnownVal
      
      options = capture.readCommand(self.flags)
      verbose = options.pop('verbose') # pop it off since runGame can't handle it
      #options['display'] = None
      options['numGames'] = 1
      options['record'] = False
      options['numTraining'] = 0
      for agent in options['agents']:
          agent.setWeights(particle.swarm.bestKnown if agent.isRed else particle.position)
      games = capture.runGames(**options)
      assert(len(games) == 1)
      if(games[0].state.data.score > 0): #Red wins
          return particle.swarm.bestKnownVal
          
      return particle.swarm.bestKnownVal + 20
      
          
if __name__ == '__main__':
    """
    Run this like you were running capture.py at the command line
    
    Important Flags to know:
    -n 4 # run 4 iterations
    -x 12 # with 12 particles
    -v # in verbose mode
    """
    flags = sys.argv[1:]
    options = capture.readCommand(flags)
    agents = options['agents']
    assert(len(agents) > 0)
    optimizableDelegate = agents[0]
    numIterations = options['numGames']
    numParticles = options['numTraining']
    verbose = options.pop('verbose')
    if(verbose):
        print("Calling swarm optimizer with numIterations = " + str(numIterations) + " numParticles = " + str(numParticles))
    optimizer = ParticleSwarmOptimizer(optimizableDelegate, numParticles, flags)
    bestValues = optimizer.optimize(numIterations)
    print("Best Values = ")
    print(bestValues)
    
    
    
    
    
      
          
          