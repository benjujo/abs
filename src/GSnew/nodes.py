import abc


class TypeException(Exception):
    pass


class TypeNode(abc.ABC):
    def __init__(self, value):
        self.value = value


# ------ Constants ------

class ConstantNode(TypeNode):
    def __init__(self, name: str, etype: int):
        self.name = name
        self.etype = etype
        
    def _compile(self, defs, target):
        const_name = self.name
        raw_element = defs[const_name]
        
        const_template = f"""
{const_name} = elements.load_element('{raw_element}', {self.etype})
const['{const_name}'] = {const_name}
"""
        return const_template
    
    def compile_proof(self, defs, target):
        return self._compile(defs, target)
    
    def compile_verify(self, defs, target):
        return self._compile(defs, target)

class ConstantG1Node(ConstantNode):
    def __init__(self, name: str):
        super().__init__(name, 1)


class ConstantG2Node(ConstantNode):
    def __init__(self, name: str):
        super().__init__(name, 2)


class ConstantGTNode(ConstantNode):
    def __init__(self, name: str):
        super().__init__(name, 3)


class ConstantZpNode(ConstantNode):
    def __init__(self, name: str):
        super().__init__(name, 0)


# ------ Variables ------
# , position: int=None

class VariableNode(TypeNode):
    # VTYPE: (ETYPE, VariableArray, CommitmentArray)
    VTYPES = {
        1: (1, "X", "c"),
        2: (2, "Y", "d"),
        -1: (0, "x", "c_prime"),
        0: (0, "y", "d_prime")
    }
    def __init__(self, name: str, vtype: int):
        self.name = name
        self.vtype = vtype

    
    def compile_proof(self, defs, target):
        var_name = self.name
        vtype_tuple = VariableNode.VTYPES[self.vtype]
        raw_element = defs[var_name]
        
        var_template = f"""
{var_name} = elements.load_element('{raw_element}', {vtype_tuple[0]})
{vtype_tuple[1]} = {vtype_tuple[1]}.append('{var_name}', {var_name})
"""
        return var_template
    
    def compile_verify(self, defs, target):
        var_name = self.name
        vtype_tuple = VariableNode.VTYPES[self.vtype]
        raw_element = defs[var_name]
        var_template = f"""
{var_name} = [elements.load_element('{raw_element[0]}', {vtype_tuple[0]}), elements.load_element('{raw_element[1]}', {vtype_tuple[0]})]
{vtype_tuple[2]} = {vtype_tuple[2]}.append('{var_name}', {var_name}, True)
"""
        return var_template


class VariableG1Node(VariableNode):
    def __init__(self, name: str):
        super().__init__(name, 1)


class VariableG2Node(VariableNode):
    def __init__(self, name: str):
        super().__init__(name, 2)


class VariableZpNode(VariableNode):
    def __init__(self, name: str, vtype: int = None):
        super().__init__(name, vtype)
        

class VariableZpLeftNode(VariableZpNode):
    def __init__(self, name: str):
        super().__init__(name, -1)


class VariableZpRightNode(VariableZpNode):
    def __init__(self, name: str):
        super().__init__(name, 0)


# ------ Mul expressions ------
class MulNode(TypeNode):
    def __init__(self, left: str, right: str, gamma: str = None):
        self.left = left
        self.right = right
        self.gamma = gamma


class MulPPENode(MulNode):
    def type_check(self, vars, consts):
        left = {**vars, **consts}[self.left]
        right = {**vars, **consts}[self.right]
        if self.gamma:
            gamma = consts[self.gamma]
            if not (isinstance(gamma, ConstantZpNode)):
                raise TypeError('gamma is not a ZpConstant')
            if not (isinstance(left, VariableG1Node) and isinstance(right, VariableG2Node)):
                raise TypeError('Not VV')
            return
        if not ((isinstance(left, VariableG1Node) and isinstance(right, ConstantG2Node)) or
                (isinstance(left, ConstantG1Node) and isinstance(right, VariableG2Node))):
            raise TypeError('Neither CV or VC')


class MulMS1Node(MulNode):
    def type_check(self, vars, consts):
        left = {**vars, **consts}[self.left]
        right = {**vars, **consts}[self.right]
        if self.gamma:
            gamma = consts[self.gamma]
            if not (isinstance(gamma, ConstantZpNode)):
                raise TypeError('gamma is not a ZpConstant')
            if not (isinstance(left, VariableZpNode) and isinstance(right, VariableG1Node)):
                raise TypeError('Not VV')
            return
        if not ((isinstance(left, VariableZpNode) and isinstance(right, ConstantG1Node)) or
                (isinstance(left, ConstantZpNode) and isinstance(right, VariableG1Node))):
            raise TypeError('Neither CV or VC')


