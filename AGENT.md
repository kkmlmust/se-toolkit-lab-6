# Agent: LLM Caller

## What is this?
A Python script that asks questions to an AI and returns JSON answers.

## LLM Provider
- **Provider**: Qwen Code API (on VM)
- **Model**: qwen3-coder-plus
- **API**: http://10.93.26.107:42005/v1

## Setup
# Install dependencies
uv add openai python-dotenv

# Create config
cp .env.agent.example .env.agent.secret
# Edit .env.agent.secret with your VM details
# Usage
uv run agent.py "Your question here"

# Example
uv run agent.py "What is REST?"

# Output
{"answer": "REST stands for Representational State Transfer.", "tool_calls": []}

# Testing 
uv run pytest tests/test_task1.py -v

# Files
-agent.py - main script
-.env.agent.secret - configuration (not in git)
-tests/test_task1.py - tests
