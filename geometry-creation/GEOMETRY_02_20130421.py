import rhinoscriptsyntax as rs
import random as rd

globalDamping = 0.1


class ometrySystem(object):

    def __init__(self,SUPERSYSTEM,STARTPOINT,NUMPEAKS,SPACING,NUMLINES,PEAKINDECESI,PEAKINDECESJ,PEAKMAGNITUDES,SUBPEAKMAGNITUDES,ITERATIONS,ROTMULTI,MAXWIG,UNUSED):
        
        self.nodes = []
        self.fixedNodes = []
        self.nodeDict = {}
        self.members = []
        self.surfaces = []
        self.pipes = []
        
        
        self.SuperSystem = SUPERSYSTEM
        self.startPoint = STARTPOINT
        self.numberOfLines = NUMLINES
        self.slacklengthfactor = .4
        self.lineSpacing = SPACING
        self.numberOfPeaks = NUMPEAKS
        self.peakIndecesI = PEAKINDECESI
        self.peakIndecesJ = PEAKINDECESJ
        self.peakMagnitudes = PEAKMAGNITUDES
        self.subPeakMagnitudes = SUBPEAKMAGNITUDES
        self.iterations = ITERATIONS
        self.rotationMultiplier = ROTMULTI
        self.maxWiggle = MAXWIG
        
        self.convertInputVariables()
        self.createTopology()
        #self.boxTrim()
        #self.cleanLists()
        self.pingCorners()
        
        rs.EnableRedraw(False)
        self.relaxation()
        rs.EnableRedraw(True)
        
        for i in range(len(self.fixedNodes)):
            self.fixedNodes[i].unFix()
            #rs.AddTextDot("v",self.fixedNodes[i].guid)
        
        self.iterations = 2
        
        rs.EnableRedraw(False)
        self.relaxation()
        rs.EnableRedraw(True)
        
        self.boxTrim()
        self.cleanLists()
        
        #self.surfacing()

    def convertInputVariables(self):
        
        for i in range(len(self.peakIndecesI)):
            self.peakIndecesI[i] = int(self.peakIndecesI[i] * self.numberOfLines)
        for i in range(len(self.peakIndecesJ)):
            self.peakIndecesJ[i] = int(self.peakIndecesJ[i] * self.numberOfLines)
        for i in range(len(self.subPeakMagnitudes)):
            self.subPeakMagnitudes[i] = self.peakMagnitudes[i] * self.subPeakMagnitudes[i]

    def createTopology(self):
        
        endPt = rs.CopyObject(self.startPoint,(0,500,0))
        
        ##DRAW TEMP LINES
        startLine = rs.AddLine(self.startPoint,endPt)
        
        rs.DeleteObject(endPt)
        
        xLines = []
        
        for i in range(self.numberOfLines):
            
            transVect = rs.VectorCreate((i*self.lineSpacing,0,0),self.startPoint)  
            
            xLines.append(rs.RotateObject(rs.CopyObject(startLine,transVect),self.startPoint,-i*self.rotationMultiplier))
            
        
        tempLine1 = rs.AddLine(rs.CurveStartPoint(xLines[-1]),rs.CurveEndPoint(xLines[0]))
        tempLine2 = rs.AddLine(rs.CurveStartPoint(xLines[0]),rs.CurveEndPoint(xLines[-1]))
        
        lliRtn = rs.LineLineIntersection(tempLine1,tempLine2)
        
        moveVector = rs.VectorCreate(self.startPoint,lliRtn[0])
        
        rs.MoveObjects(xLines,moveVector)
        
        yLines = rs.RotateObjects(xLines,self.startPoint,60,None,True)
        
        rs.DeleteObject(startLine)
        rs.DeleteObject(tempLine1)
        rs.DeleteObject(tempLine2)
        
        ##CREATE NODES
        for i in range (len(xLines)):
            for j in range (len(yLines)):
                
                point = rs.AddPoint(rs.LineLineIntersection(xLines[i], yLines[j])[0])
                
                newPt = rs.CopyObject(point,(0,rd.uniform(0,self.lineSpacing * self.maxWiggle),0))
                rs.RotateObject(newPt,point,rd.uniform(0,360))
                
                rs.DeleteObject(point)
                
                node = Node(newPt)
                
                self.nodes.append(node)
                self.nodeDict[i,j] = node
                
                #rs.AddTextDot(str(i) + "," + str(j),self.nodeDict[i,j].guid)
        
        
        
        #MOVE PEAKS
        for i in range(self.numberOfPeaks):
            
            moveVect = rs.VectorCreate((0,0,self.peakMagnitudes[i]),(0,0,0))
            
            rs.MoveObject(self.nodeDict[self.peakIndecesI[i],self.peakIndecesJ[i]].guid,moveVect)
            self.nodeDict[self.peakIndecesI[i],self.peakIndecesJ[i]].makeFixed()
            self.fixedNodes.append(self.nodeDict[self.peakIndecesI[i],self.peakIndecesJ[i]])
        
        rs.DeleteObjects(xLines)
        rs.DeleteObjects(yLines)
        
        #CREATE MEMBERS
        for i in range(self.numberOfLines-1):
            for j in range(self.numberOfLines-1):
                member1 = Member(rs.AddLine(self.nodeDict[i,j].guid,self.nodeDict[i,j+1].guid),self.slacklengthfactor)
                member2 = Member(rs.AddLine(self.nodeDict[i,j].guid,self.nodeDict[i+1,j].guid),self.slacklengthfactor)
                member3 = Member(rs.AddLine(self.nodeDict[i,j].guid,self.nodeDict[i+1,j+1].guid),self.slacklengthfactor)
                
                self.members.append(member1)
                self.members.append(member2)
                self.members.append(member3)
                
                member1.addConnectedNode(self.nodeDict[i,j],"START")
                member2.addConnectedNode(self.nodeDict[i,j],"START")
                member3.addConnectedNode(self.nodeDict[i,j],"START")
                member1.addConnectedNode(self.nodeDict[i,j+1],"END")
                member2.addConnectedNode(self.nodeDict[i+1,j],"END")
                member3.addConnectedNode(self.nodeDict[i+1,j+1],"END")
                
                self.nodeDict[i,j].addConnectedMember(member1)
                self.nodeDict[i,j].addConnectedMember(member2)
                self.nodeDict[i,j].addConnectedMember(member3)
                self.nodeDict[i,j+1].addConnectedMember(member1)
                self.nodeDict[i+1,j].addConnectedMember(member2)
                self.nodeDict[i+1,j+1].addConnectedMember(member3)
        
        #LOCATE NEAREST THINGS
        for i in range(len(self.nodes)):
            self.nodes[i].findConnectedNodes()
        for i in range(len(self.members)):
            self.members[i].findConnectedMembers()
        
        #CREATE SURROUND PEAKS
        for i in range(self.numberOfPeaks):
            
            moveVect = rs.VectorCreate((0,0,self.peakMagnitudes[i]*.9),(0,0,0))
            
            for j in range(len(self.nodeDict[self.peakIndecesI[i],self.peakIndecesJ[i]].connectedNodes)):
                self.nodeDict[self.peakIndecesI[i],self.peakIndecesJ[i]].connectedNodes[j].move(moveVect)
                self.nodeDict[self.peakIndecesI[i],self.peakIndecesJ[i]].connectedNodes[j].makeFixed()
                self.fixedNodes.append(self.nodeDict[self.peakIndecesI[i],self.peakIndecesJ[i]].connectedNodes[j])

    def cleanLists(self):
        
        for i in range(len(self.nodes)):
            
            purgeList = []
            
            for j in range(len(self.nodes[i].connectedMembers)):
                if self.nodes[i].connectedMembers[j] not in self.members:
                    purgeList.append(self.nodes[i].connectedMembers[j])
            
            for j in range(len(purgeList)):
                self.nodes[i].connectedMembers.remove(purgeList[j])

    def boxTrim(self):
        
        point1 = (10,5,-5)
        point2 = (10,-5,-5)
        point3 = (-10,-5,-5)
        point4 = (-10,5,-5)
        point5 = (10,5,100)
        point6 = (10,-5,100)
        point7 = (-10,-5,100)
        point8 = (-10,5,100)
        
        #rs.AddBox((point1,point2,point3,point4,point5,point6,point7,point8))
        box = rs.BoundingBox((point1,point2,point3,point4,point5,point6,point7,point8))
        
        lostNodes = []
        lostMembers = []
        
        for i in range(len(self.nodes)):
            
            boolRtn = rs.IsObjectInBox(self.nodes[i].guid,box,True)
            
            if boolRtn == False:
                
                rs.DeleteObject(self.nodes[i].guid)
                lostNodes.append(self.nodes[i])
        
        for i in range(len(lostNodes)):
            self.nodes.remove(lostNodes[i])
        
        for i in range(len(self.members)):
            
            boolRtn = rs.IsObjectInBox(self.members[i].curveGUID,box,True)
            
            if boolRtn == False:
                
                rs.DeleteObject(self.members[i].curveGUID)
                lostMembers.append(self.members[i])
                """
            else:
                if self.members[i].startNode not in self.nodes or self.members[i].endNode not in self.nodes:
                    
                    rs.DeleteObject(self.members[i].curveGUID)
                    lostMembers.append(self.members[i])"""
        
        for i in range(len(lostMembers)):
            self.members.remove(lostMembers[i])

    def boxMark(self):
        
        point1 = (10,5,-5)
        point2 = (10,-5,-5)
        point3 = (-10,-5,-5)
        point4 = (-10,5,-5)
        point5 = (10,5,100)
        point6 = (10,-5,100)
        point7 = (-10,-5,100)
        point8 = (-10,5,100)
        
        #rs.AddBox((point1,point2,point3,point4,point5,point6,point7,point8))
        box = rs.BoundingBox((point1,point2,point3,point4,point5,point6,point7,point8))
        
        markedLayer = rs.AddLayer("boxed",(200,0,0))
        
        lostNodes = []
        lostMembers = []
        
        for i in range(len(self.nodes)):
            
            boolRtn = rs.IsObjectInBox(self.nodes[i].guid,box,True)
            
            if boolRtn == True:
                
                rs.ObjectLayer(self.nodes[i].guid,markedLayer)

        for i in range(len(self.members)):
            
            boolRtn = rs.IsObjectInBox(self.members[i].curveGUID,box,True)
            
            if boolRtn == True:
                
                rs.ObjectLayer(self.members[i].curveGUID,markedLayer)

    def pingCorners(self):
        
        def locateNearestNode(POINT):
            
            #Variables
            ##Array to Check
            nodeArr = self.nodes
            ##Point to Check
            point = rs.AddPoint(POINT)
            
            nearestNode = None
            
            ##Current Minimum Distance
            ###Setting up Variable, set super high so any distance will overwrite it
            curMinDist = 1000000000000000000
            
            #Check Point against Point Array
            for i in range(len(nodeArr)):
                
                ##Collect current distance
                dist = rs.Distance(point, nodeArr[i].guid)
                
                ##Check new distance against current minimum
                if curMinDist > dist:
                    
                    ###If new distance is less than current minimum set it to current minimum
                    curMinDist = dist
                    
                    nearestNode = nodeArr[i]
            
            rs.DeleteObject(point)
            
            return nearestNode
            #\\\\\ENDDEF
        
        pointArr = ((9.75,4.75,-.1),(9.75,-4.75,-.1),(-9.75,-4.75,-.1),(-9.75,4.75,-.1))
        
        for i in range(len(pointArr)):
            
            nearNode = locateNearestNode(pointArr[i])
            
            moveVect = rs.VectorCreate(pointArr[i],nearNode.guid)
            
            nearNode.move(moveVect)
            
            nearNode.makeFixed()
            
            for j in range(len(nearNode.connectedNodes)):
                
                nearNode.connectedNodes[j].makeFixed()

    def relaxation(self):
        #loop for each iteration
        for i in range(self.iterations):
            #loop through each node
            for node in self.nodes:
                if node.fixed == False:
                    #zero the force total
                    totalForceVect = [0,0,0]
                    #loop through each connected member
                    for member in node.connectedMembers:
                        #get the force vector from the member
                        memberForceVect = member.getForceVect(node)
                        #add the current member force to the running total
                        totalForceVect = rs.VectorAdd(totalForceVect, memberForceVect)
                    #scale the totla force vector by a damping factor
                    totalForceVect = rs.VectorScale(totalForceVect, globalDamping)
                    
                    #move the node
                    node.move(totalForceVect)


