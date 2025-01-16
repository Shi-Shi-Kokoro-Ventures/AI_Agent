# agent/run_agent.py

from agent.agent_core import AgentCore

def run_agent_task(task: str, use_ollama: bool = True) -> str:
    """
    Creates an AgentCore instance and runs the given task prompt.
    """
    agent_core = AgentCore(use_ollama=use_ollama)
    return agent_core.run(task)
