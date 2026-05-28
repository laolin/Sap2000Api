# Sap2000 API Copyright (c) 2026 laolin. See LICENSE for details. 

class Group:
    def __init__(self, sap_model):
        self.SapModel = sap_model

    def newGroup(self, grpName):
        return self.SapModel.GroupDef.SetGroup(grpName)

    def clearGroup(self, grpName):
        return self.SapModel.GroupDef.Clear(grpName)

    def deleteGroup(self, grpName):
        return self.SapModel.GroupDef.Delete(grpName)

    def addNodeToGroup(self, grpName, nodeNameList):
        for n in nodeNameList: self.SapModel.PointObj.SetGroupAssign(n, grpName)

    def addFrameToGroup(self, grpName, frameNameList):
        for n in frameNameList: self.SapModel.FrameObj.SetGroupAssign(n, grpName)