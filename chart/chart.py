import codecs
import json
from os.path import exists


class Chart:
    def __init__(self, filename) -> None:
        self.file = filename
        self.json = None

    def exists(self): return exists(self.file)

    def load(self, process=True):
        assert self.exists(), "文件不存在"
        with codecs.open(self.file, "r") as f:
            self.json = json.load(f)
        if process:
            self.__proccess_keys()

    def __proccess_keys(self):
        if self.json == None:
            self.load()
        id = []
        time = []
        size = []
        pos = []
        for obj in self.json['notes']:
            id.append(obj['$id'])
            time.append(obj['_time'])
            size.append(obj['size'])
            pos.append(obj['pos'])
        iflinks = [0 for _ in range(len(id))]
        for obj in self.json['links']:
            for i in obj['notes']:
                iflinks[(int(i['$ref']))-1] = 1
        self.keys = [key_info for key_info in zip(id, size, time, pos, iflinks)]
