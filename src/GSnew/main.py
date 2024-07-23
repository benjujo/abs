import argparse
from gs_parser import compile_proof, compile_verify


def prove(args):
    compile_proof(args.input, args.definitions, args.output)

def verify(args):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process some integers.")
    subparsers = parser.add_subparsers()

    # prove parser
    prove_parser = subparsers.add_parser('prove', help='Prove action')
    prove_parser.add_argument('-i', '--input', help='Input file (.gs)', default='prove.gs')
    prove_parser.add_argument('-d', '--definitions', help='Definitions file (.json)', default='prove.json')
    prove_parser.add_argument('-o', '--output', help='Output file (.py)', default='prove.py')
    prove_parser.set_defaults(func=prove)

    # verify parser
    verify_parser = subparsers.add_parser('verify', help='Verify action')
    verify_parser.add_argument('-i', '--input', help='Input file (.gs)', default='prove.gs')
    verify_parser.add_argument('-d', '--definitions', help='Definitions file (.json)', default='prove.json')
    verify_parser.add_argument('-o', '--output', help='Output file (.py)', default='prove.py')
    verify_parser.set_defaults(func=verify)
    
    args = parser.parse_args()
    print(args)
    args.func(args)
