from charm.toolbox.msp import MSP as CMSP
from GS.elements import ZpElement, group
from typing import List
import json

class MSP:
    def __init__(self, index:List[str], msp: List[List[int]]):
        self.index = index
        self._msp = msp
    
    @property
    def width(self):
        return len(self.msp[0])

    @property
    def msp(self) -> List[List[ZpElement]]:
        return [[ZpElement.init(i) for i in j] for j in self._msp]

    @classmethod
    def from_policy_str(cls, policy_str: str):
        cmsp = CMSP(group)
        tree = cmsp.createPolicy(policy_str)

        dict_msp = cmsp.convert_policy_to_msp(tree)

        index = list(map(cmsp.strip_index, dict_msp.keys()))
        width = len(max(dict_msp.values(), key=len))
        #matrix = [list(map(ZpElement.init, i)) + [ZpElement.zero()] * (width - len(i)) for i in dict_msp.values()]
        matrix = [list(i) + [0] * (width - len(i)) for i in dict_msp.values()]

        return cls(index, matrix)

    def serialize(self):
        return json.dumps({
            'index': self.index,
            'msp': self._msp
        })

    @classmethod
    def from_json(cls, json_str):
        msp_dict = json.loads(json_str)
        index = msp_dict['index']
        msp = msp_dict['msp'] 
        return cls(index, msp)