class MulMS2Node(MulNode):
    def type_check(self, vars, consts):
        left = {**vars, **consts}[self.left]
        right = {**vars, **consts}[self.right]
        if self.gamma:
            gamma = consts[self.gamma]
            if not (isinstance(gamma, ConstantZpNode)):
                raise TypeError('gamma is not a ZpConstant')
            if not (isinstance(left, VariableZpNode) and isinstance(right, VariableG2Node)):
                raise TypeError('Not VV')
            return
        if not ((isinstance(left, VariableZpNode) and isinstance(right, ConstantG2Node)) or
                (isinstance(left, ConstantZpNode) and isinstance(right, VariableG2Node))):
            raise TypeError('Neither CV or VC')


class MulQENode(MulNode):
    def type_check(self, vars, consts):
        left = {**vars, **consts}[self.left]
        right = {**vars, **consts}[self.right]
        if self.gamma:
            gamma = consts[self.gamma]
            if not (isinstance(gamma, ConstantZpNode)):
                raise TypeError('gamma is not a ZpConstant')
            if not (isinstance(left, VariableZpNode) and isinstance(right, VariableG1Node)):
                raise TypeError('Not VV')
            return
        if not ((isinstance(left, VariableZpNode) and isinstance(right, ConstantZpNode)) or
                (isinstance(left, ConstantZpNode) and isinstance(right, VariableZpNode))):
            raise TypeError('Neither CV or VC')

# ------ Equations ------

class EquationNode(TypeNode):
    def __init__(self, eq_muls, target):
        self.eq_muls = eq_muls
        self.target = target

    def __iter__(self):
        return iter(self.eq_muls)


class PPEquationNode(EquationNode):
    def type_check(self, vars, consts):
        target = consts[self.target]
        if not isinstance(target, ConstantGTNode):
            raise TypeError('Not PPE equation.')
        for eq_mul in self:
            eq_mul.type_check(vars, consts)
            
    def compute_constants(self, X, Y, x, y, consts_dict):
        # A*Y + X*B + X*g*Y = T
        m = len(X)
        n = len(Y)
        A = [0] * n
        B = [0] * m
        g = [[0] * n] * m
        for i,var in enumerate(X):
            # find the eq_mul that has var as left and no gamma
            eq_mul = next((eq_mul for eq_mul in self if eq_mul.left == var.name and not eq_mul.gamma), None)
            B[i] = eq_mul.right if eq_mul else "elements.G2Element.zero()"
        for j,var in enumerate(Y):
            # find the eq_mul that has var as right and not gamma
            eq_mul = next((eq_mul for eq_mul in self if eq_mul.right == var.name and not eq_mul.gamma), None)
            A[j] = eq_mul.left if eq_mul else "elements.G1Element.zero()"
        for i,xvar in enumerate(X):
            for j,yvar in enumerate(Y):
                eq_mul = next((eq_mul for eq_mul in self if eq_mul.left == xvar.name and eq_mul.right == yvar.name), None)
                if eq_mul:
                    g[i][j] = eq_mul.gamma if eq_mul.gamma else "elements.ZpElement.zero()"
                else:
                    g[i][j] = "elements.ZpElement.zero()"
        self.a = A
        self.b = B
        self.g = g
        
            
    def compile_proof(self, defs, target):
        eq_template = f"""
eq = Equation([{', '.join(self.a)}], [{', '.join(self.b)}], [{', '.join(['[' + ', '.join(row) + ']' for row in self.g])}], {self.target}, 3)
eqs.append(eq)
"""
        return eq_template
        
    def compile_verify(self, defs, target):
        eq_template = f"""
eq = Equation([{', '.join(self.a)}], [{', '.join(self.b)}], [{', '.join(['[' + ', '.join(row) + ']' for row in self.g])}], {self.target}, 3)
eqs.append(eq)
"""
        return eq_template


class MS1EquationNode(EquationNode):
    pass


class MS2EquationNode(EquationNode):
    pass


