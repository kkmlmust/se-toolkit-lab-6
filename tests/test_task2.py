import subprocess
import json
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent

def test_agent_merge_conflict():
    """Test question about merge conflict - should read git-workflow.md"""
    result = subprocess.run(
        ["uv", "run", "agent.py", "How do you resolve a merge conflict?"],
        capture_output=True,
        text=True,
        cwd=root_dir
    )
    
    assert result.returncode == 0, f"Agent failed with code {result.returncode}"
    
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"stdout: {result.stdout}", file=sys.stderr)
        assert False, f"Invalid JSON: {e}"
    
    # Проверяем структуру
    assert "answer" in output
    assert "source" in output
    assert "tool_calls" in output
    
    # Проверяем что были tool calls
    assert len(output["tool_calls"]) > 0
    
    # Проверяем что был read_file для git-workflow.md
    read_file_calls = [
        tc for tc in output["tool_calls"] 
        if tc["tool"] == "read_file" and "git-workflow.md" in tc["args"].get("path", "")
    ]
    
    # Должен быть хотя бы один read_file для git-workflow.md
    assert len(read_file_calls) > 0, "Should read git-workflow.md"
    
    # Проверяем source
    assert "git-workflow.md" in output["source"], f"Source should reference git-workflow.md, got {output['source']}"
    
    print(f"Test passed! Answer: {output['answer'][:50]}...", file=sys.stderr)

def test_agent_list_wiki_files():
    """Test question about wiki files - should use list_files"""
    result = subprocess.run(
        ["uv", "run", "agent.py", "What files are in the wiki?"],
        capture_output=True,
        text=True,
        cwd=root_dir
    )
    
    assert result.returncode == 0, f"Agent failed with code {result.returncode}"
    
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"stdout: {result.stdout}", file=sys.stderr)
        assert False, f"Invalid JSON: {e}"
    
    # Проверяем структуру
    assert "answer" in output
    assert "source" in output
    assert "tool_calls" in output
    
    # Проверяем что был list_files
    list_files_calls = [
        tc for tc in output["tool_calls"] 
        if tc["tool"] == "list_files"
    ]
    
    assert len(list_files_calls) > 0, "Should use list_files"
    
    # Проверяем что результат list_files содержит md файлы
    for tc in list_files_calls:
        if tc["tool"] == "list_files" and "result" in tc:
            assert ".md" in tc["result"] or "wiki/" in tc["result"], "Should list markdown files"
    
    print(f"Test passed! Made {len(output['tool_calls'])} tool calls", file=sys.stderr)

def test_tool_security():
    """Test that tools prevent directory traversal"""
    # Попытка прочитать файл вне проекта
    result = subprocess.run(
        ["uv", "run", "agent.py", "Read /etc/passwd"],
        capture_output=True,
        text=True,
        cwd=root_dir
    )
    
    # Должен завершиться успешно (агент не падает)
    assert result.returncode == 0
    
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        # Если JSON не парсится, проверяем что в tool_calls есть ошибка
        pass
    
    # Проверяем что в tool_calls есть ошибки безопасности
    if "tool_calls" in output:
        for tc in output["tool_calls"]:
            if tc["tool"] == "read_file":
                assert "Error" in tc["result"] or "Access denied" in tc["result"]
                