class Member(object):

    def __init__(self, CURVEGUID, SLACKLENGTHFACTOR):
        self.curveGUID = CURVEGUID
        self.startPt = rs.CurveStartPoint(self.curveGUID)
        self.endPt = rs.CurveEndPoint(self.curveGUID)
        self.slackLength = SLACKLENGTHFACTOR * rs.CurveLength(self.curveGUID)
        self.startNode = None
        self.endNode = None
        self.isJoint = False
        self.isBreak = False
        self.branchID = None
        self.connectedMembers = []
        
        #rs.AddTextDot(str(self.level),rs.CurveMidPoint(self.curveGUID))

    def addConnectedNode(self, NODE, START_END):
        if START_END == "START":
            self.startNode = NODE
        else:
            self.endNode = NODE

    def findConnectedMembers(self):
        
        for i in range(len(self.startNode.connectedMembers)):
            if self != self.startNode.connectedMembers[i]:
                self.connectedMembers.append(self.startNode.connectedMembers[i])
        
        for i in range(len(self.endNode.connectedMembers)):
            if self != self.endNode.connectedMembers[i]:
                self.connectedMembers.append(self.endNode.connectedMembers[i])

    def getForceVect(self, NODE):
        forceMagnitude = rs.Distance(self.startPt, self.endPt) - self.slackLength
        forceVect = rs.VectorCreate(self.endPt, self.startPt)
        tempVect = rs.VectorUnitize(forceVect)
        forceVect = rs.VectorScale(tempVect, forceMagnitude)
        #verify that the vector points in the right direction
        if (NODE == self.endNode):
            forceVect = rs.VectorReverse(forceVect)
            
        return forceVect

    def updatePos(self):
        self.startPt = self.startNode.guid
        self.endPt = self.endNode.guid
        rs.DeleteObject(self.curveGUID)
        self.curveGUID = rs.AddLine(self.startPt, self.endPt)

   #ENDCLASS

