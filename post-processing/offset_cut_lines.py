import rhinoscriptsyntax as rs

def offsetCutLines(CURVES,MODIFIER,DOTS):
    
    inputCurves = CURVES
    
    modifier = MODIFIER
    
    textDots = DOTS
    
    for i in range(len(inputCurves)):
        
        innerCurves = []
        outerCurves = []
        
        centroid = rs.AddPoint(rs.CurveAreaCentroid(inputCurves[i])[0])
        explodedCurves = rs.ExplodeCurves(inputCurves[i],True)
        
        for j in range(len(explodedCurves)):
            
            innerCurves.append(explodedCurves[j])
            outerCurves.append(rs.OffsetCurve(innerCurves[j],centroid,-.25))
        
        for j in range(len(outerCurves)):
            for k in range(len(outerCurves)):
                if j != k:
                    cciRtn = rs.CurveCurveIntersection(outerCurves[j],outerCurves[k])
                    if cciRtn:
                        
                        dist1 = rs.Distance(rs.CurveStartPoint(outerCurves[j]),cciRtn[0][1])
                        dist2 = rs.Distance(rs.CurveEndPoint(outerCurves[j]),cciRtn[0][1])
                        
                        if dist1 > dist2:
                            pointToUse = rs.CurveStartPoint(outerCurves[j])
                        else:
                            pointToUse = rs.CurveEndPoint(outerCurves[j])
                            
                        
                        newLine = rs.AddLine(pointToUse,cciRtn[0][1])
                        rs.DeleteObject(outerCurves[j])
                        outerCurves[j] = newLine
        
        for j in range(len(outerCurves)):
            line1 = rs.AddLine(rs.CurveStartPoint(innerCurves[j]),rs.CurveStartPoint(outerCurves[j]))
            line2 = rs.AddLine(rs.CurveEndPoint(innerCurves[j]),rs.CurveEndPoint(outerCurves[j]))
            
            line3 = rs.AddLine(rs.CurveStartPoint(innerCurves[j]),rs.CurveEndPoint(outerCurves[j]))
            line4 = rs.AddLine(rs.CurveEndPoint(innerCurves[j]),rs.CurveStartPoint(outerCurves[j]))
                
            
            test1 = rs.CurveCurveIntersection(line1,line2)
            
            if test1:
                rs.DeleteObject(line1)
                rs.DeleteObject(line2)
                
            test2 = rs.CurveCurveIntersection(line3,line4)
            if test2:   
                rs.DeleteObject(line3)
                rs.DeleteObject(line4)
                
        
        if modifier == "PANEL":
            
            for j in range(len(outerCurves)):
                
                dom = rs.CurveDomain(outerCurves[j])
                
                center = rs.EvaluateCurve(outerCurves[j],dom[0]+((dom[1] - dom[0])/3))
                
                rotVect = rs.VectorCreate(center,(center[0],center[1],center[2]+1))
                
                tag = rs.AddCircle(center,.5)
                point = rs.AddPoint(center)
                
                vect = rs.VectorCreate(rs.CurveEndPoint(outerCurves[j]),rs.CurveStartPoint(outerCurves[j]))
                vect = rs.VectorRotate(vect,90,rotVect)
                vect = rs.VectorUnitize(vect)
                vect = rs.VectorScale(vect,.375)
                
                
                distance = rs.Distance(centroid,point)
                rs.MoveObject(tag,vect)
                rs.MoveObject(point,vect)
                newDistance = rs.Distance(centroid,point)
                
                if newDistance < distance:
                    vect = rs.VectorReverse(vect)
                    rs.MoveObject(tag,vect)
                    rs.MoveObject(point,vect)
                    rs.MoveObject(tag,vect)
                    rs.MoveObject(point,vect)
                
                cciRtn = rs.CurveCurveIntersection(tag,outerCurves[j])
                
                length = rs.CurveLength(tag)/2
                newTag = rs.TrimCurve(tag,(cciRtn[1][5],cciRtn[0][5]),False)
                newLength = rs.CurveLength(newTag)
                
                if newLength < length:
                    rs.DeleteObject(newTag)
                    newTag = rs.TrimCurve(tag,(cciRtn[0][5],cciRtn[1][5]),False)
                
                leg1 = rs.AddLine(rs.CurveStartPoint(outerCurves[j]),cciRtn[1][1])
                leg2 = rs.AddLine(rs.CurveEndPoint(outerCurves[j]),cciRtn[0][1])
                
                if rs.CurveCurveIntersection(leg1,leg2):
                    rs.DeleteObject(leg1)
                    rs.DeleteObject(leg2)
                    leg1 = rs.AddLine(rs.CurveStartPoint(outerCurves[j]),cciRtn[0][1])
                    leg2 = rs.AddLine(rs.CurveEndPoint(outerCurves[j]),cciRtn[1][1])
                
                rs.DeleteObject(tag)
                newCrv = rs.JoinCurves((newTag,leg1,leg2),True)
                rs.DeleteObject(outerCurves[j])
                outerCurves[j] = newCrv
                
                if textDots:
                    for k in range(len(textDots)):
                        
                        bool = rs.IsPointOnCurve(innerCurves[j],rs.TextDotPoint(textDots[k]))
                        
                        if bool == True:
                            
                            rs.TextDotPoint(textDots[k],point)
                            
                            rs.SelectObject(textDots[k])
                            
                            rs.Command("_-ConvertDots _DeleteInput=No _Output=Text _TextHeight=.5 _HorizontalAlign=Center _VerticalAlign=Middle _Enter")
                            
                            rs.UnselectAllObjects()
                            
                            break
                    
                    rs.DeleteObject(point)
        
        if modifier == "MEMBER":
            for j in range(len(outerCurves)):
                
                dom = rs.CurveDomain(outerCurves[j])
                
                center = rs.EvaluateCurve(outerCurves[j],dom[1]-((dom[1] - dom[0])/3))
                rotVect = rs.VectorCreate(center,(center[0],center[1],center[2]+1))
                
                point = rs.AddPoint(center)
                
                vect = rs.VectorCreate(rs.CurveEndPoint(outerCurves[j]),rs.CurveStartPoint(outerCurves[j]))
                vect = rs.VectorRotate(vect,90,rotVect)
                vect = rs.VectorUnitize(vect)
                vect = rs.VectorScale(vect,.375)
                
                distance = rs.Distance(centroid,point)
                rs.MoveObject(point,vect)
                newDistance = rs.Distance(centroid,point)
            
                if newDistance > distance:
                    vect = rs.VectorReverse(vect)
                    rs.MoveObject(point,vect)
                    rs.MoveObject(point,vect)
                
                if textDots:
                    for k in range(len(textDots)):
                        
                        bool = rs.IsPointOnCurve(innerCurves[j],rs.TextDotPoint(textDots[k]))
                        
                        if bool == True:
                            
                            rs.TextDotPoint(textDots[k],point)
                            
                            rs.SelectObject(textDots[k])
                            
                            rs.Command("_-ConvertDots _DeleteInput=No _Output=Text _TextHeight=.5 _HorizontalAlign=Center _VerticalAlign=Middle _Enter")
                            
                            rs.UnselectAllObjects()
                            
                            break
                    
                    rs.DeleteObject(point)
            
        
        
        rs.DeleteObjects(innerCurves)
        rs.DeleteObject(centroid)

if __name__ == "__main__":
    
    CURVES = rs.GetObjects("select panel pieces",rs.filter.curve)
    
    CURVES2 = rs.GetObjects("select member pieces",rs.filter.curve)
    
    DOTS = rs.GetObjects("select text dots",rs.filter.textdot)
    
    if CURVES: offsetCutLines(CURVES,"PANEL",DOTS)
    if CURVES2: offsetCutLines(CURVES2,"MEMBER",DOTS)
    
    if DOTS: rs.DeleteObjects(DOTS)
