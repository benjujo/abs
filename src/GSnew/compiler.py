import importlib
import jinja2
import nodes


variables_template ="""
{{ var.name }} = Variable({{ var.name }}, {{ var.element }}.from_bytes(b'{{ defs_json[var.name] }}'))
vars.append({{ var.name }})
"""

def compile_template(template, context):
    """Compile a template
    """
    template = jinja2.Template(template)
    return template.render(context)


def compile(gs_node: nodes.GSNode, target: str):
    """Compile a GSNode to a target language
    """
    script = ""
    
    variables = gs_node.vars
    consts = gs_node.consts
    eqs = gs_node.eqs
    
    with open(defs_file, "r") as f:
        defs_json = json.load(f)
    
    for var in gs_node.vars:
        script += compile_template(variables_template, {"var": var, "defs_json": defs_json})
    
