# Sap2000 API Copyright (c) 2026 laolin. See LICENSE for details. 

from enum import IntEnum

class Area:
    def __init__(self, sap_model):
        self.SapModel = sap_model

    class ShellType(IntEnum):
        ''' ShellType 枚举定义
            1 = 薄壳 (Shell - thin)
            2 = 厚壳 (Shell - thick)
            3 = 薄板 (Plate - thin)
            4 = 厚板 (Plate - thick)
            5 = 膜 (Membrane)
            6 = 分层壳/非线性壳 (Shell layered/nonlinear)           
        '''
        SHELL_THIN = 1
        SHELL_THICK = 2
        PLATE_THIN = 3
        PLATE_THICK = 4
        MEMBRANE = 5
        SHELL_LAYERED = 6
        

    def newAreaSection(self, section_name: str,ShellType, material_name: str, thickness: float) -> int:
        # IncludeDrillingDOF = True, MatAng = 0.0
        ret = self.SapModel.PropArea.SetShell_1(section_name, ShellType, True, material_name,  0.0, thickness, thickness)
        return ret
    
    #  同 newAreaSection
    def modifyAreaSection(self, section_name: str,ShellType, material_name: str, thickness: float) -> int:
        # IncludeDrillingDOF = True, MatAng = 0.0
        ret = self.SapModel.PropArea.SetShell_1(section_name, ShellType, True, material_name,  0.0, thickness, thickness)
        return ret


    def addArea(self,point_names,section_name,area_name):
        self.SapModel.AreaObj.AddByPoint(
            len(point_names),   # NumberPoints
            point_names,   # Point 字符串数组
            None,
            section_name,  # PropName
            area_name,     # Name  
        )
        