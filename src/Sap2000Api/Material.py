# Sap2000 API Copyright (c) 2026 laolin. See LICENSE for details. 

class Material:
    def __init__(self, sap_model):
        self.SapModel = sap_model

    # ==============================================================================
    # 新建材料
    # ==============================================================================
    def newSteel(self, Name, fy, fu, pho=-1, e=-1, poisson=0.3):
        ret = self.SapModel.PropMaterial.SetMaterial(Name, 1)
        if pho < 0: # 注意，只允许单位为 KN,m 或 N,mm。否则本函数默认值会出错
            pho = 78
        if e<0: # 注意，只允许单位为 KN,m 或 N,mm。否则本函数默认值会出错
            e = 2e8
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
        if pho < 0:  # 注意，只允许单位为 KN,m 或 N,mm。否则本函数默认值会出错
            pho = 25
        if e<0:  # 注意，只允许单位为 KN,m 或 N,mm。否则本函数默认值会出错
            e = 3e7

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