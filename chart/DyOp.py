#本文档致力于完成一个类，用以解决确定性的定期多阶段决策问题

from abc import abstractmethod
from typing import Iterable
import numpy as np
from numpy import inf
from copy import copy

class stage:
    '所有阶段的基类'#定义每个阶段的属性
    #name：表头; value:该阶段当前计算的最小决策成本； pointer：指向使value最小的下一个阶段的状态;self_num：状态总数
    state_num =0
    name = None
    value = None
    pointer = None

    def __init__(self, name_in ):#初始化时要给入该阶段状态的数量和每个状态的名字

        if(name_in is None):
            self.state_num = 1
        else:
            self.state_num = len(name_in)#如果传入空参数就只生成一个

        self.name = name_in

        self.value = np.empty(self.state_num)
        for i in range(0,self.state_num):
            self.value[i] = inf

        self.pointer = np.zeros(self.state_num)#占位，使pointer的结构与name保持一致(即对于每个状态，都应该有一个指针)
        #还是取指针为整型方便一些

    def load(self,values_in = None):#置数，在初始化最后一个状态等情况时使用
        if(values_in is None):
            values = np.zeros(self.state_num)
        else:
            values = values_in#当缺省时则函数做清0使用
        
        for i in range(0,self.state_num):
            self.value[i] = values[i]

    def print(self):
        print(self.name)

        
class Dy_Question:
    '动态规划问题'#定义动态规划整体，然后对整体进行求解
    #stages:一个列表，用于存放所有的状态

    stages = []

    def __init__(self, stage_num ,name_in_s = None):#定义初始化函数,传入一张列表，每一行传入该行的名字
        
        if (name_in_s is None):
            for i in range(0, stage_num):
                self.stages.append(stage(None))
        else:
            for i in range(0, stage_num):
                self.stages.append(stage(name_in_s[i]))
        
        self.stages[stage_num - 1].load()
        
    
    def gen_stage(self, stage_num , name_in):#重新生成某一个特定阶段,state为从1开始的某一标号
        self.stages[stage_num - 1] = stage(name_in)

    def cal_value(self,stage_num,cost_matrix):#用第n+1个状态的value信息生成第n个状态的value和pointer信息

        for cstate in range(0,self.stages[stage_num - 1].state_num):
            for nstate in range(0,self.stages[stage_num].state_num):
                if(self.stages[stage_num - 1].value[cstate] > (self.stages[stage_num].value[nstate] + cost_matrix[cstate][nstate])):
                    #将当前的最小成本和（次态的值加上决策成本）进行比较
                    self.stages[stage_num - 1].value[cstate] = (self.stages[stage_num].value[nstate] + cost_matrix[cstate][nstate])
                    #若小于，则更新最小成本
                    self.stages[stage_num - 1].pointer[cstate] = nstate
                    #并更新指针:直接把nstate的值赋给pointer便能寻址
    
    def output(self):
        best_value = inf
        best_road = np.zeros(1)

        for i in range(0,self.stages[0].state_num):#遍历第一个阶段，找到最优状态
            if(self.stages[0].value[i] < best_value):
                best_value = self.stages[0].value[i]#将该状态的值作为最优值
                best_road[0] = i#将该状态的位数作为路径的起点（采用自然数与pointer保持一致)
        
        
        cstate = i#现态
        for i in range(0,len(self.stages) - 1):
            best_road = np.append(best_road,self.stages[i].pointer[cstate])#将当前状态的指针置入best_road
            #best_road = np.append(best_road,i)#将当前状态的指针置入best_road

            cstate = self.stages[i].pointer[cstate]#当前状态的指针即为下一个状态
            cstate = int(cstate)
        
        key = [best_value,best_road]
        return key


