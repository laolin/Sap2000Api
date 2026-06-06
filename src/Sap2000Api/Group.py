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

    @staticmethod
    def _ret_code(ret):
        return ret[0] if isinstance(ret, tuple) and len(ret) > 0 else ret

    def addNodeToGroup(self, grpName, nodeNameList):
        failed = []
        for n in nodeNameList:
            ret = self.SapModel.PointObj.SetGroupAssign(n, grpName)
            ret_code = self._ret_code(ret)
            if ret_code not in (None, 0):
                failed.append((n, ret))
        return 0 if not failed else failed

    def addFrameToGroup(self, grpName, frameNameList):
        failed = []
        for n in frameNameList:
            ret = self.SapModel.FrameObj.SetGroupAssign(n, grpName)
            ret_code = self._ret_code(ret)
            if ret_code not in (None, 0):
                failed.append((n, ret))
        return 0 if not failed else failed
