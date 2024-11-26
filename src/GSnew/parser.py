from lark import Lark
from lark.indenter import Indenter
from pathlib import Path


class GSIndenter(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 4


class GSParser:
    def __init__(self):
        grammar_path = Path("grammar.lark")
        with grammar_path.open("rt") as f:
            grammar_text = f.read()
        
        self.lark = Lark(grammar_text, parser='lalr', postlex=GSIndenter())

    def parse(self, program_text: str):
        parsed = self.lark.parse(program_text)
        return parsed
