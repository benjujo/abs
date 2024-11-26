
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
        *mul_eqs, name = items
        # Without typing
        return gsnodes.EquationNode([gsnodes.MulNode(*mul_eq) for mul_eq in mul_eqs], name)
        

    def mul_eq(self, items):
        # TODO: Get context from eq and types from names
        if len(items) == 2:
            name1, name2 = items
            return name1, name2
        if len(items) == 3:
            name1, name2, name3 = items
            return name2, name3, name1
        raise Exception("Unknown length expression")
