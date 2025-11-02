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

def validate_strategy_risk(code: str) -> dict:
    """Validate Strategy for proper risk management implementation."""
    try:
        tree = ast.parsre(code)
        has_stoploss = False
        has_position_sizing = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if node.attr == "stop_loss":
                    has_stoploss = True
                if node.attr in ['size', 'stake']:
                    has_position_sizing = True
            
        return {
            "valid": has_stoploss and has_position_sizing,
            "warnings": {
                "missing_stoploss": not has_stoploss,
                "missing_position_sizing": not has_position_sizing
            }
        }
    except Exception: 
        return {"valid": False, "reason": "Error analyzing code."}