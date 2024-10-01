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
{const_name} = load_element('{const_name}', 1)
const['{const_name}'] = {const_name}
"""
        return const_template


class ConstantG2Node(ConstantNode):
    def compile_proof(self, target):
        const_name = self.name
        const_template = f"""
{const_name} = load_element('{const_name}', 2)
const['{const_name}'] = {const_name}
"""
        return const_template


class ConstantGTNode(ConstantNode):
    def compile_proof(self, target):
        const_name = self.name
        const_template = f"""
{const_name} = load_element('{const_name}', 3)
const['{const_name}'] = {const_name}
"""
        return const_template


class ConstantZpNode(ConstantNode):
    def compile_proof(self, target):
        const_name = self.name
        const_template = f"""
{const_name} = load_element('{const_name}', 0)
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
{var_name} = load_element('{var_name}', 1)
X.append(('{var_name}', {var_name}))
"""
        return var_template


class VariableG2Node(VariableNode):
    def compile_proof(self, target):
        var_name = self.name
        var_template = f"""
{var_name} = load_element('{var_name}', 2)
Y.append(('{var_name}', {var_name}))
"""
        return var_template


class VariableZpNode(VariableNode):
    _valid = False


class VariableZpLeftNode(VariableZpNode):
    def compile_proof(self, target):
        var_name = self.name
        var_template = f"""
{var_name} = load_element('{var_name}', 0)
x.append(('{var_name}', {var_name}))
"""
        return var_template


class VariableZpRightNode(VariableZpNode):
    def compile_proof(self, target):
        var_name = self.name
        var_template = f"""
{var_name} = load_element('{var_name}', 0)
y.append(('{var_name}', {var_name}))
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
        left = {**vars, **consts}[self.left]
        right = {**vars, **consts}[self.right]
        if self.gamma:
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
        left = {**vars, **consts}[self.left]
        right = {**vars, **consts}[self.right]
        if self.gamma:
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
        left = {**vars, **consts}[self.left]
        right = {**vars, **consts}[self.right]
        if self.gamma:
            gamma = consts[self.gamma]
            if not (isinstance(gamma, ConstantZpNode)):
                raise TypeError('gamma is not a ZpConstant')
            if not (isinstance(left, VariableZpNode) and isinstance(right, VariableG1Node)):
                raise TypeError('Not VV')
        if not (isinstance(left, VariableZpNode) and isinstance(right, ConstantZpNode)) or \
        (isinstance(left, ConstantZpNode) and isinstance(right, VariableZpNode)):
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
            # find the eq_mul that has var as left
            eq_mul = next((eq_mul for eq_mul in self if eq_mul.left == var.name), None)
            if eq_mul:
                B[i] = eq_mul.right
        for j,var in enumerate(Y):
            # find the eq_mul that has var as right
            eq_mul = next((eq_mul for eq_mul in self if eq_mul.right == var.name), None)
            if eq_mul:
                A[j] = consts_dict[eq_mul.left]
        for i,xvar in enumerate(X):
            for j,yvar in enumerate(Y):
                eq_mul = next((eq_mul for eq_mul in self if eq_mul.left == xvar.name and eq_mul.right == yvar.name), None)
                if eq_mul:
                    g[i][j] = consts_dict[eq_mul.gamma]
        self.a = A
        self.b = B
        self.g = g
        
            
    def compile_proof(self, target):
        eq_template = f"""
eq = Equation([{', '.join(self.a)}], [{', '.join(self.b)}], [{'], ['.join(['[' + ', '.join(row) + ']' for row in self.g])}], {self.target}, 3)
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
            if eq_mul:
                B[i] = eq_mul.right
        for j,var in enumerate(y):
            # find the eq_mul that has var as right
            eq_mul = next((eq_mul for eq_mul in self if eq_mul.right == var.name), None)
            if eq_mul:
                A[j] = consts_dict[eq_mul.left]
        for i,xvar in enumerate(x):
            for j,yvar in enumerate(y):
                eq_mul = next((eq_mul for eq_mul in self if eq_mul.left == xvar.name and eq_mul.right == yvar.name), None)
                if eq_mul:
                    g[i][j] = consts_dict[eq_mul.gamma]
        self.a = A
        self.b = B
        self.g = g
        
    def compile_proof(self, target):
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
        

    def compile_proof(self, target):
        prelude = f"""
from framework import load_element, load_crs, vars_array, Equation, equations, proof

CRS = load_crs()

X = []
Y = []
x = []
y = []

eqs = equations()
const = {{}}
"""
        script = prelude
        #for var in self.vars:
        #    script += var.compile_proof(target)
        for var in self.X:
            script += var.compile_proof(target)
        for var in self.y:
            script += var.compile_proof(target)
        for var in self.x:
            script += var.compile_proof(target)
        for var in self.y:
            script += var.compile_proof(target)
        
        for const in self.consts:
            script += const.compile_proof(target)
        for eq in self.eqs:
            script += eq.compile_proof(target)
            
        script += "variables = vars_array(X,Y,x,y)\n"
        script += "p=proof(CRS, eqs, variables)\n"
        return script



    def compile_verification(self, target):
        prelude = f"""
from framework import load_element, load_crs, vars_array, Equation, equations, proof

CRS = load_crs()

C = []
D = []
c = []
d = []

eqs = equations()
const = {{}}
"""
        script = prelude
        for var in self.vars:
            script += var.compile_proof(target)
        for const in self.consts:
            script += const.compile_proof(target)
        for eq in self.eqs:
            script += eq.compile_proof(target)
            
        script += "variables = vars_array(X,Y,x,y)\n"
        script += "p=proof(CRS, eqs, variables)\n"
        return script


