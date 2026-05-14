"""
Sap2000 API
Copyright (c) 2026 laolin. See LICENSE for details.
"""

import os
import win32com.client

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

    # ==============================================================================
    #  1 开始sap2000进程
    # ==============================================================================
    """
    Units
        lb_in_F = 1
        lb_ft_F = 2
        kip_in_F = 3
        kip_ft_F = 4
        kN_mm_C = 5
        kN_m_C = 6
        kgf_mm_C = 7
        kgf_m_C = 8
        N_mm_C = 9
        N_m_C = 10
        Ton_mm_C = 11
        Ton_m_C = 12
        kN_cm_C = 13
        kgf_cm_C = 14
        N_cm_C = 15
        Ton_cm_C = 16
    """
    # 默认单位制: kN_m_C=6  (N_mm_C=9)
    def startApp(self, Units:int=6, Visible:bool=True, FileName:str=None) -> int:
        if Units !=9: # 只允许6:KN m,  或 9:n mm 
            Units=6
        self.Units = Units

        # start Sap2000 application
        self.SapObject.ApplicationStart(Units, Visible, FileName)

    # ==============================================================================
    #  2 结束sap2000进程
    # ==============================================================================
    def exitApp(self, saveFile: bool = True) -> int:
        ret = self.SapObject.ApplicationExit(saveFile)
        self.SapObject = None
        return ret

    # ==============================================================================
    #  3 刷新窗口
    # ==============================================================================
    def refrashView(self):
        # refresh view, update (initialize) zoom
        ret = self.SapModel.View.RefreshView(0, False)

    # ==============================================================================
    #  新模型文件
    # ==============================================================================
    def newModel(self):
        # initialize model
        self.SapModel.InitializeNewModel(self.Units)

        # create new blank model
        return self.SapModel.File.NewBlank()

    # ==============================================================================
    #  保存模型文件
    # ==============================================================================
    def save(self, fn: str=''):
        return self.SapModel.File.Save(fn)

    # ==============================================================================
    #  开始分析
    # ==============================================================================
    def runAnalysis(self):
        # run model (this will create the analysis model)
        return self.SapModel.Analyze.RunAnalysis()

    # ==============================================================================
    #  lock模型
    # ==============================================================================
    def lockModel(self):
        return self.SapModel.SetModelIsLocked(True)

    # ==============================================================================
    #  unlock模型
    # ==============================================================================
    def unlockModel(self):
        return self.SapModel.SetModelIsLocked(False)

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

    # ==============================================================================
    # 新建材料
    # ==============================================================================
    def newSteel(self, Name, fy, fu, pho=-1, e=-1, poisson=0.3):
        ret = self.SapModel.PropMaterial.SetMaterial(Name, 1)
        if pho < 0:
            if self.Units==6:  # 注意，只允许单位为 KN,m 或 N,mm。否则本函数默认值会出错
                pho = 78
            else:
                pho = 78e-9
        if e<0:
            if self.Units==6:  # 注意，只允许单位为 KN,m 或 N,mm。否则本函数默认值会出错
                e = 2e8
            else:
                e = 2e5
        self.modifySteel(Name, fy, fu, pho, e, poisson)

    def modifySteel(self, Name, fy, fu, pho, e, poisson):
        ret = self.SapModel.PropMaterial.SetMPIsotropic(Name, e, poisson, 1.170e-05)  # 线膨胀系数暂时不用 随便设
        ret = self.SapModel.PropMaterial.SetWeightAndMass(Name, 1, pho)  # 1  表示容重（力），（不是质量）
        ret = self.SapModel.PropMaterial.SetOSteel_1(
            Name, fy, fu,
            fy * 1.1, fu * 1.1,  # 强制有效屈服强度是屈服强度的1.1倍
            1,2,0.015, 0.11, 0.17, -0.1,  # 参数化应应曲线，参考默认Q345的参数
        )
        return ret

    def newConcrete(self, Name, fc, pho=-1, e=-1,poisson=0.2):
        ret = self.SapModel.PropMaterial.SetMaterial(Name, 2)
        if pho < 0:
            if self.Units==6:  # 注意，只允许单位为 KN,m 或 N,mm。否则本函数默认值会出错
                pho = 25
            else:
                pho = 25e-9
        if e<0:
            if self.Units==6:  # 注意，只允许单位为 KN,m 或 N,mm。否则本函数默认值会出错
                e = 3e7
            else:
                e = 3e4

        self.modifyConcrete(Name, fc, pho, e, poisson)
        return ret

    def modifyConcrete(self, Name,fc, pho,e,poisson):
        # assign isotropic mechanical properties to material
        ret1 = self.SapModel.PropMaterial.SetMPIsotropic(Name, e, poisson, 1.000e-05)  # 线膨胀系数暂时不用 随便设
        ret2 = self.SapModel.PropMaterial.SetWeightAndMass(Name, 1, pho)  # 1  表示容重（力），（不是质量）
        ret3 = self.SapModel.PropMaterial.SetOConcrete_1(
            Name, fc,   
            False, 0, 1, 2, 0.0022, 0.0052, -0.1  # 大概参考默认的C30的参数
        )

        return ret1*10000+ret2*100+ret3

    """
    Name:
        材料名
    MatType:
        MATERIAL_STEEL = 1
        MATERIAL_CONCRETE = 2
        MATERIAL_NODESIGN = 3
        MATERIAL_ALUMINUM = 4
        MATERIAL_COLDFORMED = 5
        MATERIAL_REBAR = 6
        MATERIAL_TENDON = 7
    e:
        弹模
    psRatio:
        泊松比
    tCoefficient:
        热膨胀系数
    # """
    # def newMaterial(
    #     self,
    #     Name: str,
    #     MatType: int,
    #     e: float,
    #     psRatio: float,
    #     tCoefficient: float,
    #     Color: int = -1,
    #     Notes: str = "",
    #     GUID: str = "",
    # ) -> int:

    #     ret = self.SapModel.PropMaterial.SetMaterial(Name, MatType, Color, Notes, GUID)
    #     if ret !=0:
    #         return ret
    #     # assign isotropic mechanical properties to material
    #     ret = self.SapModel.PropMaterial.SetMPIsotropic(Name, e, psRatio, tCoefficient)
    #     return ret

    """
    TODO 增加更多截面
    SapObject.SapModel.PropFrame.SetModifiers
    # SetRectangle 矩形 *****
    # SetCircle 实心圆形截面 *****
    # SetTube 矩形管 *****
    # SetPipe 圆管 *****
    # SetISection 工字截面 *****
    # SetTee T型截面 *****
    # SetAngle 角钢
    # SetDblAngle 双角钢
    # SetChannel 槽型
    # SetDblChannel 双槽型
    # SetGeneral 通用截面
    #
    # SetRebarBeam 给混凝土梁指定钢筋
    # SetRebarColumn 给混凝土柱指定钢筋
    #
    # SetModifiers 修改属性

    """
    # ==============================================================================
    # 新建矩形截面
    # 注意 b h 的顺序和sap的函数顺序相反
    # ==============================================================================
    def newFrameSectionRect(self, name: str, mat: str, b: float, h: float) -> int:
        # define rectangular frame section property
        ret = self.SapModel.PropFrame.SetRectangle(name, mat, h, b)
        # if ret != 0:
        #     return ret
        # define frame section property modifiers
        # ModValue = [1, 1, 1, 1, 1, 1, 1, 1]
        # ret = self.SapModel.PropFrame.SetModifiers(name, ModValue)
        return ret
    # ==============================================================================
    # 修改矩形截面
    # ==============================================================================
    def modifyFrameSectionRect(self, name: str, mat: str, b: float, h: float) -> int:
        ret = self.SapModel.PropFrame.SetRectangle(name, mat, h, b)
        return ret

    def setFrameSection(self,frameName: str, sectName: str, ItemType=0):
        """给 frame 指定 新的 section  """
        self.SapModel.FrameObj.SetSection(frameName, sectName, ItemType)

    # ==============================================================================
    # 新建一个节点
    # ==============================================================================
    def addNode(
        self,
        p1: tuple[float, float, float],
        nodeName: str = None,  # 指定的名字，
        CSys: str = "Global",  # 坐标系 "Global" / "Local" / or the name of a defined coordinate system.
        MergeOff: bool = False,
        MergeNumber: int = 0,
    ) -> str:
        ret, nodename = self.SapObject.SapModel.PointObj.AddCartesian(
            p1[0], p1[1], p1[2], None, nodeName, CSys, MergeOff, MergeNumber
        )
        return None if ret!=0 else nodename

    # 一次只能修改x,y,z中的一个坐标。
    # dir=1,2,3 分别代表修改x,y,z坐标
    def alignNode(self, nodeName: str, dir: str, val: float):
        if dir == "x" or dir == "X":
            d = 1
        elif dir == "y" or dir == "Y":
            d = 2
        elif dir == "z" or dir == "Z":
            d = 3
        else:
            return -1
        self.SapModel.PointObj.SetSelected(nodeName, True)
        self.SapModel.EditPoint.Align(d, val)

    # ==============================================================================
    # 新建一根框架（梁、柱、撑） - 指定端点 节点标签 方式
    # ==============================================================================
    def addFrameByPoint(
        self,
        p1Name: str,
        p2Name: str,
        sectName: str,
        frameName: str = None,  # 指定的名字，
        CSys: str = "Global",
    ) -> str:
        [ret, frmName] = self.SapModel.FrameObj.AddByPoint(p1Name, p2Name, None, sectName, frameName)
        return "" if ret !=0 else frmName

    # ==============================================================================
    # 新建一根框架（梁、柱、撑） - 直接输入坐标方式
    # ==============================================================================
    def addFrameByXyz(
        self,
        p1: tuple[float, float, float],
        p2: tuple[float, float, float],
        sectName: str,
        frameName: str = None,  # 指定的名字，
        CSys: str = "Global",
    ) -> str:
        [ret, frmName] = self.SapModel.FrameObj.AddByCoord(
            p1[0], p1[1], p1[2], p2[0], p2[1], p2[2], None, sectName, frameName, CSys
        )
        return "" if ret != 0 else frmName

    # ==============================================================================
    def setNodeLocalAxes(self, nodeName: str, degRz: float, degRy: float, degRx: float)->int:
        """设置节点的局部坐标。SAP2000里，节点的局部坐标默认同全局坐标。
        此函数可改变节点的局部坐标系。
        (1) 从全局坐标开始 以Z轴正向为转轴,按右手法则转degRz度
        (2) 以旋转后的 Y轴正向为转轴 按右手法则转degRy度
        (3) 以旋转后的 X轴正向为转轴 按右手法测志degRx度
        最终得到节点的局部坐标系

        Args:
            nodeName (str): 节点名
            degRz (float): Z轴正向为转轴,按右手法则转degRz度
            degRy (float): 以旋转后的 Y轴正向为转轴 按右手法则转degRy度
            degRx (float): 以旋转后的 X轴正向为转轴 按右手法测志degRx度
        """
        return self.SapModel.PointObj.SetLocalAxes(nodeName, degRz, degRy, degRx)

    # ==============================================================================
    #  节点支座（约束）设置
    # ==============================================================================
    def setNodeRestraint(
        self,
        nodeName: str,
        res1: tuple[bool, bool, bool, bool, bool, bool],
        ItemType: int = 0,  # ItemType 0: 节点, 1: 组
    ):
        ret = self.SapModel.PointObj.SetRestraint(nodeName, res1, ItemType)

    # ==============================================================================
    #  框架（梁、柱、撑）两端支座设置
    # ==============================================================================
    # frmName: 框架名字 addFrame函数创建时返回的名字，或组名字（ItemType=1时）
    # ItemType：=0时按框架名字，=1时按组名字
    def setFrameReleases(self,frmName:str,res1:tuple[bool,bool,bool,bool,bool,bool],res2:tuple[bool,bool,bool,bool,bool,bool],
                         ItemType:int=0):

        startPartialFixity = [0] * 6
        endPartialFixity = [0] * 6  # 释放的弹簧刚度。非0时注意量纲
        return self.SapModel.FrameObj.SetReleases(frmName, res1, res2,startPartialFixity,endPartialFixity,ItemType)

    # ==============================================================================
    #  添加荷载模式，默认自动添加对应的荷载工况
    # ==============================================================================
    def addLoadPattern(
        self,
        patName: str,
        patType: int,
        SelfWTMultiplier: float,
        AddLoadCase: bool = True,
    ):
        return self.SapModel.LoadPatterns.Add(patName,patType,SelfWTMultiplier, AddLoadCase)

    # ==============================================================================
    #  是加在单元的节点上加荷载
    # ==============================================================================
    # frmName: 框架名字 addFrame函数创建时返回的名字
    # patName: 荷载模式
    # val: 6个数: f1 f2 f3 m1 m2 m3 , 以全局坐标系
    def addLoad_Node(
        self,
        nodeName: str,
        patName: str,
        val: tuple[float, float, float, float, float, float],
        replaceOldLoad: bool = True,
        CSys:str="Global",
        ItemType:int=0,  # 默认0 表示nodeName是对象名。 =1表示nodeName是Group名。 =2表示荷载加到当前选择对象上（frmName参数无用）
    ):
        # 注意  SAP UI操作加荷载时 默认是替换，但对于节点荷载SAP API 默认是不替换!
        r1 = self.SapModel.PointObj.SetLoadForce(nodeName, patName,val,replaceOldLoad,CSys,ItemType)  # 默认用输入的荷替换节点上的原有荷载
        return r1[0]

    # def deleteLoad_Node(self,
    #     nodeName: str,
    #     patName: str,
    #     ItemType: int = 0,  # ItemType 0: 节点, 1: 组
    #     ):

    #     # ItemType参数0表示删除1个节点上的荷载； 1表示nodeName是组名，对一组的节点荷载操作
    #     return self.SapModel.PointObj.DeleteLoadForce(nodeName, patName,ItemType)
    
    # ==============================================================================
    #  框架（梁、柱、撑）杆单元上（内部） 施加集中力
    #  注 荷载是加在 杆单元上， 可以是集中弯矩或集中力
    # ==============================================================================
    # frmName: 框架名字 addFrame函数创建时返回的名字
    # patName: 荷载模式
    # isMoment: 是集中弯矩？ 或集中力
    # dir: 力方向 类型str,  允许值:
    #   局部坐标系： 'local1' 'local2' 'local3'
    #   全局坐标系 'x' 'y' 'z'
    #   重力方向 'g'  （和z相反的方向）
    # distance 作用点距i节点的距离 (可能是相对距离 0~1)
    # val: 1个数: f1 f2 f3 或 m1 m2 m3 , 以全局坐标系
    # relativeDist: True表示距离是相对杆件总长的相对长度，范围:[0,1]. 当为False时，表示参数距离是真实距离
    # Replace: 默认True, 原荷载删除。false则原荷不删
    # ItemType: 默认0 表示frmName是对象名。 =1表示frmName是Group名. =2表示荷载加到当前选择对象上（frmName参数无用）。
    def addLoad_FramePointForce(
        self,
        frmName: str,
        patName: str,
        isMoment: bool,
        dir: str,
        distance: float,
        val: float,
        relativeDist: bool = True,
        Replace: bool = True,
        ItemType: int = 0,
    ):
        # 1 = Force
        # 2 = Moment
        nLtype = 2 if isMoment else 1
        dir = dir.upper()
        if dir == "LOCAL1":
            nDir = 1
            csys = "Local"
        elif dir == "LOCAL2":
            nDir = 2
            csys = "Local"
        elif dir == "LOCAL3":
            nDir = 3
            csys = "Local"
        elif dir == "X":
            nDir = 4
            csys = "Global"
        elif dir == "Y":
            nDir = 5
            csys = "Global"
        elif dir == "Z":
            nDir = 6
            csys = "Global"
        else:  # if dir == "G":
            nDir = 10
            csys = "Global"

        self.SapModel.FrameObj.SetLoadPoint(frmName,patName,nLtype,nDir,distance,val,csys,relativeDist,Replace,ItemType)

    # ==============================================================================
    #  框架（梁、柱、撑） 杆上施加分布荷载 （梯形分布）
    # ==============================================================================
    '''
    # frmName: 框架名字 addFrame函数创建时返回的名字
    # patName: 荷载模式
    # isMoment:  False=均布力 True=均布弯矩
    # dir: 力方向 类型str,  允许值:
    #   局部坐标系： 'local1' 'local2' 'local3'
    #   全局坐标系 'x' 'y' 'z'
    #   重力方向 'g'  （和z相反的方向）
    # 1 = Local 1 axis (only applies when CSys is Local)
    # 2 = Local 2 axis (only applies when CSys is Local)
    # 3 = Local 3 axis (only applies when CSys is Local)
    # 4 = X direction (does not apply when CSys is Local)
    # 5 = Y direction (does not apply when CSys is Local)
    # 6 = Z direction (does not apply when CSys is Local)
    # 7 = Projected X direction (does not apply when CSys is Local)
    # 8 = Projected Y direction (does not apply when CSys is Local)
    # 9 = Projected Z direction (does not apply when CSys is Local)
    # 10 = Gravity direction (only applies when CSys is Global)
    # 11 = Projected Gravity direction (only applies when CSys is Global)
    #
    # relativeDist: True表示距离是相对杆件总长的相对长度，范围:[0,1]. 当为False时，表示参数距离是真实距离
    # Replace: 默认True, 原荷载删除。false则原荷不删
    # ItemType: 默认0 表示frmName是对象名。 =1表示frmName是Group名 =2表示荷载加到当前选择对象上（frmName参数无用）。
    '''
    def addLoad_FrameDistributed(
        self,
        frmName: str,
        patName: str,
        isMoment: bool,
        dir: str,
        dist: tuple[float, float],
        val: tuple[float, float],
        relativeDist: bool = True,
        Replace: bool = True,
        ItemType: int=0
    ):
        # 根据SAP文档: This is 1 or 2, indicating the type of distributed load.
        # 1 = Force per unit length
        # 2 = Moment per unit length
        nLtype = 2 if isMoment else 1

        dir=dir.upper()
        if dir=='LOCAL1':
            nDir=1
            csys='Local'
        elif dir == "LOCAL2":
            nDir = 2
            csys = "Local"
        elif dir=='LOCAL3':
            nDir = 3
            csys = "Local"
        elif dir == "X":
            nDir = 4
            csys = "Global"
        elif dir == "Y":
            nDir = 5
            csys = "Global"
        elif dir == "Z":
            nDir = 6
            csys = "Global"
        else: #if dir == "G":
            nDir = 10
            csys = "Global"
        return self.SapModel.FrameObj.SetLoadDistributed(
            frmName,
            patName,
            nLtype,
            nDir,
            dist[0],dist[1],
            val[0],val[1],
            csys,
            relativeDist,
            Replace,
            ItemType,
        )

    def SetActiveDOF(self,dof):
        """sets the model global degrees of freedom."""
        return self.SapModel.Analyze.SetActiveDOF(dof)

    def newGroup(self,grpName):
        """创建组（如果不存在）"""
        return self.SapModel.GroupDef.SetGroup(grpName)

    def clearGroup(self, grpName):
        """清除组内所有已有的assignment"""
        return self.SapModel.GroupDef.Clear(grpName)

    def deleteGroup(self, grpName):
        """删除组"""
        return self.SapModel.GroupDef.Delete(grpName)

    def addNodeToGroup(self, grpName, nodeNameList):
        """将节点加入组"""
        for n in nodeNameList:
            self.SapModel.PointObj.SetGroupAssign(n, grpName)

    def addFrameToGroup(self, grpName, frameNameList):
        """将杆单元加入组"""
        for n in frameNameList:
            self.SapModel.FrameObj.SetGroupAssign(n, grpName)
