# main.py

import argparse
from agent.run_agent import run_agent_task

def main():
    parser = argparse.ArgumentParser(description="Run the local AI agent.")
    parser.add_argument("task", type=str, help="Instruction for the agent.")
    parser.add_argument("--use_ollama", action="store_true", help="Use local LLaMA via Ollama instead of OpenAI.")
    args = parser.parse_args()

    result = run_agent_task(args.task, use_ollama=args.use_ollama)
    print("\n=== AGENT OUTPUT ===")
    print(result)

if __name__ == "__main__":
    main()
