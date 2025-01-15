import ollama  # Correct library import
import os
import logging
import json
import time
import hashlib
import asyncio
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from enum import Enum

# ====================
# CONFIGURATION SETTINGS
# ====================
CONFIG = {
    "model": "llama2",
    "max_retries": 3,
    "timeout": 30,
    "log_path": "logs/ai_agent.log",
    "cache_path": "cache/responses/",
    "security": {
        "min_acceptable_score": 80,
        "dangerous_patterns": [
            "os.system", "eval(", "exec(", "__import__",
            "subprocess", "open(", "write(", "chmod"
        ]
    }
}

# ====================
# SECURITY LEVEL ENUM
# ====================
class SecurityLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SecurityError(Exception):
    pass

class CacheError(Exception):
    pass

# ====================
# SECURITY CONTEXT CLASS
# ====================
@dataclass
class SecurityContext:
    sanitized: bool = False
    validated: bool = False
    security_score: float = 0.0
    vulnerabilities: List[str] = None
    last_checked: datetime = None
    security_level: SecurityLevel = SecurityLevel.LOW

    def __post_init__(self):
        self.vulnerabilities = self.vulnerabilities or []
        self.last_checked = self.last_checked or datetime.now()

    def is_valid(self) -> bool:
        return self.validated and (
            datetime.now() - self.last_checked).total_seconds() < 86400

    def update_security_level(self):
        if self.security_score >= 90 and not self.vulnerabilities:
            self.security_level = SecurityLevel.HIGH
        elif self.security_score >= 70:
            self.security_level = SecurityLevel.MEDIUM
        else:
            self.security_level = SecurityLevel.LOW

# ====================
# CODE RESPONSE CLASS
# ====================
@dataclass
class CodeResponse:
    code: str
    explanation: str
    security_context: SecurityContext
    metadata: Dict
    timestamp: datetime

    def is_secure(self) -> bool:
        return (
            self.security_context.security_score >= CONFIG["security"]["min_acceptable_score"]
            and self.security_context.security_level != SecurityLevel.LOW
            and not self.security_context.vulnerabilities
        )

# ====================
# SECURITY MANAGEMENT CLASS
# ====================
class SecurityManager:
    @staticmethod
    async def perform_security_checks(code: str) -> Tuple[SecurityContext, str]:
        security_context = SecurityContext()
        sanitized_code = SecurityManager.sanitize_code(code)
        valid_syntax = SecurityManager.validate_syntax(sanitized_code)
        security_score = await SecurityManager.calculate_security_score(sanitized_code)

        security_context.validated = valid_syntax
        security_context.security_score = security_score
        security_context.sanitized = True
        security_context.update_security_level()

        return security_context, sanitized_code

    @staticmethod
    def sanitize_code(code: str) -> str:
        for pattern in CONFIG["security"]["dangerous_patterns"]:
            code = code.replace(pattern, f"# SECURITY REMOVED: {pattern}")
        return code

    @staticmethod
    def validate_syntax(code: str) -> bool:
        try:
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError:
            return False

    @staticmethod
    async def calculate_security_score(code: str) -> float:
        score = 100.0
        for pattern in CONFIG["security"]["dangerous_patterns"]:
            if pattern in code:
                score -= 20
        return max(0, score)

# ====================
# CACHE MANAGEMENT CLASS
# ====================
class CacheManager:
    def __init__(self, cache_path: str):
        self.cache_path = Path(cache_path)
        self.cache_path.mkdir(parents=True, exist_ok=True)

    def get_cache_key(self, prompt: str) -> str:
        return hashlib.sha256(prompt.encode()).hexdigest()

    def get_cached_response(self, prompt: str) -> Optional[CodeResponse]:
        cache_key = self.get_cache_key(prompt)
        cache_file = self.cache_path / f"{cache_key}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return CodeResponse(**data)
        return None

    def cache_response(self, prompt: str, response: CodeResponse):
        cache_key = self.get_cache_key(prompt)
        cache_file = self.cache_path / f"{cache_key}.json"
        with open(cache_file, 'w') as f:
            json.dump(response.__dict__, f)

# ====================
# AI AGENT CLASS
# ====================
class AIAgent:
    def __init__(self):
        self.security_manager = SecurityManager()
        self.cache_manager = CacheManager(CONFIG["cache_path"])

    async def generate_response(self, prompt: str) -> CodeResponse:
        """Generate a secure response from Ollama API with caching."""
        cached_response = self.cache_manager.get_cached_response(prompt)
        if cached_response and cached_response.is_secure():
            return cached_response

        # ✅ Corrected the ollama.chat call here
        response = ollama.chat(
            model=CONFIG["model"],
            messages=[{"role": "user", "content": prompt}]
        )

        # Proper error handling if no message content returned
        message_content = response.get("message", {}).get("content", "")
        if not message_content:
            raise SecurityError("No valid content received from Ollama.")

        # Run security checks on the generated content
        security_context, sanitized_code = await self.security_manager.perform_security_checks(message_content)

        # Create the code response object
        code_response = CodeResponse(
            code=sanitized_code,
            explanation="AI-generated secure response",
            security_context=security_context,
            metadata={"model": CONFIG["model"]},
            timestamp=datetime.now()
        )

        # Cache the secure response for future use
        self.cache_manager.cache_response(prompt, code_response)
        return code_response

    async def refactor_code(self, code: str) -> CodeResponse:
        """Refactor code for better readability and structure."""
        refactor_prompt = f"""
        Refactor the following code for better readability and security compliance:

        {code}
        """
        return await self.generate_response(refactor_prompt)

# ====================
# RUN THE AGENT
# ====================
if __name__ == "__main__":
    agent = AIAgent()
    task = input("What task would you like me to perform? ")
    asyncio.run(agent.generate_response(task))
