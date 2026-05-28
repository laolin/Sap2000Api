# Sap2000 API Copyright (c) 2026 laolin. See LICENSE for details. 

class Frame:
    def __init__(self, sap_model):
        self.SapModel = sap_model

    # ==============================================================================
    # 新建矩形截面
    # ==============================================================================
    def newFrameSectionRect(self, name: str, mat: str, b: float, h: float) -> int:
        ret = self.SapModel.PropFrame.SetRectangle(name, mat, h, b)
        return ret

    def modifyFrameSectionRect(self, name: str, mat: str, b: float, h: float) -> int:
        ret = self.SapModel.PropFrame.SetRectangle(name, mat, h, b)
        return ret

    def setFrameSection(self,frameName: str, sectName: str, ItemType=0):
        """给 frame 指定 新的 section  """
        self.SapModel.FrameObj.SetSection(frameName, sectName, ItemType)


    def addFrameByPoint(self, p1Name, p2Name, sectName, frameName=None) -> str:
        [ret, frmName] = self.SapModel.FrameObj.AddByPoint(p1Name, p2Name, None, sectName, frameName)
        return "" if ret !=0 else frmName

    def addFrameByXyz(self, p1, p2, sectName, frameName=None, CSys="Global") -> str:
        [ret, frmName] = self.SapModel.FrameObj.AddByCoord(
            p1[0], p1[1], p1[2], p2[0], p2[1], p2[2], None, sectName, frameName, CSys
        )
        return "" if ret != 0 else frmName

    def setFrameReleases(self, frmName, res1, res2, ItemType=0):
        startPartialFixity = [0] * 6
        endPartialFixity = [0] * 6 
        return self.SapModel.FrameObj.SetReleases(frmName, res1, res2, startPartialFixity, endPartialFixity, ItemType)