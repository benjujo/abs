
from lark import Token, Transformer
import nodes as gsnodes


class ASTTransformer(Transformer):
    def start(self, items):
        vars = items[0]
        consts = items[1]
        eqs = items[2]
        return gsnodes.GSNode(vars, consts, eqs)

    def NAME(self, item):
        return item.value

    def vars(self, items):
        return items

    def var(self, items):
        name, element_type = items
        if element_type == "G1":
            return gsnodes.VariableG1Node(name)
        elif element_type == "G2":
            return gsnodes.VariableG2Node(name)
        elif element_type == "ZP":
            return gsnodes.VariableZpNode(name)
        raise Exception("Unknown variable element type")

    def consts(self, items):
        return items

    def const(self, items):
        name, element_type = items
        if element_type == "G1":
            return gsnodes.ConstantG1Node(name)
        elif element_type == "G2":
            return gsnodes.ConstantG2Node(name)
        elif element_type == "ZP":
            return gsnodes.ConstantZpNode(name)
        elif element_type == "GT":
            return gsnodes.ConstantGTNode(name)
        raise Exception("Unknown constant element type")

    def eqs(self, items):
        return items

    def eq(self, items):
        *eq_exprs, name, eq_type = items
        if eq_type == "PPE":
            return gsnodes.PPEquationNode([gsnodes.ExpressionPPENode(*eq_expr) for eq_expr in eq_exprs], gsnodes.ConstantGTNode(name))
        elif eq_type == "MS1":
            return gsnodes.MS1EquationNode([gsnodes.ExpressionMS1ENode(*eq_expr) for eq_expr in eq_exprs], gsnodes.ConstantG1Node(name))
        elif eq_type == "MS2":
            return gsnodes.MS2EquationNode([gsnodes.ExpressionMS2ENode(*eq_expr) for eq_expr in eq_exprs], gsnodes.ConstantG2Node(name))
        elif eq_type == "QE":
            return gsnodes.QEquationNode([gsnodes.ExpressionQENode(*eq_expr) for eq_expr in eq_exprs], gsnodes.ConstantZpNode(name))
        raise Exception("Unknown equation type")

    def eq_expr(self, items):
        # TODO: Get context from eq and types from names
        if len(items) == 2:
            name1, name2 = items
            return name1, name2
        if len(items) == 3:
            name1, name2, name3 = items
            return name2, name3, name1
        raise Exception("Unknown length expression")