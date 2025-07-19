import ast 

BANNED_KEYWORDS=[
     "import os", "import subprocess", "open(", "exec(", "eval(", "__import__",
    "os.system", "shutil", "pickle", "socket", "requests"
]
def contains_dangerous_code(code:str) -> bool:
    return any(bad in code for bad in BANNED_KEYWORDS)

def is_valid_python(code:str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False

def has_backtrader_strategy(code:str) -> bool:
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                # Check for ast.Name and ast.Attribute
                    if (
                        (isinstance(base, ast.Name) and base.id == 'Strategy') or
                        (isinstance(base, ast.Attribute) and base.attr == 'Strategy')
                    ):
                        return True
        return False
    except SyntaxError:
        return False
    
def validate_strategy_code(code: str) -> dict:
    if contains_dangerous_code(code):
        return {"valid": False, "reason": "Dangerous code detected."}

    if not is_valid_python(code):
        return {"valid": False, "reason": "Syntax error in code."}

    if not has_backtrader_strategy(code):
        return {"valid": False, "reason": "No valid backtrader Strategy class found."}

    return {"valid": True}