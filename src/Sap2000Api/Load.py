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
        nDir, csys = self._dir_to_int_csys(dir)
        self.SapModel.FrameObj.SetLoadPoint(frmName, patName, nLtype, nDir, distance, val, csys, relativeDist, Replace, ItemType)

    def addLoad_FrameDistributed(self, frmName, patName, isMoment, dir, dist, val, relativeDist=True, Replace=True, ItemType=0):
        nLtype = 2 if isMoment else 1
        nDir, csys = self._dir_to_int_csys(dir)
        return self.SapModel.FrameObj.SetLoadDistributed(frmName, patName, nLtype, nDir, dist[0], dist[1], val[0], val[1], csys, relativeDist, Replace, ItemType)


    # ==============================================================================
    #  面对象均布荷载 (Uniform Load on Area Objects)
    #  在面对象上直接施加均布面荷载（非传递至框架）
    # ==============================================================================
    def addLoad_AreaUniform(self, areaName: str, patName: str, val: float,
                             dir: str, Replace: bool = True, CSys: str = None, ItemType: int = 0):
        """给面对象分配均布面荷载（需要对面单元进行剖分、最终是传递面单元的节点荷载到边梁上）

        Parameters
        ----------
        areaName : str
            面对象名称或组名称，取决于 ItemType 取值
        patName : str
            已定义的荷载模式名称
        val : float
            均布荷载值 [F/L²]
        dir : str
            荷载方向, 支持以下 6 种字符串:
              "LOCAL1" 局部1轴    "LOCAL2" 局部2轴    "LOCAL3" 局部3轴
              "X"      X方向     "Y"      Y方向     "Z"      Z方向
        Replace : bool
            是否替换该荷载模式下已有的均布荷载, 默认True
        CSys : str, optional
            坐标系名称, 默认 None 时由 dir 自动推断 (LOCALx→"Local", X/Y/Z→"Global")
            也可手动指定坐标系名称
        ItemType : int
            指定 areaName 的含义: 0=Object(按名称), 1=Group(按组), 2=SelectedObjects(按选中对象),
            默认0

        Returns
        -------
        int
            0 表示成功, 非0 表示失败
        """
        nDir, autoCSys = self._dir_to_int_csys(dir)
        if CSys is None:
            CSys = autoCSys
        ret = self.SapModel.AreaObj.SetLoadUniform(
            areaName, patName, val, nDir, Replace, CSys, ItemType
        )
        return ret

    # ==============================================================================
    #  面对象均布至框架荷载 (Uniform to Frame Load on Area Objects)
    #  将面对象上的均布荷载按单向或双向传递到其支撑框架上
    # ==============================================================================
    def addLoad_AreaUniformToFrame(self, areaName: str, patName: str, val: float,
                                    dir: str, distOneWayTwoWay: int = 2,
                                    Replace: bool = True, CSys: str = None, ItemType: int = 0):
        """给面对象分配均布至框架荷载（用简单的导荷载公式，传递梯形、三角形分布荷载到边梁上）

        Parameters
        ----------
        areaName : str
            面对象名称或组名称，取决于 ItemType 取值
        patName : str
            已定义的荷载模式名称
        val : float
            均布荷载值 [F/L²]
        dir : str
            荷载方向, 支持以下 6 种字符串:
              "LOCAL1" 局部1轴    "LOCAL2" 局部2轴    "LOCAL3" 局部3轴
              "X"      X方向     "Y"      Y方向     "Z"      Z方向
        distOneWayTwoWay : int
            荷载分布类型: 1=单向分布(平行于局部1轴), 2=双向分布(平行于局部1轴和2轴), 默认2
        Replace : bool
            是否替换该荷载模式下已有的均布荷载, 默认True
        CSys : str, optional
            坐标系名称, 默认 None 时由 dir 自动推断 (LOCALx→"Local", X/Y/Z→"Global")
            也可手动指定坐标系名称
        ItemType : int
            指定 areaName 的含义: 0=Object(按名称), 1=Group(按组), 2=SelectedObjects(按选中对象),
            默认0

        Returns
        -------
        int
            0 表示成功, 非0 表示失败
        """
        nDir, autoCSys = self._dir_to_int_csys(dir)
        if CSys is None:
            CSys = autoCSys
        ret = self.SapModel.AreaObj.SetLoadUniformToFrame(
            areaName, patName, val, nDir, distOneWayTwoWay, Replace, CSys, ItemType
        )
        return ret

    # ==============================================================================
    #  方向字符串转整数 (辅助函数, 供面对象均布至框架荷载使用)
    #  将 6 个方向字符串映射为 SAP2000 内部的整数值及推荐坐标系
    # ==============================================================================
    def _dir_to_int_csys(self, dir_str: str) -> tuple:
        """将方向字符串转换为 (方向整数值, 坐标系)

        Parameters
        ----------
        dir_str : str
            方向字符串, 支持以下 6 种取值:
              "LOCAL1" → 局部1轴    "LOCAL2" → 局部2轴    "LOCAL3" → 局部3轴
              "X"      → X方向     "Y"      → Y方向     "Z"      → Z方向

        Returns
        -------
        tuple
            (int, str): 方向整数值(1~6) 和 坐标系字符串("Local" 或 "Global")
            未匹配时默认返回 (10, "Global") 即重力方向
        """
        mapping = {
            "LOCAL1": (1, "Local"), "LOCAL2": (2, "Local"), "LOCAL3": (3, "Local"),
            "X": (4, "Global"),     "Y": (5, "Global"),     "Z": (6, "Global"),
        }
        return mapping.get(dir_str.upper(), (10, "Global"))