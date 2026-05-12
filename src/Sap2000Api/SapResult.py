"""
Sap2000 API - SapResult
Copyright (c) 2026 laolin @ Gitee. See LICENSE for details.
"""

import os,sys

if __name__ == "__main__":
    sys.path.append("..")

from Sap2000Api import Sap2000Api

class SapResult:

    def __init__(self, sapapi: Sap2000Api) -> None:
        self.SapObject = sapapi.SapObject
        self.SapModel = sapapi.SapModel

    def deselectAllLoadCases(self):
        self.SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()

    def setLoadCase(self, caseName: str):
        return self.SapModel.Results.Setup.SetCaseSelectedForOutput(caseName)

    @staticmethod
    def __RET(res, begin: int, end: int):
        """根据SAP返回值的特点，res[0]表示是否错误。res[1]表示返回值数量。res[2]表示对象名字。
        为方便处理:
        当res=1时，直接返回一个数组，
        当res>1时，返回一个字典。

        """
        if res[0]!=0:
            return res[0]
        if res[1]==0:
            return -1
        if res[1]==1:
            return res[begin : end + 1]
        return {f"{res[2][i]}": [res[j][i] for j in range(begin, end + 1)] for i in range(res[1])}

    # 节点位移
    def getJointDisp(self, pName: str, ItemType: int = 0):
        # [
        #     0  ret,
        #     1  NumberResults,
        #     2  Obj,
        #     3  Elm,
        #     4  ACase,
        #     5  StepType,
        #     6  StepNum,
        #     7  U1,
        #     8  U2,
        #     9  U3,
        #     10 R1,
        #     11 R2,
        #     12 R3,
        # ]
        # ItemTypeElm: 见SAP说明，ObjectElm = 0, Element = 1, GroupElmc = 2, SelectionElm = 3
        r = self.SapModel.Results.JointDispl(pName, ItemType)
        return SapResult.__RET(r, 7, 12)

    # 节点位移-绝对位移
    #  Absolute and relative displacements are the same except when reported for time history load cases subjected to acceleration loading.
    def getJointDispAbs(self, pName: str, ItemType: int = 0):
        # [
        #     0  ret,
        #     1  NumberResults,
        #     2  Obj,
        #     3  Elm,
        #     4  ACase,
        #     5  StepType,
        #     6  StepNum,
        #     7  U1,
        #     8  U2,
        #     9  U3,
        #     10 R1,
        #     11 R2,
        #     12 R3,
        # ]
        # ItemTypeElm: 见SAP说明，ObjectElm = 0, Element = 1, GroupElmc = 2, SelectionElm = 3
        r = self.SapModel.Results.JointDisplAbs(pName, ItemType)
        return SapResult.__RET(r, 7, 12)

    # 节点反力（基于节点的局部坐标。默认同全局坐标，但是节点的局部坐标是可以修改的）
    # 返回的值和符号是 基于节点的局部坐标（SAP里通常节点局部坐标同全局坐标）的杆端内力
    # 即：返回 外部约束 对 节点 的作用力（基于节点的局部坐标（全局坐标））
    def getJointReact(self, pName: str, ItemType: int = 0):
        # [
        #     0  ret,
        #     1  NumberResults,
        #     2  Obj,
        #     3  Elm,
        #     4  ACase,
        #     5  StepType,
        #     6  StepNum,
        #     7  f1,
        #     8  f2,
        #     9  f3,
        #     10 m1,
        #     11 m2,
        #     12 m3,
        # ]
        # ItemTypeElm: 见SAP说明，ObjectElm = 0, Element = 1, GroupElmc = 2, SelectionElm = 3
        r = self.SapModel.Results.JointReact(pName, ItemType)
        return SapResult.__RET(r, 7, 12)

    # 杆件内力（分段，会按杆单元的荷载作用点自动分段，基于杆单元局部坐标）
    def getFrameForce(self, frmName: str, ItemType: int = 0):
        # [
        #     0  ret,  = 0 表示正确。否则出错。
        #     1  NumberResults, 荷载数据长度。
        #     2  @ Obj, 对象元组例如梁名字为'beam1'时，返回的元组可能是这样的：（'beam1','beam1','beam1',...）
        #     3  @ ObjSta,This is an array that includes the distance measured from the I-end of the line object to the result location.
        #           元组，和杆件I点的相真实距离 (0.0, 4.55, 4.55, 6.5, 13.0)
        #     4  Elm,
        #           单元名元组。梁对象可能划分为几个单元。返回的元组可能是这样的：('beam1-1','beam1-1','beam1-1',...)
        #     5  ElmSta,This is an array that includes the distance measured from the I-end of the line element to the result location.
        #           元组，和单元I点的相真实距离 (0.0, 4.55, 4.55, 6.5, 13.0)
        #     6  LoadCase,  荷载工况名元组
        #     7  StepType,  元组，荷载步名，静力时返回元素为空字符串的元组: ('', '', '', '', '')
        #     8  StepNum, 元组，步数？静力时返回元素为0的元组:(0.0, 0.0, 0.0, 0.0, 0.0)
        #
        #     9  P, 构件局部坐标的6个内力
        #     10 V2,
        #     11 V3,
        #     12 T,
        #     13 M2,
        #     14 M3,
        # ]
        res = self.SapModel.Results.FrameForce(frmName, ItemType)
        """根据SAP返回值的特点，res[0]表示是否错误。res[1]表示返回值数量。res[2]表示对象名字。
        为方便处理:
        当res=1时，直接返回一个数组，
        当res>1时，返回一个字典。
        """
        begin, end = 9, 14
        if res[0] != 0:
            return res[0]
        if res[1] == 0:
            return -1
        if res[1] == 1:
            return res[begin : end + 1]
        return {
            f"{res[2][i]}@{i}@{res[3][i]:.6g}": [res[j][i] for j in range(begin, end + 1)]
            for i in range(res[1])
        }

    # 杆件两端节点的内力（基于全局坐标）
    # 返回的值和符号是 基于节点的局部坐标（SAP里通常节点局部坐标同全局坐标）的杆端内力
    # 即：返回 节点 对 杆 的作用力（基于节点的局部坐标（全局坐标））
    def getFrameJointForce(self, frmName: str, ItemType: int = 0):
        # [
        #     0  ret,
        #     1  NumberResults,
        #     2  @ Obj,
        #     3  Elm,
        #     4  @ NodeName,
        #     5  LoadCase,
        #     6  StepType,
        #     7  StepNum,

        #     8  P, 基于全部坐标的6个内力
        #     9  V2,
        #     10 V3,
        #     11 T,
        #     12 M2,
        #     13 M3,
        # ]
        res = self.SapModel.Results.FrameJointForce(frmName, ItemType)

        """根据SAP返回值的特点，res[0]表示是否错误。res[1]表示返回值数量。res[2]表示对象名字。
        为方便处理:
        当res=1时，直接返回一个数组，
        当res>1时，返回一个字典。
        """
        begin,end = 8, 13
        if res[0] != 0:
            return res[0]
        if res[1] == 0:
            return -1
        if res[1] == 1:
            return res[begin : end + 1]
        return {
            f"{res[2][i]}@{res[4][i]}": [res[j][i] for j in range(begin, end + 1)]
            for i in range(res[1])
        }
