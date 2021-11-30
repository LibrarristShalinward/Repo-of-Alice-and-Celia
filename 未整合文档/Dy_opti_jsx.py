#本文档致力于完成一个类，用以解决确定性的定期多阶段决策问题

import numpy as np
from numpy import inf

class stage:
    '所有阶段的基类'#定义每个阶段的属性
    #name：表头; value:该阶段当前计算的最小决策成本； pointer：指向使value最小的下一个阶段的状态;self_num：状态总数
    state_num =0
    name = None
    value = None
    pointer = None

    def __init__(self, name_in ):#初始化时要给入该阶段状态的数量和每个状态的名字

        if(name_in == None):
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
        if(values_in == None):
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
        
        if (name_in_s == None):
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

