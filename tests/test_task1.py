import subprocess
import json
import sys
from pathlib import Path

# Add root directory to path
root_dir = Path(__file__).parent.parent


def test_agent_basic_question():
    """Test that agent.py returns valid JSON with answer and tool_calls"""
    # Run agent with a simple question
    result = subprocess.run(
        ["uv", "run", "agent.py", "What is 2+2?"],
        capture_output=True,
        text=True,
        cwd=root_dir
    )

    # Check that the program completed successfully
    assert result.returncode == 0, f"Agent failed with code {result.returncode}"

    # Try to parse stdout as JSON
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"stdout: {result.stdout}", file=sys.stderr)
        print(f"stderr: {result.stderr}", file=sys.stderr)
        assert False, f"Output is not valid JSON: {e}"

    # Check that 'answer' field exists
    assert "answer" in output, "Response missing 'answer' field"

    # Check that 'tool_calls' field exists
    assert "tool_calls" in output, "Response missing 'tool_calls' field"

    # Check that tool_calls is a list
    assert isinstance(output["tool_calls"], list), "'tool_calls' must be a list"

    # Check that answer is not empty
    assert output["answer"] and len(output["answer"]) > 0, "Answer is empty"

    print(f"Test passed! Answer: {output['answer'][:50]}...", file=sys.stderr)
