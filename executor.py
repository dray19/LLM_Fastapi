"""Safe execution environment for pandas code with validation."""

import pandas as pd

# Allowed globals for code execution
SAFE_GLOBALS = {
    "pd": pd
}

# Security: tokens that indicate potentially dangerous operations
FORBIDDEN_TOKENS = [
    "__",           # Dunder methods (can access internals)
    "import",       # Dynamic imports
    "open(",        # File operations
    "exec(",        # Code execution
    "eval(",        # Expression evaluation
    "os.",          # OS operations
    "sys.",         # System operations
    "subprocess",   # Process spawning
]


def validate_code(code: str) -> None:
    """
    Validate code string for forbidden tokens.
    
    Args:
        code: Python code string to validate
        
    Raises:
        ValueError: If forbidden token is detected
    """
    for token in FORBIDDEN_TOKENS:
        if token in code:
            raise ValueError(f"Forbidden token detected: {token}")


def run_pandas_code(df: pd.DataFrame, code: str) -> pd.DataFrame:
    """
    Execute pandas code in a sandboxed environment.
    
    Args:
        df: Input DataFrame to operate on
        code: Python code string to execute (must assign output to 'result')
        
    Returns:
        The DataFrame assigned to 'result' variable in the code
        
    Raises:
        ValueError: If code validation fails or 'result' variable not set
    """
    print("\n" + "=" * 50)
    print("EXECUTING CODE")
    print("=" * 50)
    print(code)
    print("=" * 50 + "\n")
    
    validate_code(code)
    
    local_vars = {"df": df.copy()}
    exec(code, SAFE_GLOBALS, local_vars)
    
    if "result" not in local_vars:
        raise ValueError("Code must assign output to variable 'result'")
    
    return local_vars["result"]