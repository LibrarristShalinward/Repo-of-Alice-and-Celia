# 目标函数相关的类
import yaml as y

ReLU = lambda x : max(x, 0)

class config:
    def __init__(self) -> None:
        with open("diff_cfg.yaml", "r") as f:
            yml = y.load(f)
        for key, value in yml.items(): 
            self.__setattr__(key, value)
        if not "k2" in yml.keys(): 
            self.k2 = 1 / self.D
        if not "k3" in yml.keys(): 
            self.k3 = 10 / self.D
        if not "chi0" in yml.keys(): 
            self.chi0 = self.d

class Diff(config):
    def __init__(self) -> None:
        super().__init__()
        self.dtt = lambda dt: max(dt, self.tao0)

    def point(self, dt):
        return self.k1 / self.dtt(dt)

    def move(self, x_1, x_2, dt):
        if abs(x_2-x_1) > self.chi0:
            dxx = abs(x_2-x_1) - self.chi0
        else:
            dxx = 0
        return self.k2 * dxx / self.dtt(dt)

    def xhand(self, flag, x_2):
        if flag == 0:
            return self.k3 * ReLU(x_2)
        else:
            return self.k3 * ReLU(-x_2)

    def __call__(self, dt, x_1, x_2, bt, flag):# bt键型黑黑0黑黄1黄黑2黄黄3；flag左手0右手1
        if bt == 0 or bt == 2:
            return self.point(dt) + self.move(x_1, x_2, dt) + self.xhand(flag, x_2)
        else:
            return self.k2f * self.move(x_1, x_2, dt) + self.xhand(flag, x_2)
    
    def xnote_diff(self):
        def xnote(notep, noten, flag, bt): 
            return self(
                dt = noten["_time"] - notep["_time"], 
                x_1 = notep["pos"], 
                x_2 = noten["pos"], 
                bt = bt, 
                flag = flag)
        return xnote
