import game
from game import Grid

DEBUG = True
PRINTDEBUG = False

class LayoutNode:
    def __init__(self, pos):
        self.positions = [pos]
        self.neighbors = []
    
    def __hash__(self):
        if(len(self.positions) == 0): return 0
        return hash(self.positions[0]) #since each graph will have a position in only one node this should work
        
    def __len__(self):
        if(self.positions == None):
            return 0
        return len(self.positions)
    
    def __str__(self):
        return str(self.positions)
    
    def getNeighbors(self):
        return self.neighbors
    
    def getPositions(self):
        return self.positions

class CellLayout:
    def __init__(self, layout, distancer):
        self.distancer = distancer
        self.layout = layout
        self.walls = layout.walls
        onBoardPos = self.getLegalPosition()
        initialNode = LayoutNode(onBoardPos)
        self.cells = {onBoardPos: initialNode}
        self.expandGrid(initialNode)
        if(DEBUG):
            self.debugCheck()
        pivotNode = self.getBestNeighbor()
        if(PRINTDEBUG):
            print pivotNode.getPositions()
            for neighbor in pivotNode.getNeighbors():
                print neighbor.getPositions()
        # use the pivot node to contract the grid, since we can assume
        # it is either a singleton node (splitter or crossroads), in
        # which case it works like a champ or it is a double or single,
        # in which case the board is so simple it shouldn't matter anyway
        self.contractGrid(pivotNode)
        if(DEBUG):
            self.debugCheck()
        if(PRINTDEBUG):
            for cell in set(self.cells.values()):
                print cell
        
        
    # should only be ever called at the beginning, before
    # contracting.  It assumes that each node has only one
    # position.    
    def expandGrid(self, startNode):
        curPos = startNode.getPositions()[0]
        possiblePositions = [(curPos[0] + 1, curPos[1]), (curPos[0] - 1, curPos[1]), (curPos[0], curPos[1] + 1), (curPos[0], curPos[1]-1)]
        expandPositions = [pos for pos in possiblePositions if (0 <= pos[0] and pos[0] < self.walls.width and 0 <= pos[1] and pos[1] < self.walls.height and not self.walls[pos[0]][pos[1]])]
        if(PRINTDEBUG):
            print str(curPos) + " --> " + str(expandPositions)
        for nextPos in expandPositions:
            if(nextPos in self.cells):
                neighbor = self.cells[nextPos]
                if(not neighbor in startNode.getNeighbors()): # we might have looped around so don't doulbe count neighbors
                    startNode.getNeighbors().append(neighbor)
                if(not startNode in neighbor.getNeighbors()): # we might have looped around, so don't double count neighbors
                    neighbor.getNeighbors().append(startNode)
            else:
                neighbor = LayoutNode(nextPos)
                self.cells[nextPos] = neighbor
                self.expandGrid(neighbor)
     
    # looks at the dict of cells and returns the
    # cell with the most neighbors            
    def getBestNeighbor(self):
        nodes = self.cells.values()
        if(nodes == None or len(nodes) <= 0):
            return None
        maxNeighbor = nodes[0]
        maxLen = len(maxNeighbor.getNeighbors())
        for node in nodes:
            curLen = len(node.getNeighbors())
            if(curLen > maxLen):
                maxLen = curLen
                maxNeighbor = node
        return maxNeighbor
                
    def contractGrid(self, pivotNode):
        contractedNodes = set([])
        self.contractNodesRec(pivotNode, contractedNodes)
        
    def contractNodesRec(self, startNode, alreadyContracted):
        if startNode in alreadyContracted or len(startNode.getNeighbors()) == 0:
            return
        if( len(startNode.getNeighbors()) > 2):
            alreadyContracted.add(startNode)
            for neighbor in startNode.getNeighbors():
                self.contractNodesRec(neighbor, alreadyContracted)
            return
        # if we get here, we know we are in a pipe or dead-end
        contractors = [x for x in startNode.getNeighbors() if len(x.getNeighbors()) <= 2]
        if( len(contractors) == 0 ):
            alreadyContracted.add(startNode)
            for neighbor in startNode.getNeighbors():
                self.contractNodesRec(neighbor, alreadyContracted)
            return
        # if we get here, we know we can contract
        cur = startNode
        next = contractors[0] #choose a direction to contract
        while(len(next.getNeighbors()) <= 2):
            cur.getNeighbors().remove(next)
            next.getNeighbors().remove(cur)
            assert(len(next.getNeighbors()) <= 1)
            cur.getPositions().extend(next.getPositions())
            for pos in next.getPositions():
                self.cells[pos] = cur
            if(len(next.getNeighbors()) == 0):
                break
            nextnext = next.getNeighbors()[0]
            cur.getNeighbors().append(nextnext)
            nextnext.getNeighbors().remove(next)
            nextnext.getNeighbors().append(cur)
            next = nextnext
        self.contractNodesRec(startNode, alreadyContracted)
        
    
    def getLegalPosition(self):
        positions = self.layout.agentPositions
        if(len(positions) > 0):
            return positions[0][1]
        walls = self.layout.walls
        for i in range(walls.width):
            for j in range(walls.height):
                if(not walls[i][j]):
                    return (i,j)
        return None
    
    
    # Returns whether the agent at trapperPos can trap the
    # agent at trappedPos, searching through depthToSearch
    # in the cell graph
    #
    # Returns None if you enter a position that isn't in
    # the cell graph
    #
    # If returns a pair of a boolean (whether we can trap)
    # and a list (the cells we block off containing trappedPos)
    def canTrap(self, trapperPos, trappedPos, depthToSearch):
        startNode = self.cells[trapperPos]
        endNode = self.cells[trappedPos]
        if(startNode == None or endNode == None):
            return None
        if(trapperPos == trappedPos):
            return (True, [trapperPos])
        if(startNode == endNode): #it's in our node, and isn't equal to us
            assert(len(startNode.getNeighbors()) < 3)
            if(len(startNode.getNeighbors()) <= 0):
                trapperIndex = startNode.getPositions().index(trapperPos)
                trappedIndex = startNode.getPositions().index(trappedPos)
                if(trappedIndex < trapperIndex):
                    trappedCells = startNode.getPositions()[:trapperIndex]
                else:
                    trappedCells = startNode.getPositions()[trapperIndex:]
                return (True, trappedCells)
            if(len(startNode.getNeighbors()) == 1):
                neighbor = startNode.getNeighbors()[0]
                if(len(neighbor.getPositions()) > 1):
                    return (False, []) # here we are in a loop, so it can always loop away
                neighborPos = neighbor.getPositions()[0]
                trapperDist = self.distancer.getDistance(trapperPos, neighborPos)
                trappedDist = self.distancer.getDistance(trappedPos, neighborPos)
                if(trapperDist < trappedDist):
                    trapperIndex = startNode.getPositions().index(trapperPos)
                    trappedIndex = startNode.getPositions().index(trappedPos)  
                    if(trappedIndex < trapperIndex):
                        trappedCells = startNode.getPositions()[:trapperIndex]
                    else:
                        trappedCells = startNode.getPositions()[trapperIndex:]
                    return (True, trappedCells)
                else:
                    return (False, [])
            # if we get here, we are in a two-sided pipe
            neighbor0 = startNode.getPositions()[0]
            if(len(neighbor0.getPositions()) > 1):
                return (False, []) # here we are in a loop, so it can always loop away
            neighbor0pos = neighbor0.getPositions()[0]
            trapperDist = self.distancer.getDistance(trapperPos, neighbor0pos)
            trappedDist = self.distancer.getDistance(trappedPos, neighbor0pos)
            if(trapperDist < trappedDist):
                neighbor = startNode.getPositions()[0]
            else:
                neighbor = startNode.getPositions()[1]
            blocked = set([])
            canTrap = canTrapRec(neighbor, depthToSearch, blocked)
            if(canTrap):
                blockList = [s for s in blocked]
                if(endNode in blocked):
                    return (True, blockList)
                else:
                    return (False, blockList)
            return (False, [])
        for neighbor in startNode.getNeighbors():
            blocked = set([])
            canTrap = canTrapRec(neighbor, depthToSearch, blocked)
            if(canTrap):
                blockList = [s for s in blocked]
                if(endNode in blocked):
                    return (True, blockList)
        return (False, [])
    
        
    def canTrapRec(self, startNode, depthToSearch, blockedNodes):
        if(startNode in exploredNodes):
            return True
        if(depthToSearch == 0):
            return False
        blockedNodes.add(startNode)
        for neighbor in startNode.getNeighbors():
            if(not self.canTrapRec(neighbor, depthToSearch - 1, blockedNodes)):
                return False
        return True
    
    
    def debugCheck(self):
        self.debugGrid = Grid(self.walls.width, self.walls.height, True)
        onBoardPos = self.getLegalPosition()
        curCell = self.cells[onBoardPos]
        assert(curCell != None)
        self.debugExpand(curCell)
        if(PRINTDEBUG):
            print "DEBUG GRID:"
            print self.debugGrid
            print "WALLS:"
            print self.walls
        assert(self.debugGrid == self.walls)
        for val in self.cells.values():
            for neighbor in val.getNeighbors():
                assert(val in neighbor.getNeighbors())
    
    def debugExpand(self, curCell):
        assert(len(curCell.getPositions()) > 0)
        testPos = curCell.getPositions()[0]
        if(not self.debugGrid[testPos[0]][testPos[1]]):
            return # base case -- stop if we've already expanded
        for pos in curCell.getPositions():
            self.debugGrid[pos[0]][pos[1]] = False
        for neighbor in curCell.getNeighbors():
            self.debugExpand(neighbor)
    
    