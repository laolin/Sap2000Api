# Sap2000 API Copyright (c) 2026 laolin. See LICENSE for details. 

import os
import win32com.client

from .Group import Group
from .Material import Material
from .Load import Load
from .Node import Node
from .Frame import Frame

from .Result import Result

class Sap2000Api:

    def __init__(self,version: str = "Sap2000v15") -> None:
        self.version=version
        self.SapObject = None
        self.SapModel = None
        self.Units = 6  # kN_m_C = 6

        # create Sap2000 object
        self.SapObject = win32com.client.Dispatch(self.version + ".SapObject")
        # create SapModel object
        self.SapModel = self.SapObject.SapModel

        self.Group = Group(self.SapModel)
        self.Material = Material(self.SapModel)
        self.Load = Load(self.SapModel)

        self.Node = Node(self.SapModel)
        self.Frame = Frame(self.SapModel)

        self.Result = Result(self.SapModel)

    # ==============================================================================
    #  1 开始sap2000进程 (基础管理保留在主类)
    # ==============================================================================
    def startApp(self, Units:int=6, Visible:bool=True, FileName:str=None) -> int:
        if Units !=9: Units=6
        self.Units = Units
        self.SapObject.ApplicationStart(Units, Visible, FileName)

    def exitApp(self, saveFile: bool = True) -> int:
        ret = self.SapObject.ApplicationExit(saveFile)
        self.SapObject = None
        return ret

    def refrashView(self):
        self.SapModel.View.RefreshView(0, False)

    def newModel(self):
        self.SapModel.InitializeNewModel(self.Units)
        return self.SapModel.File.NewBlank()

    def save(self, fn: str=''):
        return self.SapModel.File.Save(fn)

    def runAnalysis(self):
        return self.SapModel.Analyze.RunAnalysis()

    def lockModel(self):
        return self.SapModel.SetModelIsLocked(True)

    def unlockModel(self):
        return self.SapModel.SetModelIsLocked(False)

    def SetActiveDOF(self, dof):
        return self.SapModel.Analyze.SetActiveDOF(dof)

    # ------------------------
    # ==============================================================================
    # 设置质量源
    # srcType =1 表示来自荷载
    # loadPats 来自哪些荷载
    # massMultipliers 每个荷载的系数
    # 例 self.SetMassSource(1,['DEAD',"LIVE"],[1.0,0.5])
    # ==============================================================================
    def SetMassSource(self, srcType: int=2, loadPats=None, massMultipliers=None):
        # This is 1, 2 or 3, indicating the mass source option.
        # 1 = From element self mass and additional masses
        # 2 = From loads
        # 3 = From element self mass and additional masses and loads
        if loadPats is None:
            loadPats=["DEAD", "LIVE"]
        if massMultipliers is None:
            massMultipliers = [1.0, 0.5]

        self.SapModel.PropMaterial.SetMassSource(srcType, len(loadPats),loadPats, massMultipliers)
