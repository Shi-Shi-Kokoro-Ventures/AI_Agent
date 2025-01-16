# agent/agent_core.py

"""
🤖 Enhanced AI Agent Core System
===============================

Production-grade AI agent system with robust async support, comprehensive safety checks,
and detailed performance monitoring.

Author: Your Friendly Neighborhood Dev 🚀
Last Updated: 2024-01-16
"""

import os
import time
import asyncio
import logging
import importlib
import ast
from typing import List, Dict, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

# Third-party imports
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.llms import OpenAI, BaseLLM
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import BaseCallbackHandler

# Local imports
from agent.custom_llm import OllamaLLM
from agent.tools.file_tools import read_file, write_file
from agent.tools.code_tools import run_python_code
from agent.utils.performance_tracker import PerformanceTracker
from agent.utils.safety_validator import SafetyValidator
from agent.config import load_config

# Load configuration
CONFIG = load_config()

# Configure logging
logging.basicConfig(
    level=getattr(logging, CONFIG.get('LOG_LEVEL', 'INFO')),
    format='%(asctime)s 🤖 %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@dataclass
class RequestMetrics:
    """Detailed metrics for a single request"""
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    success: bool = False
    error: Optional[str] = None

@dataclass
class AgentMetrics:
    """Enhanced agent performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_error: Optional[str] = None
    last_activity: Optional[datetime] = None
    request_history: List[RequestMetrics] = field(default_factory=list)
    
    def add_request(self, metrics: RequestMetrics):
        """Add request metrics with thread safety"""
        self.request_history.append(metrics)
        self.total_requests += 1
        
        if metrics.success:
            self.successful_requests += 1
            if metrics.duration is not None:
                if self.successful_requests == 1:
                    self.average_response_time = metrics.duration
                else:
                    self.average_response_time = (
                        (self.average_response_time * (self.successful_requests - 1) + metrics.duration)
                        / self.successful_requests
                    )
        else:
            self.failed_requests += 1
            self.last_error = metrics.error
            
        self.last_activity = metrics.end_time or metrics.start_time

class EnhancedPerformanceCallback(BaseCallbackHandler):
    """Thread-safe performance monitoring with detailed metrics"""
    
    def __init__(self, metrics: AgentMetrics):
        self.metrics = metrics
        self._current_request: Optional[RequestMetrics] = None
        self._lock = asyncio.Lock()

    async def on_llm_start(self, *args, **kwargs):
        """Handle LLM start with thread safety"""
        async with self._lock:
            self._current_request = RequestMetrics(
                start_time=datetime.now()
            )

    async def on_llm_end(self, *args, **kwargs):
        """Handle successful LLM completion"""
        if self._current_request:
            async with self._lock:
                self._current_request.end_time = datetime.now()
                self._current_request.duration = (
                    self._current_request.end_time - self._current_request.start_time
                ).total_seconds()
                self._current_request.success = True
                self.metrics.add_request(self._current_request)
                self._current_request = None

    async def on_llm_error(self, error: Union[str, Exception], *args, **kwargs):
        """Handle LLM errors with detailed tracking"""
        if self._current_request:
            async with self._lock:
                self._current_request.end_time = datetime.now()
                self._current_request.success = False
                self._current_request.error = str(error)
                self.metrics.add_request(self._current_request)
                self._current_request = None

class CodeValidator:
    """Advanced Python code validation and security checking"""
    
    BLOCKED_IMPORTS = {
        'os', 'subprocess', 'sys', 'builtins', 'shutil',
        'pickle', 'marshal', 'base64', 'codecs'
    }
    
    BLOCKED_ATTRIBUTES = {
        'eval', 'exec', 'compile', '__import__', 'open',
        'file', 'execfile', 'input', 'raw_input'
    }

    @classmethod
    def validate_code(cls, code: str) -> Tuple[bool, Optional[str]]:
        """
        Thoroughly validate Python code for security concerns.
        
        Returns:
            Tuple[bool, Optional[str]]: (is_safe, error_message)
        """
        try:
            # Parse the code into an AST
            tree = ast.parse(code)
            
            # Check for dangerous imports and attributes
            for node in ast.walk(tree):
                # Check imports
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    for name in node.names:
                        if name.name.split('.')[0] in cls.BLOCKED_IMPORTS:
                            return False, f"Blocked import: {name.name}"
                
                # Check attribute access
                elif isinstance(node, ast.Attribute):
                    if node.attr in cls.BLOCKED_ATTRIBUTES:
                        return False, f"Blocked attribute: {node.attr}"
                
                # Check calls to dangerous functions
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in cls.BLOCKED_ATTRIBUTES:
                            return False, f"Blocked function call: {node.func.id}"
            
            return True, None
            
        except SyntaxError as e:
            return False, f"Invalid syntax: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

class AgentCore:
    """Enhanced AI Agent Core with robust async support and safety features"""

    def __init__(
        self,
        use_ollama: bool = True,
        model_config: Optional[Dict[str, Any]] = None,
        memory_config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the agent with configuration and safety checks"""
        self.use_ollama = use_ollama
        self.model_config = model_config or {
            "temperature": CONFIG.get('TEMPERATURE', 0.7),
            "max_tokens": CONFIG.get('MAX_TOKENS', 2000),
            "top_p": CONFIG.get('TOP_P', 0.9)
        }
        
        # Default memory configuration
        default_memory_config = {
            "max_token_limit": CONFIG.get('MEMORY_TOKEN_LIMIT', 2048),
            "return_messages": True,
            "output_key": "output",
            "input_key": "input",
            "memory_key": "chat_history"
        }
        self.memory_config = {**default_memory_config, **(memory_config or {})}
        
        # Initialize components
        self.metrics = AgentMetrics()
        self.performance_tracker = PerformanceTracker()
        self.code_validator = CodeValidator()
        self._initialize_components()
        
        logger.info("🎉 Agent initialized with enhanced security and monitoring!")

    def _initialize_components(self):
        """Initialize all agent components with error handling"""
        try:
            self.memory = ConversationBufferMemory(**self.memory_config)
            self.tools = []
            self.llm = None
            self.agent = None
            self._executor = ThreadPoolExecutor(max_workers=CONFIG.get('MAX_WORKERS', 3))
            
            self._build_llm()
            self._build_tools()
            self._build_agent()
            
        except Exception as e:
            logger.error(f"Failed to initialize agent components: {e}")
            raise

    async def _safe_run_python_code(self, code: str) -> str:
        """Enhanced safe Python code execution with thorough validation"""
        is_safe, error_message = self.code_validator.validate_code(code)
        
        if not is_safe:
            return f"⚠️ Code validation failed: {error_message}"
        
        try:
            # Run code in a separate thread to prevent blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._executor,
                run_python_code,
                code
            )
            return result
        except Exception as e:
            return f"❌ Error executing code: {str(e)}"

    async def run(self, prompt: str) -> str:
        """
        Execute agent tasks with proper async handling and safety checks.
        
        This method properly handles async operations without nested event loops.
        """
        if not prompt or not isinstance(prompt, str):
            raise ValueError("🤔 I need a valid prompt to help you!")
        
        try:
            # Run agent in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self._executor,
                self.agent.run,
                prompt
            )
            return f"✨ {response}"
            
        except Exception as e:
            logger.error(f"Error running agent: {e}")
            raise

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        stats = {
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "success_rate": (
                self.metrics.successful_requests / self.metrics.total_requests
                if self.metrics.total_requests > 0 else 0
            ),
            "average_response_time": f"{self.metrics.average_response_time:.2f}s",
            "last_activity": (
                self.metrics.last_activity.strftime("%Y-%m-%d %H:%M:%S")
                if self.metrics.last_activity else None
            ),
            "last_error": self.metrics.last_error,
            "recent_requests": []
        }
        
        # Add recent request details
        for req in self.metrics.request_history[-10:]:  # Last 10 requests
            stats["recent_requests"].append({
                "timestamp": req.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration": f"{req.duration:.2f}s" if req.duration else None,
                "success": req.success,
                "error": req.error
            })
            
        return stats

