import argparse
from parser import GSParser
from ast_builder import ASTTransformer
from gsfy import gsfy
import os


def prove(args):
    input_file = args.input
    definitions_file = args.definitions
    output_file = args.output
    
    parser=GSParser()
    with open(input_file, "r") as f:
        p=parser.parse(f.read())
        
    with open(definitions_file, "r") as f:
        defs=json.loads(f.read())
    
    t=ASTTransformer()
    r=t.transform(p)

    r.type_check()
    p=r.compile_proof(defs, None)

    with open(output_file, 'w') as f:
        f.write(p)
        
    if args.forward:
        # TODO: Run compiled proof
        pass
    

def verify(args):
    input_file = args.input
    definitions_file = args.definitions
    output_file = args.output
    
    parser=GSParser()
    with open(input_file, "r") as f:
        p=parser.parse(f.read())
        
    with open(definitions_file, "r") as f:
        defs=json.loads(f.read())
        
    t=ASTTransformer()
    r=t.transform(p)

    r.type_check()
    p=r.compile_verify(defs, None)

    with open(output_file, 'w') as f:
        f.write(p)
    
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process a Groth-Sahai proof.")
    subparsers = parser.add_subparsers()

    INPUT_DEFAULT = os.environ.get("GS_INPUT", "prove.gs")
    DEFINITIONS_DEFAULT = os.environ.get("GS_DEFINITIONS", "prove.json")
    OUTPUT_DEFAULT = os.environ.get("GS_OUTPUT", "prove.py")
    
    # prove parser
    prove_parser = subparsers.add_parser('prove', help='Prove action')
    prove_parser.add_argument('-i', '--input', help='Input file (.gs)', default=INPUT_DEFAULT)
    prove_parser.add_argument('-d', '--definitions', help='Definitions file (.json)', default=DEFINITIONS_DEFAULT)
    prove_parser.add_argument('-o', '--output', help='Output file (.py)', default=OUTPUT_DEFAULT)
    prove_parser.add_argument('-f', '--forward', help='Forward mode', action='store_false')
    prove_parser.set_defaults(func=prove)

    # verify parser
    verify_parser = subparsers.add_parser('verify', help='Verify action')
    verify_parser.add_argument('-i', '--input', help='Input file (.gs)', default=INPUT_DEFAULT)
    verify_parser.add_argument('-d', '--definitions', help='Definitions file (.json)', default=DEFINITIONS_DEFAULT)
    verify_parser.add_argument('-o', '--output', help='Output file (.py)', default=OUTPUT_DEFAULT)
    verify_parser.add_argument('-f', '--forward', help='Forward mode', action='store_false')
    verify_parser.set_defaults(func=verify)
    
    args = parser.parse_args()
    args.func(args)
