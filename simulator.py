import sys
import random
import time

class UserNode :

    def __init__(self, userID) :
        self.userID = userID
        self.followers = []
        self.active = -1
        self.activate = False
        self.thr = float(random.randint(1,10))/100.
        self.nfollowing = 0
        self.influenced = 0
        self.prob = float(random.randint(99,100))/100.

    def setActivate(self, activate) :
        if self.active == -1:
            self.activate = activate

    def setActiveTime(self, timestep) :
        self.active = timestep

    def isActive(self) :
        return self.active

    def willActivate(self) :
        return self.activate

    def addFollowing(self) :
        self.nfollowing += 1

    def influence(self) :
        self.influenced += 1

    def changedMind(self) :
        if self.active > -1:
            return False
        if self.nfollowing != 0 :
            return (float(self.influenced) / float(self.nfollowing)) > self.thr


class SimulatorFrame :

    def __init__(self) :
        self.timestep = 0
        self.nodelist = {}
        self.newActives = []
        self.lastsize = -1
        self.thissize = 0

    def addNode(self, nodeID) :
        newnode = UserNode(nodeID)
        self.nodelist[nodeID] = newnode
        return newnode

    def makeActive(self, userID) :
        self.newActives.append(userID)
        self.nodelist[userID].active = 0

    def readStructure(self, structureFile) :

        # reads user IDs and counts lines in file
        print "\tReading User IDs..."
        linecount = 0
        f = open(structureFile)
        for line in f:
            userLine = line.split()
            newnode = self.addNode(int(userLine[0].rstrip(':')))
            linecount += 1
            if linecount % 1000 == 0:
                print "\t\t" + str(linecount) + " Users Read"
        f.close()
        print "\tStructure Contains " + str(linecount) + " Users"


        f = open(structureFile)
        edgecount = 0
        print "\tReading Edges..."
        for line in f:  
            for user in userLine[1:]:
                try:
                    self.nodelist[int(user)]
                except:
                    continue
                newnode.followers.append(int(user))
                edgecount += 1
            if edgecount % 10000 == 0:
                print "\t\t" + str(edgecount) + " Edges Read"
        f.close()
        print "\tStructure Contains " + str(edgecount) + " Edges"



        # reads follower lists
        print "\tCounting Follower Lists..."
        print "\t\t0 / " + str(linecount)
        count = 0
        f = open(structureFile)
        for node in self.nodelist.values():
            count += 1
            if count % 1000 == 0:
                print "\t\t" + str(count) + " / " + str(linecount)
            for othernode in node.followers:
                try:
                    self.nodelist[othernode]
                except:
                    continue
                self.nodelist[othernode].addFollowing()

    def activeCount(self) :
        nActive = 0
        for node in self.nodelist.values():
            if node.isActive() > -1:
                nActive += 1
            self.lastsize = self.thissize
            self.thissize = nActive
        return nActive


    def activeStep(self) :
        for node in self.nodelist.values():
            if node.willActivate() == True:
                node.setActivate(False)
                node.setActiveTime(self.timestep)


    def lin_thr_step(self) :
        for node in self.newActives:
            print 'Node ' + str(node)
            for follower in self.nodelist[node].followers:
                print "Influencing follower " + str(follower.userid)
                self.nodelist[follower].influence()
        self.newActives = []
        for node in self.nodelist.values():
            if node.changedMind():
                self.newActives.append(node.userID)
                node.setActivate(True)

    def ind_cscd_step(self) :
        nextActives = []
        for node in self.newActives:
            for follower in self.nodelist[node].followers:
                roll = random.random()
                if roll < self.nodelist[node].prob:
                    self.nodelist[follower].setActivate(True)
                    nextActives.append(follower)
        self.newActives = nextActives
        

    def simulateStep(self, time) :
        self.timestep = time
#        self.ind_cscd_step()
        self.lin_thr_step()
        self.activeStep()


    def printResults(self, filename) :
        f = open(filename, 'w')
        for node in self.nodelist.values():
            f.write(str(node.userID) + "\t" + str(node.isActive()) + "\n")

# Main Function



usage = "Usage: python simulator.py structureFile saveFile nIters nSeeds"

if len(sys.argv) != 5:
    print usage 
    exit()

structFile = sys.argv[1]
nIters = int(sys.argv[3])
nSeeds = int(sys.argv[4])


###############################################################################


sim = SimulatorFrame()
print "Reading Structure from file: " + structFile
sim.readStructure(structFile)

starttime = time.time()

print "Beginning Simulation with " + str(nSeeds) + " Seed Nodes..."
for i in range(0, nSeeds):
    seedNode = sim.nodelist.values()[random.randint(0,len(sim.nodelist)-1)]
    sim.makeActive(seedNode.userID)
#for i in range(0, nSeeds - 1):
#    if seedNode.followers[i] in sim.nodelist:
#        sim.makeActive(sim.nodelist[seedNode.followers[i]].userID)
#    else:
#        nSeeds += 1

for timestep in range(1,nIters + 1) :
    sim.simulateStep(timestep)
    if timestep % 5 == 0:
        nActive = sim.activeCount()
        nNodes = len(sim.nodelist)
        print "Timestep " + str(timestep) + ":  " + str(nActive) \
              + " / " + str(nNodes) + "  Nodes Active"
        if nActive == nNodes or sim.lastsize == sim.thissize:
            break

print "Printing Results to " + sys.argv[2] + "..."
sim.printResults(sys.argv[2])
print "Simulation Complete!"

runtime = int((time.time()) - starttime)
sec = str(runtime % 60)
mins = str(int(runtime / 60) % 60)
hrs = str(int(runtime / 3600))

print "Simulation Time: " + hrs + " hours  " \
      + mins + " minutes  " + sec + " seconds"

##############################################################################

