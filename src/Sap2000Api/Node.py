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

    # ==============================================================================
    #  刚性隔板约束 (Diaphragm Constraint)
    #  定义或修改一个刚性隔板约束，约束平面内所有节点在其平面内具有相同的位移
    # ==============================================================================
    def defineDiaphragm(self, name: str, axis: int = 3, CSys: str = "Global") -> int:
        """定义或修改刚性隔板约束 (Diaphragm Constraint)

        若指定名称未被使用，则新建约束；若已用于同类型隔板约束，则修改其定义；
        若已用于其他类型约束，则返回错误。

        Parameters
        ----------
        name : str
            约束名称
        axis : int
            隔板平面法线方向，取值如下:
              1 = X轴 (垂直于YZ平面)
              2 = Y轴 (垂直于XZ平面)
              3 = Z轴 (垂直于XY平面)
              4 = AutoAxis (自动根据所分配的节点确定), 默认3
        CSys : str
            坐标系名称, 默认 "Global"

        Returns
        -------
        int
            0 表示成功, 非0 表示失败
        """
        return self.SapModel.ConstraintDef.SetDiaphragm(name, axis, CSys)

    # ==============================================================================
    #  将节点分配到约束 (Assign Constraint to Point Objects)
    #  将指定的节点约束（如隔板约束）分配给相应的节点对象
    # ==============================================================================
    def setNodeDiaphragm(self, nodeName: str, DiaphragmName: str, Replace: bool = True, ItemType: int = 0) -> int:
        """将节点分配到指定的约束 (Assign Constraint to Point Objects)

        Parameters
        ----------
        nodeName : str
            节点名称或组名称，取决于 ItemType 取值
        constraintName : str
            已定义的约束名称（如通过 setDiaphragm 定义的隔板约束）
        Replace : bool
            是否替换该节点上已有的约束分配, 默认True
        ItemType : int
            指定 nodeName 的含义: 0=Object(按名称), 1=Group(按组), 2=SelectedObjects(按选中对象),
            默认0

        Returns
        -------
        int
            0 表示成功, 非0 表示失败
        """
        return self.SapModel.PointObj.SetConstraint(nodeName, DiaphragmName, ItemType, Replace)