class DyOptim:
    '动态规划问题'#定义动态规划整体，然后对整体进行求解
    #stages:一个列表，用于存放所有的状态

    stages = []

    @abstractmethod
    def link(self, stage_idx, status_idx) -> Iterable: 
        pass

    @abstractmethod
    def cost(self, stage_idx, status_idx, next_status_idx) -> float: 
        pass
    
    @abstractmethod
    def end_cost(self, end_status_idx) -> float:
        pass

    def __init__(self, struct, link, cost, end_cost = None):#定义初始化函数,传入一张列表，每一行传入该行的名字
        
        self.struct = struct
        '''
            struct为动态规划网络结构。其形式如下：
            struct = [阶段0状态数, 阶段1状态数, ..., 阶段n - 1状态数]
        '''
        self.num_stage = len(self.struct)#阶段数
        self.link = link
        '''
            连接函数，形式为link(stage_idx, status_idx)
            返回与第stage_idx阶段第status_idx状态连接的所有第stage_idx + 1阶段状态的编号
        '''
        self.cost = cost
        '''
            惩罚函数，形式为cost(stage_idx, status_idx, next_status_idx)
            返回stage_idx阶段status_idx状态与stage_idx + 1阶段next_status_idx状态间的路程
        '''
        if end_cost is None:
            def end_cost(_): return 0.
        self.end_cost = end_cost

        self.route, self.pointer = None, None
        '''
            暂定路径规划，在规划到第k状态时其形式为
            [
                [(状态0, 下一阶段状态, cost-to-go), 
                (状态1, 下一阶段状态, cost-to-go), 
                (状态2, 下一阶段状态, cost-to-go), 
                ..., 
                (状态n_k - 1, 下一阶段状态, cost-to-go)], #阶段k

                [(状态1, 下一阶段状态, cost-to-go), 
                (状态2, 下一阶段状态, cost-to-go), 
                (状态4, 下一阶段状态, cost-to-go), 
                ..., 
                (状态###, 下一阶段状态, cost-to-go)], #阶段k + 1
                
                [(状态0, 下一阶段状态, cost-to-go), 
                (状态16, 下一阶段状态, cost-to-go), 
                (状态384, 下一阶段状态, cost-to-go), 
                ..., 
                (状态###, 下一阶段状态, cost-to-go)], #阶段k + 2
                
                ..., 

                [(状态32, 下一阶段状态, cost-to-go), 
                (状态854, 下一阶段状态, cost-to-go), 
                (状态1438, 下一阶段状态, cost-to-go), 
                ..., 
                (状态###, 下一阶段状态, cost-to-go)], #阶段n - 1]
        '''
        self.reset()

    def cal_value(self, state_idx): #用第state_idx + 1个状态的cost-to-go信息生成第state_idx个状态的cost-to-go和pointer信息
        
        assert state_idx == self.pointer
        print("开始规划第%i阶段" %(state_idx))
        self.route = [[]] + self.route

        if self.pointer == self.num_stage - 1:
            return self.cal_end()

        for stage_idx in range(self.struct[state_idx]): 
            min_c = inf
            for this_p in self.link(state_idx, stage_idx): 
                this_c = self.cost(state_idx, stage_idx, this_p) + self.route[1][this_p][2]#将当前的最小成本和（次态的值加上决策成本）进行比较
                if this_c < min_c:
                    min_c = this_c #若小于，则更新最小成本
                    min_p = this_p #并更新指针:直接把nstate的值赋给pointer便能寻址
            self.route[0].append((stage_idx, min_p, min_c))
        
        self.pointer -= 1
    
    def cal_end(self): 
        assert self.pointer == self.num_stage - 1
        self.route = [[]] + self.route
        
        for stage_idx in range(self.struct[-1]): 
            self.route[0].append((stage_idx, None, self.end_cost(stage_idx)))
        
        self.pointer -= 1


    def cpr_route(self, state_idx): #根据第state_idx - 1个状态的pointer信息删除第state_idx个状态的大部分记录，仅保留pointer指向的状态的信息，精简路径列表，降低空间复杂度
        
        assert state_idx > self.pointer + 1

        valid_stage = []
        for stage in self.route[state_idx - self.pointer - 2]: 
            idx = stage[1]
            if not idx in valid_stage:
                valid_stage.append(idx)

        ori_len = len(self.route[state_idx - self.pointer - 1])
        i = 0
        j = 0

        while(i < len(self.route[state_idx - self.pointer - 1])): 
            if j == len(valid_stage):
                del self.route[state_idx - self.pointer - 1][i:]
                break
            else: 
                vld_idx = valid_stage[j]
            
            if self.route[state_idx - self.pointer - 1][i][0] == vld_idx:
                i += 1
                j += 1
            else:
                del self.route[state_idx - self.pointer - 1][i]
        
        return ori_len - len(self.route[state_idx - self.pointer - 1])
    
    def cpr_routes(self, start_idx, end_idx): 
        cpr_size = 0
        for idx in range(start_idx, min(end_idx, self.num_stage - 1)): 
            cpr_size += self.cpr_route(idx)
        return cpr_size
    
    def cpr_route_period(self, start_idx, l): 
        return self.cpr_routes(start_idx, start_idx + l)
    
    def cpr_after(self, start_idx): 
        return self.cpr_routes(start_idx, self.num_stage - 1)
    
    def cpr_all(self):
        return self.cpr_after(self.pointer + 2)
    
    def reset(self):
        del self.route
        self.pointer = self.num_stage - 1
        self.route = []

    def step(self): 
        self.cal_value(self.pointer)
    
    def forward(self): 
        self.reset()
        while(self.pointer >= 0):
            self.step()

    def output(self):
        best_value = inf
        best_road = np.zeros(1)

        for i in range(0,self.stages[0].state_num):#遍历第一个阶段，找到最优状态
            if(self.stages[0].value[i] < best_value):
                best_value = self.stages[0].value[i]#将该状态的值作为最优值
                best_road[0] = i#将该状态的位数作为路径的起点（采用自然数与pointer保持一致)
        
        
        cstate = i#现态
        for i in range(0,len(self.stages) - 1):
            best_road = np.append(best_road,self.stages[i].pointer[cstate])#将当前状态的指针置入best_road
            #best_road = np.append(best_road,i)#将当前状态的指针置入best_road

            cstate = self.stages[i].pointer[cstate]#当前状态的指针即为下一个状态
            cstate = int(cstate)
        
        key = [best_value,best_road]
        return key


def main():
    names = [
        [1,2,3],
        [4,5],
        [6,7,8],
        [9]
    ]

    Q1 = Dy_Question(4,names)
    c3 = [
        [1],
        [2],
        [3]
    ]
    c2 = [
        [6,4,4],
        [inf,5,2]
    ]
    c1 = [
        [2,1],
        [1,3],
        [3,2]
    ]
    
    Q1.cal_value(3,c3)
    Q1.cal_value(2,c2)
    Q1.cal_value(1,c1)
    
    key = Q1.output()
    print( key[1])
    

    

if __name__ == '__main__':
    main() 

