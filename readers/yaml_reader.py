import yaml
import os

class YamlReader(object):
    def __init__(self, filename):
        self.f = open(filename, 'r')
        self.dataMap = yaml.load(self.f)
        self.f.close()
        
    def get_calls(self):
        return self.dataMap