class Node(object):

    def __init__(self, GUID):
        self.guid = GUID
        self.connectedMembers = []
        self.connectedNodes = []
        self.fixed = False
        self.isBreak = False
        self.isJoint = False
        self.branchID = None
        
        #rs.AddTextDot(self.level, rs.PointCoordinates(self.guid))

    def addConnectedMember(self, MEMBER):
        self.connectedMembers.append(MEMBER)
        #rs.AddTextDot(str(len(self.connectedMembers)), rs.PointCoordinates(self.guid))

    def findConnectedNodes(self):
        
        for i in range(len(self.connectedMembers)):
            if self.connectedMembers[i].startNode != self:
                self.connectedNodes.append(self.connectedMembers[i].startNode)
            
            if self.connectedMembers[i].endNode != self:
                self.connectedNodes.append(self.connectedMembers[i].endNode)

    def makeFixed(self):
        self.fixed = True
        #rs.AddTextDot(str(len(self.connectedMembers)), rs.PointCoordinates(self.guid))

    def unFix(self):
        self.fixed = False

    def move(self, totalForceVect):
        moveVect = rs.VectorAdd((0,0,0), totalForceVect)
        rs.MoveObject(self.guid,moveVect)
        for member in self.connectedMembers:
            member.updatePos()

    #ENDCLASS

