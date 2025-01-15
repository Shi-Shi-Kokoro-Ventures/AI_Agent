import unittest
from src.ai_agent import AIAgent
import asyncio

class TestAIAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.agent = AIAgent()

    def test_generate_response(self):
        """Test if the AI agent generates a response successfully."""
        async def run_test():
            response = await self.agent.generate_response("Generate a Python script to calculate factorial")
            self.assertTrue(response.code)
            self.assertTrue(response.explanation)
            self.assertTrue(response.security_context.validated)

        asyncio.run(run_test())

    def test_security_check(self):
        """Test if the security checks catch unsafe code."""
        async def run_test():
            code = "eval('2+2')"
            context, sanitized_code = await self.agent.security_manager.perform_security_checks(code)
            self.assertFalse(context.validated)
            self.assertIn('SECURITY REMOVED', sanitized_code)

        asyncio.run(run_test())

    def test_cache_response(self):
        """Test if the cache stores and retrieves responses correctly."""
        async def run_test():
            prompt = "Write a Python script to reverse a string"
            await self.agent.generate_response(prompt)
            cached_response = self.agent.cache_manager.get_cached_response(prompt)
            self.assertIsNotNone(cached_response)

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
