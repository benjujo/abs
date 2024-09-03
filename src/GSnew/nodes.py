import abc


class TypeException(Exception):
    pass


class TypeNode(abc.ABC):
    def __init__(self, value):
        self.value = value


# ------ Constants ------

class ConstantNode(TypeNode):
    def __init__(self, name: str):
        self.name = name

class ConstantG1Node(ConstantNode):
    def compile_proof(self, target):
        const_name = self.name
        const_template = f"""
{const_name} = Constant(load_element({const_name}, 1))
const['{const_name}'] = {const_name}
"""
        return const_template


class ConstantG2Node(ConstantNode):
    def compile_proof(self, target):
        const_name = self.name
        const_template = f"""
{const_name} = Constant(load_element({const_name}, 2))
const['{const_name}'] = {const_name}
"""
        return const_template


class ConstantGTNode(ConstantNode):
    def compile_proof(self, target):
        const_name = self.name
        const_template = f"""
{const_name} = Constant(load_element({const_name}, 3))
const['{const_name}'] = {const_name}
"""
        return const_template


class ConstantZpNode(ConstantNode):
    def compile_proof(self, target):
        const_name = self.name
        const_template = f"""
{const_name} = Constant(load_element({const_name}, 0))
const['{const_name}'] = {const_name}
"""
        return const_template


# ------ Variables ------
# , position: int=None

class VariableNode(TypeNode):
    def __init__(self, name: str):
        self.name = name

    '''
    def compile_proof(self, target):
        var_template = """
{var_name} = Variable(load_element({var_name}, element_type), var_type)
vars['{var_name}'] = {var_name}
"""
    '''


class VariableG1Node(VariableNode):
    def compile_proof(self, target):
        var_name = self.name
        var_template = f"""
{var_name} = Variable(load_element('{var_name}', 1), 1)
X.append({var_name})
"""
        return var_template


class VariableG2Node(VariableNode):
    def compile_proof(self, target):
        var_name = self.name
        var_template = f"""
{var_name} = Variable(load_element('{var_name}', 2), 2)
Y.append({var_name})
"""
        return var_template


class VariableZpNode(VariableNode):
    _valid = False


class VariableZpLeftNode(VariableZpNode):
    def compile_proof(self, target):
        var_name = self.name
        var_template = f"""
{var_name} = Variable(load_element('{var_name}', 0), -1)
x.append({var_name})
"""
        return var_template


class VariableZpRightNode(VariableZpNode):
    def compile_proof(self, target):
        var_name = self.name
        var_template = f"""
{var_name} = Variable(load_element('{var_name}', 0), 0)
y.append({var_name})
"""
        return var_template


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
        if not (isinstance(left, VariableG1Node) and isinstance(right, ConstantG2Node)) or \
        (isinstance(left, ConstantG1Node) and isinstance(right, VariableG2Node)):
            raise TypeError('Neither CV or VC')


class MulMS1Node(MulNode):
    def type_check(self, vars, consts):
        left = vars[self.left]
        right = vars[self.right]
        if self.gammma:
            gamma = consts[self.gamma]
            if not (isinstance(gamma, ConstantZpNode)):
                raise TypeError('gamma is not a ZpConstant')
            if not (isinstance(left, VariableZpNode) and isinstance(right, VariableG1Node)):
                raise TypeError('Not VV')
        if not (isinstance(left, VariableZpNode) and isinstance(right, ConstantG1Node)) or \
        (isinstance(left, ConstantZpNode) and isinstance(right, VariableG1Node)):
            raise TypeError('Neither CV or VC')


class MulMS2Node(MulNode):
    def type_check(self, vars, consts):
        left = vars[self.left]
        right = vars[self.right]
        if self.gammma:
            gamma = consts[self.gamma]
            if not (isinstance(gamma, ConstantZpNode)):
                raise TypeError('gamma is not a ZpConstant')
            if not (isinstance(left, VariableZpNode) and isinstance(right, VariableG2Node)):
                raise TypeError('Not VV')
        if not (isinstance(left, VariableZpNode) and isinstance(right, ConstantG2Node)) or \
        (isinstance(left, ConstantZpNode) and isinstance(right, VariableG2Node)):
            raise TypeError('Neither CV or VC')


class MulQENode(MulNode):
    def type_check(self, vars, consts):
        left = vars[self.left]
        right = vars[self.right]
        if self.gammma:
            gamma = consts[self.gamma]
            if not (isinstance(gamma, ConstantZpNode)):
                raise TypeError('gamma is not a ZpConstant')
            if not (isinstance(left, VariableZpNode) and isinstance(right, VariableG1Node)):
                raise TypeError('Not VV')
        if not (isinstance(left, VariableZpNode) and isinstance(right, ConstantG1Node)) or \
        (isinstance(left, ConstantZpNode) and isinstance(right, VariableG1Node)):
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
        n = len(X)
        m = len(Y)
        A = [0] * m
        B = [0] * n
        g = [[0] * n] * m
        for i,var in enumerate(X):
            # find the eq_mul that has var as left
            eq_mul = next((eq_mul for eq_mul in self if eq_mul.left == var.name), None)
            if eq_mul:
                B[i] = eq_mul.right
        for i,var in enumerate(Y):
            # find the eq_mul that has var as right
            eq_mul = next((eq_mul for eq_mul in self if eq_mul.right == var.name), None)
            if eq_mul:
                A[i] = eq_mul.left
        for i,xvar in enumerate(X):
            for j,yvar in enumerate(Y):
                eq_mul = next((eq_mul for eq_mul in self if eq_mul.left == xvar.name and eq_mul.right == yvar.name), None)
                if eq_mul:
                    g[i][j] = eq_mul.gamma
        self.a = A
        self.b = B
        self.g = g
        
            
    def compile_proof(self, target):
        eq_template = f"""
eqs.append(({self.a}, {self.b}, {self.g}, {self.target}))
"""
        return eq_template


class MS1EquationNode(EquationNode):
    pass


class MS2EquationNode(EquationNode):
    pass


class QEquationNode(EquationNode):
    pass


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

    def type_check(self):
        vars_dict = {v.name:v for v in self.vars}
        consts_dict = {c.name:c for c in self.consts}
        self.assign_eqs_type(consts_dict)
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
        

    def compile_proof(self, target):
        prelude = f"""
from nodes import *
from framework import load_element, load_crs, proof, Variable, Constant

CRS = load_crs()

X = []
Y = []
x = []
y = []

eqs = []
"""
        script = prelude
        for var in self.vars:
            script += var.compile_proof(target)
        for const in self.consts:
            script += const.compile_proof(target)
        for eq in self.eqs:
            script += eq.compile_proof(target)
            
        script += "proof(CRS, eqs, X, Y, x, y)"
        return script



    def compile_verification(self, target):
        pass