class Surface3pt(object):
    
    def __init__(self,MEMBER1,MEMBER2):
        
        self.members = [MEMBER1,MEMBER2]
        self.nodes = []
        
        self.guid = self.create()
        
        surfaceAreaRtn = rs.SurfaceArea(self.guid)
        self.surfaceArea = surfaceAreaRtn[0]

    def create(self):
        
        self.nodes.append(self.members[0].startNode)
        self.nodes.append(self.members[0].endNode)
        
        if self.members[1].startNode not in self.nodes:
            self.nodes.append(self.members[1].startNode)
        
        if self.members[1].endNode not in self.nodes:
            self.nodes.append(self.members[1].endNode)
        
        guidListy = []
        for i in range(len(self.nodes)):
            guidListy.append(self.nodes[i].guid)
        
        return rs.AddSrfPt(guidListy)

    def getOpenNodes(self):
        
        for i in range(len(self.nodes)):
            
            if self.nodes[i] != self.members[0].startNode and self.nodes[i] != self.members[0].endNode:
                node1 = self.nodes[i]
            elif self.nodes[i] != self.members[1].startNode and self.nodes[i] != self.members[1].endNode:
                node2 = self.nodes[i]
        
        if node1 and node2:
            return [node1,node2]

    #ENDCLASS

