"""
GENETIC FABRIC CASTING
TAUBMAN COLLEGE THESIS W2013
MARK WRIGHT & MATTHEW JENSEN

FILE MANAGEMENT SCRIPT

Required for .gif capture:
    Python 2.7 x86 w/ PIL and numpy installed

    RunCPythonScript.py: https://github.com/localcode/rhinopythonscripts/blob/master/RunCPythonScript.py

    images2gif.py: https://code.google.com/p/visvis/source/browse/images2gif.py?spec=svnd82415598349aa47ba3d5b226124fc9b6ba72353&r=d82415598349aa47ba3d5b226124fc9b6ba72353

    animatedGif.py

If you don't want to use that / don't have it installed
comment it out at around line 190 and it will still run
"""

import rhinoscriptsyntax as rs
import random as rd
import os

global externalSoftwareExists
externalSoftwareExists = False

if os.path.exists('C:\Python27') == True and os.path.exists("C:\Python27\Lib\site-packages\\" + "numpy")  == True and os.path.exists('C:\Python27\Lib\site-packages\PIL') == True :
    externalSoftwareExists = True
    import RunCPythonScript as rc

print "externalSoftwareExists = " + str(externalSoftwareExists)

class leManager(object):

    #INIT
    def __init__(self):
        
        filter = "Text file (*.csv)|*.csv|All Files (*.*)|*.*||"
        self.inputFilenames = rs.OpenFileNames("Open Files", filter)
        
        if not self.inputFilenames: return
        
        self.systemIDS = []
        self.fileDataDict = {}
        self.variableTypeKey = {}
        self.scriptPath = os.path.dirname(os.path.realpath(__file__))

        self.getVariableTypeKey()

        for i in range(len(self.inputFilenames)):
            self.readParentFile(self.inputFilenames[i])

    #INIT FUNCTIONS
    def getVariableTypeKey(self):
        
        def csvStripSplit(TEXT):
            
            data = TEXT.strip("()\n").strip("()\r").split(",")
            
            return data
        
        #read each line from the file
        file = open(self.scriptPath + "\\VariableTypeKey.csv", "r")
        contents = file.readlines()
        file.close()
        
        #strip data from input file
        contents = [csvStripSplit(line) for line in contents]
        
        for i in range(len(contents)):
            
            #collect variable names
            self.variableTypeKey[contents[i][0]] = contents[i][1]

    def readParentFile(self,FILE):
        
        variableNames = []
        variableValues = []
        
        #read each line from the file
        file = open(FILE, "r")
        contents = file.readlines()
        file.close()

        def csvStripSplit(TEXT):
            
            data = TEXT.strip("()\n").strip("()\r").split(",")
            
            return data

        def csvConvertStrings():
        
            for i in range(len(variableValues)):
                
                if self.variableTypeKey[variableNames[i]] == 'float':
                    variableValues[i] = float(variableValues[i])
                elif self.variableTypeKey[variableNames[i]] == 'int': 
                    variableValues[i] = int(variableValues[i])

        #strip data from input file
        contents = [csvStripSplit(line) for line in contents]
        
        for i in range(len(contents)):
            
            #collect variable names
            variableNames.append(contents[i][0])
            #collect variable values
            variableValues.append(contents[i][1])
        
        #convert files to their file types
        csvConvertStrings()
        
        #add new 
        self.systemIDS.append(FILE)
        self.fileDataDict[FILE] = variableValues

    #EXTERNAL FUNCTIONS
    def writeResults(self,SUPERSYSTEM):

        def captureAnimatedGif(objectsToCapture):
            
            #reset view to default perspective view
            rs.Command("-_Perspective")
            
            #select objects to image
            rs.SelectObjects(objectsToCapture)
            
            #hide everything else
            objsToHide = rs.InvertSelectedObjects()
            rs.HideObjects(objsToHide)
            
            #reselect objects to image
            rs.SelectObjects(objectsToCapture)
            
            #zoom into the objects to image
            rs.ZoomSelected()
            
            #zoom out slightly
            rs.Command("Zoom Out")
            
            #deselect those objects
            rs.UnselectAllObjects()
            
            #determine the rotation angle for each image
            rotateAngle = 360/50
            
            #draw each frame and rotate
            for i in range(50):
                
                imgDrop = '"' + fileFolder + "\image" + str(i) + '.png"'
                rs.Command("-_ViewCaptureToFile " + imgDrop + " _Width=800 _Height=800 _Enter")
                rs.RotateView(None,0,rotateAngle)
            
            #designate where to save new gif
            animateScriptPath = self.scriptPath + "\\animatedGif.py"
            
            #pass off work to external script
            arguments = ['"' + fileFolder + '"']
            print arguments
            runRtn = rc.run(animateScriptPath, arguments, 'python',False)
            print runRtn
            
            #move the newly created gif to the actual destination
            srcPath = fileFolder + "animatedOutput.gif"
            dstPath = filePath[:-4] + "_image.gif"
            os.rename(srcPath,dstPath)
            
            #delete temporary images
            for i in range(50):
                img2Del = fileFolder + "\image" + str(i) + ".png"
                os.remove(img2Del)
            
            #unhide all objects
            rs.ShowObjects(objsToHide)

        def captureSingleJpg(objectsToCapture):
            
            #reset view to default perspective view
            rs.Command("-_Perspective")
            
            #select objects to image
            rs.SelectObjects(objectsToCapture)
            
            #hide everything else
            objsToHide = rs.InvertSelectedObjects()
            rs.HideObjects(objsToHide)
            
            #reselect objects to image
            rs.SelectObjects(objectsToCapture)
            
            #zoom into the objects to image
            rs.ZoomSelected()
            
            #zoom out slightly
            rs.Command("Zoom Out")
            
            #deselect those objects
            rs.UnselectAllObjects()
            
            savePath = '"' + filePath[:-4] + '_thumbnail.jpg"'
            
            rs.Command("-_ViewCaptureToFile " + savePath + " _Width=295 _Height=295 _Enter")
            
            #unhide all objects
            rs.ShowObjects(objsToHide)

        #rename input variables
        insys = SUPERSYSTEM
        
        filePath = os.path.realpath(insys.ID)
        fileFolder = os.path.dirname(os.path.realpath(insys.ID))
        
        file = open(insys.ID , "a")
        
        file.write("SystemLength," + str(insys.systemLength) + "\n")
        file.write("SystemHeight," + str(insys.systemHeight) + "\n")
        file.write("SystemDensity," + str(insys.systemDensity) + "\n")
        file.write("NumberOfMembers," + str(insys.numberOfMembers) + "\n")
        file.write("AverageMemberLength," + str(insys.averageMemberLength) + "\n")
        file.write("MaxMemberLength," + str(insys.maxMemberLength) + "\n")
        file.write("MinMemberLength," + str(insys.minMemberLength) + "\n")
        file.write("SurfaceArea," + str(insys.surfaceArea) + "\n")
        file.write("Volume," + str(insys.volume) + "\n")
        
        file.close()
        
        rs.Command("_-SetDisplayMode _Shaded _Enter")
        
        if externalSoftwareExists == True:
            captureAnimatedGif(insys.allObjects)
        
        captureSingleJpg(insys.allObjects)
        
        rs.SelectObjects(insys.allObjects)
        exportPath = '"' + filePath[:-4] + '_geometry.3dm"'
        rs.Command("_-Export _SaveSmall=Yes " + exportPath + " _Enter")
        rs.UnselectAllObjects()


if __name__ == "__main__":
    
    fi = leManager()
    
    print fi.fileDataDict