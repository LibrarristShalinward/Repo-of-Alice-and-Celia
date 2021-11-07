#目标函数相关的类
import numpy as np 
class Solution:
    D = 0.16
    d = 0.02
    k1 = 1
    k2 = 1/D
    k2f = 1.2
    k3 = 10/D
    tao0 = 0.1
    chi0 = d
    def __init__(self, dt, x_1, x_2, bt, flag):  #bt键型黑黑0黑黄1黄黑2黄黄3；flag左手0右手1
        self.dt = dt
        self.x_1 = x_1
        self.x_2 = x_2
        self.bt = bt
        self.flag = flag
    def Point(self):
        if self.dt > self.tao0:
            dtt = self.dt
        else:
            dtt = self.tao0
        return self.k1 / dtt
    def Move(self):
        if abs(self.x_2-self.s_1) > self.chi0:
            dxx = abs(self.x_2-self.s_1) - self.chi0
        else:
            dxx = 0
        return self.k2 * dxx / self.dt
    def ReLU(self):
        if self.x_2 >= 0:
            return self.x_2
        else:
            return 0    
    def Xhand(self):
        if self.flag == 0:
            return self.k3 * self.ReLU(self.x_2)
        else:
            return self.k3 * self.ReLU(-self.x_2)
    def Diff(self):
        if (self.bt == 0)|(self.bt == 2):
            return self.Point() + self.Move() + self.Xhand()
        else:
            return self.k2f * self.Move() + self.Xhand()