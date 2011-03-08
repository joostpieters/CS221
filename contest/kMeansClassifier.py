import random
import string

MAX_ITERS = 500

def distance(vec1, vec2):
  if not vec1 or not vec2:
    return 1e10

  if len(vec1) != len(vec2):
    return -1
  
  squaredD = 0
  for i in range(len(vec1)):
    squaredD += (vec1[i] - vec2[i])**2
  return squaredD**.5

def getCenter(keys, data):
  if len(keys)==0:
    return None
  runningSum = [0]*len(data[keys[0]])
  for key in keys:
    for i in range(len(runningSum)):
      runningSum[i] += data[key][i]

  for i in range(len(runningSum)):
    runningSum[i] = runningSum[i] / float(len(keys))
  return runningSum

def chooseClusterCenters(clusterElements, data):
  clusters = {}
  for cluster in clusterElements:
     clusters[cluster] = getCenter(clusterElements[cluster], data)
 
  return clusters

def chooseElements(clusters, data):
  clustersChosen = {}
  for cluster in clusters:
    clustersChosen[cluster] = ()
   
  for d in data:
    bestSeenValue = 1e10
    bestSeenCluster = None
    for cluster in clusters:
      if distance(data[d],clusters[cluster]) < bestSeenValue:
        bestSeenValue=distance(data[d],clusters[cluster])
        bestSeenCluster = cluster
    clusterContents = list(clustersChosen[bestSeenCluster])
    clusterContents.append(d)
    clustersChosen[bestSeenCluster] = tuple(clusterContents)

  return clustersChosen

def kMeans(data, k): #data is map from names to vectors, k is number of desired clusters, return is list of tuples
                     #with first element being cluster location, second element being the key values of the elements
                     #of the cluster.
  clusters = {}
  clusterElements = {}
  #choose k starting points from the data
  for key in data.keys()[:k]:
    clusters[key] = data[key]

  
  lastClusters = ''
  for i in range(MAX_ITERS):
    clusterElements = chooseElements(clusters, data)
    if str(clusterElements) == lastClusters:
      return clusters, clusterElements
    lastClusters = str(clusterElements)
    clusters = chooseClusterCenters(clusterElements, data)
  return clusters, clusterElements
def main():
   data = {}
   for i in range(100):
     data[''.join(random.choice(string.letters) for i in xrange(6))] = (random.random(), random.random())
   clusters, clusterElements =  kMeans(data,80)
   print clusters
   print clusterElements

if __name__ == "__main__":
  main()
