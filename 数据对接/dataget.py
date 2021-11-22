import codecs
import numpy as np
import json
from os import mkdir, remove
from os.path import exists, getsize


class chart:
    def __init__(self, ID = None) -> None:
        self.__ID = ID
        self.__name = ""
        self.file = ID + ".json"
        self.json = None

    def exists(self):return exists(self.file)

    def load(self, process = True): 
        if self.exists():
            with codecs.open(self.file, "r") as f:
                self.json = json.load(f)
        else:
            self.json = None
        if process and self.json != None:
            self.__proccess_keys()
        return self.json

    def __proccess_keys(self):
        if self.json == None: self.load()
        id=[]
        time=[]
        size=[]
        #pos=[]
        for obj in self.json['notes']:
            id.append(obj['$id'])
            time.append(obj['_time'])
            size.append(obj['size'])
        iflinks=[0 for _ in range(len(id))]
        for obj in self.json['links']:
            for i in obj['notes']:
                iflinks[(int(i['$ref']))-1]=1
        A=[id, size, time, iflinks]
        A=np.array(A)
        return A