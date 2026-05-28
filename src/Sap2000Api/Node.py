# Sap2000 API Copyright (c) 2026 laolin. See LICENSE for details. 

class Node:
    def __init__(self, sap_model):
        self.SapModel = sap_model

     # ==============================================================================
    # 新建一个节点
    # ==============================================================================
    def addNode(self, p1, nodeName=None, CSys="Global", MergeOff=False, MergeNumber=0) -> str:
        ret, nodename = self.SapModel.PointObj.AddCartesian(
            p1[0], p1[1], p1[2], None, nodeName, CSys, MergeOff, MergeNumber
        )
        return None if ret!=0 else nodename

    def alignNode(self, nodeName: str, dir: str, val: float):
        if dir.upper() == "X": d = 1
        elif dir.upper() == "Y": d = 2
        elif dir.upper() == "Z": d = 3
        else: return -1
        self.SapModel.PointObj.SetSelected(nodeName, True)
        self.SapModel.EditPoint.Align(d, val)

    def setNodeLocalAxes(self, nodeName, degRz, degRy, degRx):
        return self.SapModel.PointObj.SetLocalAxes(nodeName, degRz, degRy, degRx)

    def setNodeRestraint(self, nodeName, res1, ItemType=0):
        self.SapModel.PointObj.SetRestraint(nodeName, res1, ItemType)
