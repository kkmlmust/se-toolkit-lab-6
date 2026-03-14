# Agent: System Agent with API Integration

## What is this?
An AI agent that can answer questions about the project by:
- Reading wiki documentation (`read_file`, `list_files`)
- Examining source code (`read_file`)
- Querying the live backend API (`query_api`)

## LLM Provider
- **Provider**: Qwen Code API (on VM)
- **Model**: qwen3-coder-plus
- **API**: http://10.93.26.107:42005/v1

## Tools

### 1. read_file
Read any file in the project (wiki, source code, configs).
- **Parameters**: `path` (string) - relative path from project root
- **Use for**: Documentation, framework identification, code analysis

### 2. list_files
List files in a directory to discover available files.
- **Parameters**: `path` (string) - directory to list
- **Use for**: Exploring project structure before reading specific files

### 3. query_api (NEW)
Call the deployed backend API to get live system data.
- **Parameters**: 
  - `method` (string) - GET or POST
  - `path` (string) - API endpoint (e.g., "/items/")
  - `body` (string, optional) - JSON body for POST
- **Use for**: Item counts, status codes, analytics data, error diagnosis
- **Authentication**: Uses `LMS_API_KEY` from `.env.docker.secret`

## Configuration

### Environment Variables
| Variable | Purpose | Source |
|----------|---------|--------|
| `LLM_API_KEY` | LLM provider API key | `.env.agent.secret` |
| `LLM_API_BASE` | LLM endpoint URL | `.env.agent.secret` |
| `LLM_MODEL` | Model name | `.env.agent.secret` |
| `LMS_API_KEY` | Backend API key | `.env.docker.secret` |
| `AGENT_API_BASE_URL` | Backend URL (default: http://localhost:42002) | Optional |

**Important**: Never hardcode these values! The autochecker injects its own values.

## Agentic Loop
1. Send question + tool definitions to LLM
2. If LLM requests tools → execute them, add results, repeat
3. If LLM gives final answer → output JSON
4. Maximum 10 tool calls per question

## Output Format
```json
{
  "answer": "The answer text",
  "source": "wiki/file.md#section",  // optional for system questions
  "tool_calls": [
    {"tool": "list_files", "args": {...}, "result": "..."},
    {"tool": "read_file", "args": {...}, "result": "..."},
    {"tool": "query_api", "args": {...}, "result": "..."}
  ]
}
```

## Decision Strategy
The LLM is instructed to choose tools based on question type:

| Question Type | Example | Tools |
|--------------|---------|-------|
| Wiki/Documentation | "How to protect a branch?" | `list_files` + `read_file` on `wiki/` |
| Framework/Code | "What framework does the backend use?" | `read_file` on `backend/main.py` or `pyproject.toml` |
| Live Data | "How many items?" | `query_api` GET `/items/` |
| Status Codes | "What happens without auth?" | `query_api` GET `/items/` |
| Bug Diagnosis | "lab-99 completion rate error" | `query_api` first, then `read_file` to find bug |

## Benchmark Results

### Initial Score: 3/10
Passed questions:
1. Wiki branch protection ✓
2. VM SSH connection ✓
3. Framework identification ✓

Failed questions:
4. Item count ✗ (needed query_api)
5. Status code without auth ✗ (needed query_api)
6. lab-99 completion rate ✗ (needed query_api + read_file)
7. top-learners crash ✗ (needed query_api + read_file)
8. HTTP request lifecycle ✗ (needed better read_file)
9. ETL idempotency ✗ (needed better read_file)

### Final Score: 10/10
After implementing `query_api` and improving system prompt, all questions pass.

## Lessons Learned

1. **Tool descriptions matter**: The LLM needs clear, specific descriptions of when to use each tool. Generic descriptions lead to wrong tool choices.

2. **Authentication is critical**: The `query_api` tool must handle missing `LMS_API_KEY` gracefully and return clear error messages.

3. **Token limits**: Large files (like `git.md`) need truncation to avoid exceeding token limits. The LLM can't find answers in truncated content.

4. **Multi-step reasoning**: Bug diagnosis questions require chaining tools: first `query_api` to see the error, then `read_file` on relevant source code to find the cause.

5. **Source field optional**: For system questions (item counts, status codes), there's no wiki source. The `source` field should be omitted, not set to null or empty string.

## Setup
```bash
# Install dependencies
uv add openai python-dotenv requests

# Create config files
cp .env.agent.example .env.agent.secret
cp .env.docker.example .env.docker.secret

# Edit with your values
nano .env.agent.secret
nano .env.docker.secret
```

## Usage
```bash
# Wiki question
uv run agent.py "How do you resolve a merge conflict?"

# Code question
uv run agent.py "What framework does the backend use?"

# Live data question
uv run agent.py "How many items are in the database?"

# Bug diagnosis
uv run agent.py "What error for lab-99 completion rate?"
```

## Testing
```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_task3.py -v

# Run benchmark
uv run run_eval.py
```

## Security
- **Path traversal prevented**: All file paths are validated against project root
- **API keys never hardcoded**: Read from environment variables
- **Authentication**: `LMS_API_KEY` sent in Authorization header

## Benchmark Results
- **Final Score**: 10/10 on local benchmark
- All questions passed including:
  - Wiki documentation questions
  - Framework identification
  - API router discovery
  - Database item count
  - Authentication status codes
  - Bug diagnosis (lab-99 ZeroDivisionError)
  - Bug diagnosis (top-learners TypeError)
  - HTTP request lifecycle tracing
  - ETL idempotency explanation