from .chart import Chart
from .DyOp import DyOptim
import yaml as y
import codecs
from typing import Iterable
import sys
import json



c_path = __file__[:-11]



def size_of_iter(iter):
    if isinstance(iter, Iterable):
        return sum([size_of_iter(item) for item in iter])
    else: 
        return sys.getsizeof(iter)



class PoliciedChart(Chart, DyOptim): 
    def __init__(self, filename) -> None:
        with open(c_path + "op_cfg.yaml", "r") as f: 
            self.cfg = y.load(f)
            self.set_cfg()
        self.op_struct = None
        self.link, self.cost, self.end = None, None, None
        self.route = None

        Chart.__init__(self, filename)
        self.load()

        DyOptim.__init__(self, 
            [2 ** st for st in self.get_op_struct()], 
            self.get_link(), 
            self.get_cost(), 
            self.get_end())
        
        # self.max_size = 0.
    
    def set_cfg(self, cfg = None): 
        flag = True

        if cfg: 
            try: self.minStageLen = cfg["minStageLen"]
            except: pass
            else: flag = False

            try: self.maxStageLen = cfg["maxStageLen"]
            except: pass
            else: flag = False

            try: self.stageTime = cfg["stageTime"]
            except: pass
            else: flag = False
        
        if flag: 
            print("使用默认动态规划设置")
            self.minStageLen = self.cfg["minStageLen"]
            self.maxStageLen = self.cfg["maxStageLen"]
            self.stageTime = self.cfg["stageTime"]
    
    def __sizeof__(self):
        return size_of_iter(self.route) / 2 ** 20



    def get_op_struct(self): 
        if self.op_struct is not None:
            return self.op_struct
        
        time_ran = [key[2] - self.stageTime for key in self.keys]
        include_ran = []

        for i in range(self.num_keys): 
            ctime = time_ran[i]
            include_ran.append([])
            for j in range(i): 
                if ctime < self.keys[j][2]: 
                    include_ran[i].append(j)

        for i in range(self.num_keys):
            if include_ran[i]:
                include_ran[i] = len(include_ran[i])
            else: 
                include_ran[i] = 0
        
        for i in range(self.maxStageLen, len(include_ran)):
            include_ran[i] = max(include_ran[i], self.minStageLen)
            include_ran[i] = min(include_ran[i], self.maxStageLen)
        
        self.op_struct = include_ran

        return self.op_struct



    def conflict(self, note_idx, flag): 
        if self.keys[note_idx][2] - self.keys[note_idx - 1][2] > .05: 
            return False
        if self.keys[note_idx][3] > self.keys[note_idx - 1][3] and flag == 0:
            return True
        if self.keys[note_idx][3] < self.keys[note_idx - 1][3] and flag == 1:
            return True
        return False

    def get_link(self): 
        if self.link is None:
            def link(stage_idx, status_idx): 
                assert status_idx < 2 ** self.op_struct[stage_idx]
                next_len = self.op_struct[stage_idx + 1]
                current_tail = status_idx % (2 ** (next_len - 1))
                return (int(current_tail * 2), int(current_tail * 2 + 1))
            self.link = link
        return self.link
    
    def get_cost(self): 
        if self.cost is None:
            def cost(stage_idx, status_idx, next_status_idx): 
                assert next_status_idx in self.link(stage_idx, status_idx)

                if self.op_struct[stage_idx + 1] < 2: 
                    return 0.

                flag = next_status_idx % 2
                prev_idx = None
                i = 1

                while(i <= self.op_struct[stage_idx]):
                    next_status_idx //= 2
                    if next_status_idx % 2 == flag:
                        prev_idx = i
                        break
                    i += 1
                
                if prev_idx is None:
                    cost = 0
                else: 
                    cost = self.xnote_diff(stage_idx - i, stage_idx, flag)
                if next_status_idx % 4 in [2, 3] and self.conflict(stage_idx, next_status_idx % 2): 
                    cost += 1e3
                
                return cost
            self.cost = cost
        return self.cost
    
    def get_end(self):
        if self.end is None:
            def cost_end(end_status_idx): 
                if self.op_struct[-1] < 2: 
                    return 0.

                flag = end_status_idx % 2
                prev_idx = None
                i = 1

                while(i <= self.op_struct[-1] - 1):
                    end_status_idx //= 2
                    if end_status_idx % 2 == flag:
                        prev_idx = i
                        break
                    i += 1
                
                if prev_idx is None:
                    cost = 0
                else: 
                    cost = self.xnote_diff(- 1 - i, -1, flag)
                if end_status_idx % 4 in [2, 3] and self.conflict(-1, end_status_idx % 2): 
                    cost += 1e3
                
                return cost
            self.end = cost_end
        return self.end
    


    def forward(self, cpr_lv = 0):
        if cpr_lv == 0: 
            return DyOptim.forward(self)
        self.reset()
        self.step()
        for _ in range(10):
            self.step()
            if cpr_lv == 1: self.cpr_route(self.pointer + 2)
        while(self.pointer >= 0):
            self.step()
            if cpr_lv == 1: self.cpr_route(self.pointer + 2)
            if cpr_lv == 2 and self.pointer % 10 == 0: self.cpr_route_period(self.pointer + 2, 10)
        if cpr_lv == 3: self.cpr_all()
    
    # def step(self):
    #     super().step()
    #     if self.pointer % 10 == 0: 
    #         self.max_size = max(self.max_size, self.__sizeof__())

    def get_op_re(self, cpr_lv = 3):
        if not self.route:
            self.forward(cpr_lv)
        
        self.re = []
        if len(self.route[1]) > 1: 
            next = 0 if self.route[1][0][2] < self.route[1][1][2] else 1
        else:
            next = 0
        
        for state in self.route[1:-1]: 
            try: 
                next_idx = [live[0] for live in state].index(next)
                self.re.append(state[next_idx][0] % 2)
                next = state[next_idx][1]
            except: 
                assert False, "压缩存储空间过程中，最优路径断裂，阶段编号：%i" %(self.route.index(state))
        
        return self.re
    
    def export(self, filename = None, cpr_lv = 3): 
        if filename is None: 
            filename = self.file[:-5] + ".a&c"
        
        exp_json = self.json
        for i in range(len(self.get_op_re(cpr_lv))):
            exp_json["notes"][i]["_hand"] = self.re[i]
        
        with codecs.open(filename, "w") as f:
            json.dump(exp_json, f)
        
        return exp_json
    
    def __call__(self, filename = None, cpr_lv = 3):
        return self.export(filename, cpr_lv)
