import abc


class TypeException(Exception):
    pass


class TypeNode(abc.ABC):
    def __init__(self, value):
        self.value = value


class ElementNode(TypeNode):
    def evaluate(self):
        return f'Element({self.value})'


class G1Node(ElementNode):
    def evaluate(self):
        return f'G1({self.value})'


class G2Node(ElementNode):
    def evaluate(self):
        return f'G2({self.value})'


class GTNode(ElementNode):
    def evaluate(self):
        return f'GT({self.value})'


class ZpNode(ElementNode):
    def evaluate(self):
        return f'Zp({self.value})'

# ------ Constants ------

class ConstantNode(TypeNode):
    def __init__(self, name: str):
        self.name = name

class ConstantG1Node(ConstantNode):
    pass


class ConstantG2Node(ConstantNode):
    pass


class ConstantGTNode(ConstantNode):
    pass


class ConstantZpNode(ConstantNode):
    pass


# ------ Variables ------
# , position: int=None

class VariableNode(TypeNode):
    def __init__(self, name: str):
        self.name = name


class VariableG1Node(VariableNode):
    pass


class VariableG2Node(VariableNode):
    pass


class VariableZpNode(VariableNode):
    _valid = False


class VariableZpLeftNode(VariableZpNode):
    pass


class VariableZpRightNode(VariableZpNode):
    pass


# ------ Expressions ------
class ExpressionNode(TypeNode):
    def __init__(self, left: str, right: str, gamma: str = None):
        self.left = left
        self.right = right
        self.gamma = gamma


class ExpressionPPENode(ExpressionNode):
    def type_check(self, vars):
        left = vars[self.left]
        right = vars[self.right]
        assert (isinstance(left, VariableG1Node) and isinstance(right, ConstantG2Node) and (self.gamma==None)) or \
        (isinstance(left, ConstantG1Node) and isinstance(right, VariableG2Node) and (self.gamma==None))
        
        
    


class ExpressionMS1ENode(ExpressionNode):
    pass


class ExpressionMS2ENode(ExpressionNode):
    pass


class ExpressionQENode(ExpressionNode):
    pass

# ------ Equations ------

class EquationNode(TypeNode):
    def __init__(self, eq_exprs, target):
        self.eq_exprs = eq_exprs
        self.target = target

    def __iter__(self):
        return iter(self.eq_exprs)

class PPEquationNode(EquationNode):
    def type_check(self, vars_dict):
        assert isinstance(self.target, ConstantGTNode)
        for eq_expr in self:
            eq_expr.type_check(vars_dict)


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

    def type_check(self):
        for eq in self.eqs:
            eq.type_check({**{v.name:v for v in self.vars}, **{c.name:c for c in self.consts}})

    def compile_proof(self, target):
        pass

    def compile_verification(self, target):
        pass