class QEquationNode(EquationNode):
    def type_check(self, vars, consts):
        target = consts[self.target]
        if not isinstance(target, ConstantZpNode):
            raise TypeError('Not QE equation.')
        for eq_mul in self:
            eq_mul.type_check(vars, consts)
            
    def compute_constants(self, X, Y, x, y, consts_dict):
        # a*y + x*b + x*g*y = t
        m = len(x)
        n = len(y)
        A = [0] * n
        B = [0] * m
        g = [[0] * n] * m
        for i,var in enumerate(x):
            # find the eq_mul that has var as left
            eq_mul = next((eq_mul for eq_mul in self if eq_mul.left == var.name), None)
            B[i] = eq_mul.right if eq_mul else "elements.ZpElement.zero()"
        for j,var in enumerate(y):
            # find the eq_mul that has var as right
            eq_mul = next((eq_mul for eq_mul in self if eq_mul.right == var.name), None)
            A[j] = eq_mul.left if eq_mul else "elements.ZpElement.zero()"
        for i,xvar in enumerate(x):
            for j,yvar in enumerate(y):
                eq_mul = next((eq_mul for eq_mul in self if eq_mul.left == xvar.name and eq_mul.right == yvar.name), None)
                if eq_mul:
                    g[i][j] = eq_mul.gamma if eq_mul.gamma else "elements.ZpElement.zero()"
        self.a = A
        self.b = B
        self.g = g
        
    def compile_proof(self, defs, target):
        eq_template = f"""
eq = Equation([{', '.join(self.a)}], [{', '.join(self.b)}], [{'], ['.join(['[' + ', '.join(row) + ']' for row in self.g])}], {self.target}, 0)
eqs.append(eq)
"""
        return eq_template
    
    def compile_verify(self, defs, target):
        eq_template = f"""
eq = Equation([{', '.join(self.a)}], [{', '.join(self.b)}], [{'], ['.join(['[' + ', '.join(row) + ']' for row in self.g])}], {self.target}, 0)
eqs.append(eq)
"""
        return eq_template


