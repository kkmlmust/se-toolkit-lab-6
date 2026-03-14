# Agent: Documentation Assistant with Tools

## What is this?
An AI agent that can read files and list directories to answer questions about the project wiki.

## Tools
The agent has two tools:
1. **read_file** - Read contents of any file in the project
2. **list_files** - List files in a directory

## Agentic Loop
1. Send question + tool definitions to LLM
2. If LLM requests tools → execute them, add results, repeat
3. If LLM gives final answer → output JSON with answer, source, and all tool calls
4. Maximum 10 tool calls per question

## Output Format
```json
{
  "answer": "The answer text",
  "source": "wiki/file.md#section",
  "tool_calls": [
    {"tool": "list_files", "args": {"path": "wiki"}, "result": "file1.md\nfile2.md"},
    {"tool": "read_file", "args": {"path": "wiki/file.md"}, "result": "file contents..."}
  ]
}
```
# Security
Prevents directory traversal (cannot read files outside project)

All paths are validated against project root

# Setup 
Same as Task 1:
```bash
uv add openai python-dotenv
cp .env.agent.example .env.agent.secret
# Edit with your VM details
```
# Usage 
uv run agent.py "How do you resolve a merge conflict?"

# Testing
uv run pytest tests/test_task2.py -v