class Pipe(object):
    
    def __init__(self,MEMBER,STARTRAD,ENDRAD):
        
        self.member = MEMBER
        self.startRadius = STARTRAD
        self.endRadius = ENDRAD
        
        self.guid = self.create()
        
        surfaceAreaRtn = rs.SurfaceArea(self.guid)
        self.surfaceArea = surfaceAreaRtn[0]
        
        surfaceVolumeRtn = rs.SurfaceVolume(self.guid)
        self.volume = surfaceVolumeRtn[0]

    def create(self):

        cdRtn = rs.CurveDomain(self.member.curveGUID)
        startParam = cdRtn[0]
        endParam = cdRtn[1]

        startVector = rs.VectorCreate(self.member.startNode.guid,self.member.endNode.guid)
        self.startPlane = rs.PlaneFromNormal(self.member.startNode.guid,startVector)
        startCirc = rs.AddCircle(self.startPlane,self.startRadius)

        projectPt = rs.CopyObject(self.member.endNode.guid,startVector)
        endVector = rs.VectorCreate(projectPt,self.member.endNode.guid)
        self.endPlane = rs.PlaneFromNormal(self.member.endNode.guid,endVector)
        endCirc = rs.AddCircle(self.endPlane,self.endRadius)
        
        newPipe = rs.AddSweep1(self.member.curveGUID,[startCirc,endCirc])
        rs.CapPlanarHoles(newPipe)
        #newPipe = rs.AddPipe(self.member.curveGUID,[startParam,endParam],[startCirc,endCirc],1)
        
        rs.DeleteObject(projectPt)
        rs.DeleteObject(startCirc)
        rs.DeleteObject(endCirc)

        return newPipe

    #ENDCLASS


if __name__ == "__main__":
    
    #                (SUPERSYSTEM,STARTPOINT,NUMPEAKS,SPACING,NUMLINES,PEAKINDECESI    ,PEAKINDECESJ   ,PEAKMAGNITUDES,SUBPEAKMAGNITUDES,ITERATIONS,ROTMULTI,MAXWIG,UNUSED):
    ge = ometrySystem("test"     ,rs.GetObject("selpt")   ,5       ,1     ,20       ,[.7,.5,.3,.5,.7] ,[.1,.3,.4,.5,.7] ,[10,5,12,8,15],[.9,.7,.8,.8,.9] ,10,.9,.9,0)