class GSNode(abc.ABC):
    def __init__(self, vars, consts, eqs):
        self.vars = vars
        self.consts = consts
        self.eqs = eqs

    def assign_eqs_type(self, consts_dict):
        for i,eq in enumerate(self.eqs):
            target = consts_dict[eq.target]
            if isinstance(target, ConstantGTNode):
                eq_muls = [MulPPENode(eq_mul.left, eq_mul.right, eq_mul.gamma) for eq_mul in eq.eq_muls]
                self.eqs[i] = PPEquationNode(eq_muls, eq.target)
            if isinstance(target, ConstantG1Node):
                eq_muls = [MulMS1Node(eq_mul.left, eq_mul.right, eq_mul.gamma) for eq_mul in eq.eq_muls]
                self.eqs[i] = MS1EquationNode(eq_muls, eq.target)
            if isinstance(target, ConstantG2Node):
                eq_muls = [MulMS2Node(eq_mul.left, eq_mul.right, eq_mul.gamma) for eq_mul in eq.eq_muls]
                self.eqs[i] = MS2EquationNode(eq_muls, eq.target)
            if isinstance(target, ConstantZpNode):
                eq_muls = [MulQENode(eq_mul.left, eq_mul.right, eq_mul.gamma) for eq_mul in eq.eq_muls]
                self.eqs[i] = QEquationNode(eq_muls, eq.target)
                
    def assign_vars_zp(self, vars_dict):
        for eq in self.eqs:
            if isinstance(eq, PPEquationNode):
                continue
            if isinstance(eq, MS1EquationNode):
                for eq_mul in eq:
                    left = vars_dict.get(eq_mul.left)
                    if left is not None and isinstance(left, VariableZpNode):
                        if isinstance(left, VariableZpLeftNode):
                            raise TypeException('ZpLeft in right position')
                        if isinstance(left, VariableZpRightNode):
                            continue
                        vars_dict[eq_mul.left] = VariableZpRightNode(eq_mul.left)
            if isinstance(eq, MS2EquationNode):
                for eq_mul in eq:
                    right = vars_dict.get(eq_mul.right)
                    if right is not None and isinstance(right, VariableZpNode):
                        if isinstance(right, VariableZpRightNode):
                            raise TypeException('ZpRight in left position')
                        if isinstance(right, VariableZpLeftNode):
                            continue
                        vars_dict[eq_mul.right] = VariableZpLeftNode(eq_mul.right)
            if isinstance(eq, QEquationNode):
                for eq_mul in eq:
                    left = vars_dict.get(eq_mul.left)
                    if left is not None and isinstance(left, VariableZpNode):
                        if isinstance(left, VariableZpRightNode):
                            raise TypeException('ZpRight in left position')
                        if isinstance(left, VariableZpLeftNode):
                            continue
                        vars_dict[eq_mul.left] = VariableZpLeftNode(eq_mul.left)
                    
                    right = vars_dict.get(eq_mul.right)
                    if right is not None and isinstance(right, VariableZpNode):
                        if isinstance(right, VariableZpLeftNode):
                            raise TypeException('ZpLeft in right position')
                        if isinstance(right, VariableZpRightNode):
                            continue
                        vars_dict[eq_mul.right] = VariableZpRightNode(eq_mul.right)

    def type_check(self):
        vars_dict = {v.name:v for v in self.vars}
        consts_dict = {c.name:c for c in self.consts}
        self.assign_eqs_type(consts_dict)
        self.assign_vars_zp(vars_dict)
        X = [v for v in vars_dict.values() if isinstance(v, VariableG1Node)]
        Y = [v for v in vars_dict.values() if isinstance(v, VariableG2Node)]
        x = [v for v in vars_dict.values() if isinstance(v, VariableZpLeftNode)]
        y = [v for v in vars_dict.values() if isinstance(v, VariableZpRightNode)]
        for eq in self.eqs:
            eq.type_check(vars_dict, consts_dict)
            eq.compute_constants(X, Y, x, y, consts_dict)
        
        self.X = X
        self.Y = Y
        self.x = x
        self.y = y
        

    def compile_proof(self, defs, crs_dict, target):
        prelude = f"""from framework import CRS, Equation, equations, proof
from utils import NamedArray
import {target} as elements

crs = CRS.from_json({crs_dict})

X = NamedArray([])
Y = NamedArray([])
x = NamedArray([])
y = NamedArray([])

eqs = equations()
const = {{}}
"""
        script = prelude
        #for var in self.vars:
        #    script += var.compile_proof(defs, target)
        for var in self.X:
            script += var.compile_proof(defs, target)
        for var in self.Y:
            script += var.compile_proof(defs, target)
        for var in self.x:
            script += var.compile_proof(defs, target)
        for var in self.y:
            script += var.compile_proof(defs, target)
        
        for const in self.consts:
            script += const.compile_proof(defs, target)
        for eq in self.eqs:
            script += eq.compile_proof(defs, target)
            
        script += "p=proof(crs, eqs, X, Y, x, y)\np.consts=const\nprint(p.to_json())\n"
        return script



    def compile_verify(self, defs, crs_filename, target):
        prelude = f"""from framework import CRS, Equation, equations, verify
from utils import NamedArray, UnamedArray
import numpy as np
import {target} as elements

crs = CRS.from_json({crs_filename})

c = NamedArray([])
d = NamedArray([])
c_prime = NamedArray([])
d_prime = NamedArray([])


eqs = equations()
const = {{}}
"""

        
        script = prelude
        #for var in self.vars:
        #    script += var.compile_verify(defs, target)
        for var in self.X:
            script += var.compile_verify(defs, target)
        for var in self.Y:
            script += var.compile_verify(defs, target)
        for var in self.x:
            script += var.compile_verify(defs, target)
        for var in self.y:
            script += var.compile_verify(defs, target)
        for const in self.consts:
            script += const.compile_verify(defs, target)
            
        script += "pis = [\n"
        for pi in defs['pis']:
            script += "    UnamedArray([\n"
            for b in pi:
                if isinstance(b, str):
                    script += f"            elements.load_element('{b}', 1),\n"
                else:
                    script += "        [\n"
                    for e in b:
                        script += f"            elements.load_element('{e}', 2),\n"
                    script += "        ],\n"
            script += f"    ]),\n"
        script += "]\n"
            
        script += "thetas = [\n"
        for pi in defs['thetas']:
            script += "    UnamedArray([\n"
            for b in pi:
                if isinstance(b, str):
                    script += f"        elements.load_element('{b}', 1),\n"
                else:
                    script += "        [\n"
                    for e in b:
                        script += f"            elements.load_element('{e}', 1),\n"
                    script += "        ],\n"
            script += f"    ]),\n"
        script += "]\n"
        
        
            
        for eq in self.eqs:
            script += eq.compile_verify(defs, target)
            
        script += "v=verify(crs, eqs, c, c_prime, d, d_prime, pis, thetas)\nprint(v)\n"
        return script


