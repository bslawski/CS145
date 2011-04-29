import sys
import random

class UserNode :

    def __init__(self, userID) :
        self.userID = userID
        self.followers = []
        self.active = -1
        self.activate = False
        self.thr = float(random.randint(1,81))/100.
        self.nfollowing = 0
        self.influenced = 0
        self.prob = float(random.randint(1,60))/1000.

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

    def resetInfluence(self) :
        self.influenced = 0

    def changedMind(self) :
        if self.active > -1:
            return False
        if self.nfollowing != 0 :
            return (float(self.influenced) / float(self.nfollowing)) > self.thr


class SimulatorFrame :

    def __init__(self) :
        self.timestep = 0
        self.nodelist = {}

    def addNode(self, nodeID) :
        newnode = UserNode(nodeID)
        self.nodelist[nodeID] = newnode
        return newnode

    def makeActive(self, userID) :
        self.nodelist[userID].active = 0

    def readStructure(self, structureFile) :

        # reads user IDs and counts lines in file
        print "\tReading User IDs..."
        linecount = 0
        f = open(structureFile)
        for line in f:
            userLine = line.split()
            newnode = self.addNode(int(userLine[0]))
            for user in userLine[1:]:
                newnode.followers.append(int(user))
            linecount += 1
            if linecount % 1000 == 0:
                print "\t\t" + str(linecount) + " Users Read"
        f.close()

        # reads follower lists
        print "\tReading Follower Lists..."
        print "\t\t0 / " + str(linecount)
        count = 0
        f = open(structureFile)
        for node in self.nodelist.values():
            count += 1
            if count % 1000 == 0:
                print "\t\t" + str(count) + " / " + str(linecount)
            for othernode in node.followers:
                if othernode in self.nodelist:
                    self.nodelist[othernode].addFollowing()

    def activeCount(self) :
        nActive = 0
        for node in self.nodelist.values():
            if node.isActive() > -1:
                nActive += 1
        return nActive


    def activeStep(self) :
        for node in self.nodelist.values():
            if node.willActivate() == True:
                node.setActivate(False)
                node.setActiveTime(self.timestep)


    def lin_thr_step(self) :
        for node in self.nodelist.values():
            if node.isActive() > -1:
                for follower in node.followers:
                    if follower in self.nodelist:
                        self.nodelist[follower].influence()
        for node in self.nodelist.values():
            if node.changedMind():
                node.setActivate(True)
            node.resetInfluence()

    def ind_cscd_step(self) :
        for node in self.nodelist.values():
            if node.isActive() == self.timestep - 1:
                for follower in node.followers:
                    roll = random.random()
                    if roll < node.prob:
                        if follower in self.nodelist:
                            self.nodelist[follower].setActivate(True)
        

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

sim = SimulatorFrame()
print "Reading Structure from file: " + structFile
sim.readStructure(structFile)

print "Beginning Simulation with " + str(nSeeds) + " Seed Nodes..."
seedNode = sim.nodelist.values()[random.randint(0,len(sim.nodelist)-1)]
sim.makeActive(seedNode.userID)
for i in range(0, nSeeds - 1):
    if i in sim.nodelist:
        sim.makeActive(sim.nodelist[seedNode.followers[i]].userID)
    else:
        nSeeds += 1

for time in range(1,nIters + 1) :
    sim.simulateStep(time)
    if time % 1 == 0:
        nActive = sim.activeCount()
        nNodes = len(sim.nodelist)
        print "Timestep " + str(time) + ":  " + str(nActive) \
              + " / " + str(nNodes) + "  Nodes Active"
        if nActive == nNodes:
            break

print "Printing Results to " + sys.argv[2] + "..."
sim.printResults(sys.argv[2])
print "Simulation Complete!"




