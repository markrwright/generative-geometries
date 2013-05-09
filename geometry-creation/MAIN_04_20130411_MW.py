"""
GENETIC FABRIC CASTING
TAUBMAN COLLEGE THESIS W2013
MARK WRIGHT & MATTHEW JENSEN

MAIN SCRIPT
"""

import rhinoscriptsyntax as rs
import GENETICS_03_20130407_MW as fi
import GEOMETRY_02_20130421 as ge

class superSystem(object):

    def __init__(self,SYSTEMID,SYSTEMZERO):
        
        #input variables
        self.ID = SYSTEMID
        self.zero = rs.AddPoint(SYSTEMZERO)
        
        #base point variables
        self.numberOfPeaks = fm.fileDataDict[self.ID][0]
        self.peakIndecesI = fm.fileDataDict[self.ID][1:6]
        self.peakIndecesJ = fm.fileDataDict[self.ID][6:11]
        self.peakMagnitudes = fm.fileDataDict[self.ID][11:16]
        self.subPeakMagnitudes = fm.fileDataDict[self.ID][16:21]
        
        self.systemLength = None
        self.systemHeight = None
        self.systemDensity = None
        self.numberOfMembers = None
        self.averageMemberLength = None
        self.maxMemberLength = None
        self.minMemberLength = None
        self.surfaceArea = None
        self.volume = None
        
        #collections
        self.allObjects = []
        
        
        #                               (SUPERSYSTEM,STARTPOINT,NUMPEAKS          ,SPACING             ,NUMLINES            ,PEAKINDECESI     ,PEAKINDECESJ     ,PEAKMAGNITUDES     ,SUBPEAKMAGNITUDES,RELAXATIONITERATIONS)
        self.geoSystem = ge.ometrySystem(self.ID    ,self.zero,fm.fileDataDict[self.ID][0],fm.fileDataDict[self.ID][22],fm.fileDataDict[self.ID][21],self.peakIndecesI,self.peakIndecesJ,self.peakMagnitudes,self.subPeakMagnitudes,fm.fileDataDict[self.ID][23],fm.fileDataDict[self.ID][24],fm.fileDataDict[self.ID][25],fm.fileDataDict[self.ID][26])
        
        self.collectGeometries()
        
        self.systemAnalysis()
        
        #END INIT

    def systemAnalysis(self):
        
        self.numberOfMembers = len(self.geoSystem.members)
        
        for i in range(len(self.geoSystem.members)):
            
            memberLengths = []
            
            memberLengths.append(rs.CurveLength(self.geoSystem.members[i].curveGUID))
            
            memberLengths.sort()
            
            self.maxMemberLength = memberLengths[-1]
            
            self.minMemberLength = memberLengths[0]
            
            self.averageMemberLength = sum(memberLengths) / self.numberOfMembers
        
        boundingBox = rs.BoundingBox(self.allObjects)
        
        self.systemLength = rs.Distance(boundingBox[0],boundingBox[2])
        
        self.systemHeight = rs.Distance(boundingBox[0],boundingBox[4])
        
        surfaceObjects = []
        
        pipeVolumes = []
        
        for i in range(len(self.geoSystem.pipes)):
            surfaceObjects.append(self.geoSystem.pipes[i].surfaceArea)
            pipeVolumes.append(self.geoSystem.pipes[i].volume)
        for i in range(len(self.geoSystem.surfaces)):
            surfaceObjects.append(self.geoSystem.surfaces[i].surfaceArea)
        
        self.surfaceArea = sum(surfaceObjects)
        
        self.volume = sum(pipeVolumes)
        
        tempBox = rs.AddBox(boundingBox)
        
        BoundingBoxVolume = rs.SurfaceVolume(tempBox)
        
        rs.DeleteObject(tempBox)
        
        self.systemDensity = self.numberOfMembers / BoundingBoxVolume[0]

    def collectGeometries(self):
        
        #Collect all Geometry for super list
        for i in range(len(self.geoSystem.members)):
                self.allObjects.append(self.geoSystem.members[i].curveGUID)
        
        for i in range(len(self.geoSystem.nodes)):
                self.allObjects.append(self.geoSystem.nodes[i].guid)
        """
        for i in range(len(self.geoSystem.pipes)):
                self.allObjects.append(self.geoSystem.pipes[i].guid)
        
        for i in range(len(self.geoSystem.surfaces)):
                self.allObjects.append(self.geoSystem.surfaces[i].guid)
                """

    #END CLASS


#||||||||||MAIN
def main():

    #BEGIN
    global fm
    
    fm = fi.leManager()
    
    if fm.inputFilenames:
        #collect systems in list
        systems = []
         
        #SET UP SYSTEM ARRAY IN RHINOSPACE
        #set y axis interval to begin at 0
        zeroY = 0
        
        #set up interval for systems to be placed in rhinospace
        for i in range(len(fm.systemIDS)):
            
            if fm.systemIDS[i] != "skip":
                
                zeroX = (i%5) * 600
                
                if i%5 == 0 and i !=0:  
                    zeroY = zeroY + 1000
                
                systemZero = (zeroX,zeroY,0)
                
                
                #CREATE SYSTEM
                systems.append(superSystem(fm.systemIDS[i],systemZero))
        
        #WRITE RESULTS FILE
        for i in range(len(systems)):
            fm.writeResults(systems[i])
            
    
    #END MAIN

if __name__ == "__main__": main()
