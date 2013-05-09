import rhinoscriptsyntax as rs

def createMembers(SURFACE,CENTROID):
    
    #LOCALIZE INPUT VARIABLES
    inputSurface = SURFACE
    
    #LOCATE POLYSURFACE CENTROID
    centroid = CENTROID
    
    #BREAK DOWN POLYSURFACE
    surfaces = rs.ExplodePolysurfaces(inputSurface)
    
    #SILHOUETTE SURFACES
    rs.SelectObjects(surfaces)
    rs.Command("Silhouette")
    members = rs.LastCreatedObjects()
    rs.UnselectAllObjects()
    
    #LOCATE SURFACE NODES
    nodes = []
    for i in range(len(surfaces)):
        controlPoints = rs.SurfacePoints(surfaces[i])
        for j in range(len(controlPoints)):
            if controlPoints[j] not in nodes:
                nodes.append(controlPoints[j])
    
    #CREATE TRIM LINES
    for i in range(len(nodes)):
        rs.AddLine(nodes[i],centroid)
    
    #LOFT MEMBERS
    memberSurfaces = []
    extrudedMembers = []
    for j in range(len(surfaces)):
        surfaceNormal = rs.SurfaceNormal(surfaces[j],(0,0))
        surfaceNormal = rs.VectorReverse(surfaceNormal)
        
        for i in range(len(members)):
            if rs.IsPointOnSurface(surfaces[j],rs.CurveStartPoint(members[i])) == True and rs.IsPointOnSurface(surfaces[j],rs.CurveEndPoint(members[i])) == True:
                if members[i] not in extrudedMembers:
                    extrudedMembers.append(members[i])
                    
                    midPt = rs.AddPoint(rs.CurveMidPoint(members[i]))
                    
                    extrudeVect = rs.VectorUnitize(surfaceNormal)
                    extrudeVect = rs.VectorScale(extrudeVect,3)
                    
                    newPt = rs.CopyObject(midPt,extrudeVect)
                    extrusion = rs.ExtrudeCurveStraight(members[i],midPt,newPt)
                    
                    orientFrom = (rs.CurveStartPoint(members[i]),rs.CurveEndPoint(members[i]),newPt)
                    orientTo = (rs.CurveStartPoint(members[i]),rs.CurveEndPoint(members[i]),centroid)
                    
                    rs.OrientObject(extrusion,orientFrom,orientTo)
                    
                    memberSurfaces.append(extrusion)
                    
                    rs.DeleteObject(newPt)
                    
    
    rs.DeleteObject(inputSurface)


if __name__ == "__main__":
    
    panels = rs.GetObjects("select triangular panels", rs.filter.polysurface)
    
    centroid = rs.GetObject("select centroid point",rs.filter.point)
    
    createMembers(panels,centroid)