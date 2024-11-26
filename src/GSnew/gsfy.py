import dis
from functools import wraps
import os
import json


def json_serializer(obj):
    if hasattr(obj, '__json__'):
        return obj.__json__()
    else:
        # For non-serializable objects, use the default JSON serialization
        return json.JSONEncoder().default(obj)


def gsfy(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        gs_mode = os.environ.get("GS_MODE", None)
        if gs_mode not in ["PROOF", "VERIFY"]:
            print("GS_MODE must be set to PROOF or VERIFY")
            return func(*args, **kwargs)
        
        # Execute the function and capture its local variables dynamically
        local_vars = {}

        def capture_locals(frame, event, arg):
            """Helper to capture local variables during function execution."""
            if event == "return":
                local_vars.update(frame.f_locals)
            return capture_locals

        # Use sys.settrace to capture locals during execution
        import sys
        sys.settrace(capture_locals)
        result = func(*args, **kwargs)
        sys.settrace(None)

        # Collect variable names from bytecode
        bytecode_vars = {
            instr.argval
            for instr in dis.get_instructions(func)
            if instr.opname in {"LOAD_FAST", "STORE_FAST", "LOAD_GLOBAL", "STORE_GLOBAL"}
        }

        # Match bytecode variables to their runtime values
        collected_values = {var: local_vars.get(var, None) for var in bytecode_vars}
        print("Variables and Values:", collected_values)
        
        gs_string = collected_values.get('GS_STRING', None)
        if not gs_string:
            return result
        
        
        
        definitions_file = args.definitions
        output_file = args.output
        
        parser = GSParser()
        p = parser.parse(gs_string)
            
        t = ASTTransformer()
        r = t.transform(p)

        r.type_check()
        if gs_mode == "PROOF":
            # Create JSON with definitions from consts and vars
            definitions = {}
            variables = r.vars
            constants = r.consts
            
            for var in variables:
                definitions[var.name] = collected_values[var.name]
            for const in constants:
                definitions[const.name] = collected_values[const.name]
                
            with open(definitions_file, "w") as f:
                f.write(json.dumps(definitions, default=json_serializer))
                
            
            
            compiled = r.compile_proof(definitions, None)
            
            with open(output_file, 'w') as f:
                f.write(compiled)
        else:
            compiled = r.compile_verify(definitions, None)

        with open(output_file, 'w') as f:
            f.write(p)
            
        
        
        

        return result

    return wrapper