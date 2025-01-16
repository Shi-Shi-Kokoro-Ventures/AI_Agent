"""
Initialization file for the agent package.
Provides centralized imports, package versioning, and logging setup.
"""

import logging

# Package version
__version__ = "1.0.0"

# Set up logging for the agent package
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Centralized imports for tools and core components
from agent.agent_core import AgentCore
from agent.custom_llm import OllamaLLM
from agent.tools.file_tools import read_file, write_file
from agent.tools.code_tools import run_python_code

__all__ = [
    "AgentCore",
    "OllamaLLM",
    "read_file",
    "write_file",
    "run_python_code",
    "__version__",
]
