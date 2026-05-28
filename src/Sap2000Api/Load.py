# Sap2000 API Copyright (c) 2026 laolin. See LICENSE for details. 

class Load:
    def __init__(self, sap_model):
        self.SapModel = sap_model

    def addLoadPattern(self, patName, patType, SelfWTMultiplier, AddLoadCase=True):
        return self.SapModel.LoadPatterns.Add(patName, patType, SelfWTMultiplier, AddLoadCase)

    def addLoad_Node(self, nodeName, patName, val, replaceOldLoad=True, CSys="Global", ItemType=0):
        r1 = self.SapModel.PointObj.SetLoadForce(nodeName, patName, val, replaceOldLoad, CSys, ItemType)
        return r1[0]

    def addLoad_FramePointForce(self, frmName, patName, isMoment, dir, distance, val, relativeDist=True, Replace=True, ItemType=0):
        nLtype = 2 if isMoment else 1
        dir = dir.upper()
        mapping = {"LOCAL1": (1, "Local"), "LOCAL2": (2, "Local"), "LOCAL3": (3, "Local"), "X": (4, "Global"), "Y": (5, "Global"), "Z": (6, "Global")}
        nDir, csys = mapping.get(dir, (10, "Global"))
        self.SapModel.FrameObj.SetLoadPoint(frmName, patName, nLtype, nDir, distance, val, csys, relativeDist, Replace, ItemType)

    def addLoad_FrameDistributed(self, frmName, patName, isMoment, dir, dist, val, relativeDist=True, Replace=True, ItemType=0):
        nLtype = 2 if isMoment else 1
        dir = dir.upper()
        mapping = {"LOCAL1": (1, "Local"), "LOCAL2": (2, "Local"), "LOCAL3": (3, "Local"), "X": (4, "Global"), "Y": (5, "Global"), "Z": (6, "Global")}
        nDir, csys = mapping.get(dir, (10, "Global"))
        return self.SapModel.FrameObj.SetLoadDistributed(frmName, patName, nLtype, nDir, dist[0], dist[1], val[0], val[1], csys, relativeDist, Replace, ItemType)
