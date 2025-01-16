# agent/tools/code_tools.py

import subprocess
import tempfile

def run_python_code(code: str) -> str:
    """
    Runs a Python code snippet in a temporary file and returns stdout/stderr.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False) as tmp_file:
        file_name = tmp_file.name
        tmp_file.write(code)
    
    try:
        result = subprocess.run(
            ["python", file_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout if result.stdout else ""
        errors = result.stderr if result.stderr else ""
        return f"Output:\n{output}\nErrors:\n{errors}"
    except Exception as e:
        return f"Error running code: {e}"
    finally:
        # If you want to delete the temp file after, you could do so here
        pass
