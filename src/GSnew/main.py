import argparse
from parser import GSParser
from ast_builder import ASTTransformer
from gsfy import gsfy
import subprocess
import sys
import os
import json


def prove(args):
    input_file = args.input
    definitions_file = args.definitions
    output_file = args.output
    proof_output_file = args.proof_output
    crs_file = args.crs
    
    parser=GSParser()
    with open(input_file, "r") as f:
        p=parser.parse(f.read())
        
    with open(definitions_file, "r") as f:
        defs=json.loads(f.read())
        
    #try:
    with open(crs_file, "r") as f:
        crs=json.loads(f.read())
    #except FileNotFoundError:
    #    if crs_file == 'sound':
    #        crs = CRS.new_sound()
    #    elif crs_file == 'wi':
    #        crs = CRS.new_wi()
    #    else:
    #        raise Exception('CRS not valid')
    
    t=ASTTransformer()
    r=t.transform(p)

    r.type_check()
    p=r.compile_proof(defs, crs, "elements")

    with open(output_file, 'w') as f:
        f.write(p)
        
    if args.forward:
        try:
            result = subprocess.run(
                ["python", output_file],
                capture_output=True,  # Captures stdout and stderr
                text=True             # Outputs strings instead of bytes
            )
            
            # Handle output and errors
            print(result.stdout)
            with open(proof_output_file, 'w') as f:
                f.write(result.stdout)
            
            if result.stderr:
                print("Errors:", file=sys.stderr)
                print(result.stderr, file=sys.stderr)
                
        except Exception as e:
            print(f"An error occurred while running the proof: {e}", file=sys.stderr)
    

def verify(args):
    input_file = args.input
    definitions_file = args.definitions
    output_file = args.output
    crs_file = args.crs
    
    parser=GSParser()
    with open(input_file, "r") as f:
        p=parser.parse(f.read())
        
    with open(definitions_file, "r") as f:
        defs=json.loads(f.read())
        
    with open(crs_file, "r") as f:
        crs=json.loads(f.read())
        
    t=ASTTransformer()
    r=t.transform(p)

    r.type_check()
    p=r.compile_verify(defs, crs, "elements")

    with open(output_file, 'w') as f:
        f.write(p)
        
    if args.forward:
        try:
            result = subprocess.run(
                ["python", output_file],
                capture_output=True,  # Captures stdout and stderr
                text=True             # Outputs strings instead of bytes
            )
            
            # Handle output and errors
            print(result.stdout)
            
            if result.stderr:
                print("Errors:", file=sys.stderr)
                print(result.stderr, file=sys.stderr)
                
        except Exception as e:
            print(f"An error occurred while running the proof: {e}", file=sys.stderr)
            
def generate_crs(args):
    crs_file = args.crs
    crs_type = args.type
    from framework import CRS
    
    
    if crs_type == 'sound':
        crs = CRS.new_sound()
    elif crs_type == 'wi':
        crs = CRS.new_wi()
    else:
        raise Exception('CRS not valid')
    with open(crs_file, 'w') as f:
        f.write(crs.to_json())
    print(crs.to_json())
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process a Groth-Sahai proof.")
    subparsers = parser.add_subparsers()

    INPUT_DEFAULT = os.environ.get("GS_INPUT", "prove.gs")
    DEFINITIONS_DEFAULT = os.environ.get("GS_DEFINITIONS", "prove.json")
    OUTPUT_DEFAULT = os.environ.get("GS_OUTPUT", "prove.py")
    PROOF_OUTPUT_DEFAULT = os.environ.get("GS_PROOF_OUTPUT", "verify.json")
    CRS_DEFAULT = os.environ.get("GS_CRS", "crs.json")
    CRS_TYPE = os.environ.get("GS_CRS_TYPE", "sound")
    
    # prove parser
    prove_parser = subparsers.add_parser('prove', help='Prove action')
    prove_parser.add_argument('-i', '--input', help='Input file (.gs)', default=INPUT_DEFAULT)
    prove_parser.add_argument('-d', '--definitions', help='Definitions file (.json)', default=DEFINITIONS_DEFAULT)
    prove_parser.add_argument('-c', '--crs', help='CRS file (.json)', default=CRS_DEFAULT)
    prove_parser.add_argument('-o', '--output', help='Output file (.py)', default=OUTPUT_DEFAULT)
    prove_parser.add_argument('-p', '--proof-output', help='Output definitions file (.json)', default=PROOF_OUTPUT_DEFAULT)
    prove_parser.add_argument('-f', '--forward', help='Forward mode', action='store_true')
    prove_parser.set_defaults(func=prove)

    # verify parser
    verify_parser = subparsers.add_parser('verify', help='Verify action')
    verify_parser.add_argument('-i', '--input', help='Input file (.gs)', default=INPUT_DEFAULT)
    verify_parser.add_argument('-d', '--definitions', help='Definitions file (.json)', default=DEFINITIONS_DEFAULT)
    verify_parser.add_argument('-c', '--crs', help='CRS file (.json)', default=CRS_DEFAULT)
    verify_parser.add_argument('-o', '--output', help='Output file (.py)', default=OUTPUT_DEFAULT)
    verify_parser.add_argument('-f', '--forward', help='Forward mode', action='store_true')
    verify_parser.set_defaults(func=verify)

    # crs generator
    crs_generator = subparsers.add_parser('crs', help='Generate CRS')
    crs_generator.add_argument('-c', '--crs', help='CRS output file (.json)', default=CRS_DEFAULT)
    crs_generator.add_argument('-t', '--type', help='CRS type', default=CRS_TYPE)
    crs_generator.set_defaults(func=generate_crs)
    
    args = parser.parse_args()
    args.func(args)