# Example test cases (you would typically put these in a separate test file)
import unittest

class TestAgentCore(unittest.TestCase):
    """Test cases for AgentCore functionality"""
    
    async def asyncSetUp(self):
        self.agent = AgentCore(use_ollama=True)

    async def test_code_validation(self):
        """Test code validation functionality"""
        dangerous_code = "import os; os.system('rm -rf /')"
        is_safe, error = self.agent.code_validator.validate_code(dangerous_code)
        self.assertFalse(is_safe)
        self.assertIn("Blocked import", error)

    async def test_metrics_tracking(self):
        """Test metrics tracking functionality"""
        await self.agent.run("Hello, world!")
        stats = self.agent.get_performance_stats()
        self.assertEqual(stats["total_requests"], 1)
        self.assertGreaterEqual(stats["success_rate"], 0)

    async def test_memory_configuration(self):
        """Test memory configuration and limits"""
        self.assertLessEqual(
            self.agent.memory_config["max_token_limit"],
            CONFIG.get('MEMORY_TOKEN_LIMIT', 2048)
        )

if __name__ == "__main__":
    # Proper async execution in main
    async def main():
        agent = AgentCore()
        try:
            result = await agent.run("Tell me a joke about Python programming!")
            print(result)
        except Exception as e:
            print(f"😅 Error: {str(e)}")
        finally:
            agent._executor.shutdown(wait=True)

    # Run with proper async handling
    if asyncio.get_event_loop().is_running():
        # We're already in an event loop
        asyncio.create_task(main())
    else:
        # No event loop running
        asyncio.run(main())