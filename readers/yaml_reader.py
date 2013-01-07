import yaml
import os

from endpoint.settings import SPECS_PATH

class YamlReader(object):
    def __init__(self, spec):
        self.f = open(os.path.join(SPECS_PATH, spec + '.yml'), 'r')
        self.dataMap = yaml.load(self.f)
        self.f.close()
        
    def get_calls(self):
        return self.dataMap