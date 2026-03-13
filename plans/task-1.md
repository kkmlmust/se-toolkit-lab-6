# Task 1: Call an LLM from Code - Implementation Plan

## LLM Provider Selection
- **Provider**: Qwen Code API
- **Deployment**: Running on VM at http://10.93.26.107:42005/v1
- **Model**: qwen3-coder-plus
- **API Key**: Stored in `.env.agent.secret`

## Technical Approach
1. **Configuration**: Use `python-dotenv` to load `.env.agent.secret`
2. **LLM Client**: OpenAI-compatible client from `openai` library
3. **Input Processing**: Read question from command-line arguments (`sys.argv`)
4. **API Call**: Send request to Qwen API with system prompt and user question
5. **Output Formatting**: Return JSON with `answer` and empty `tool_calls`
6. **Error Handling**: Log to stderr, exit with non-zero code on errors

## Implementation Steps
1. Install dependencies: `uv add openai python-dotenv`
2. Create `agent.py` with main logic
3. Write regression test in `tests/test_task1.py`
4. Document in a `AGENT.md`

## Testing Strategy
- Run agent with test question
- Verify JSON output structure
- Check that stderr contains logs (not stdout)
- Ensure exit code 0 on success