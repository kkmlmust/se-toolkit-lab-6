# Task 2: Documentation Agent with Tools - Implementation Plan

## Overview
Extend the Task 1 agent to include tools (`read_file`, `list_files`) and implement an agentic loop that can navigate the project wiki to answer questions.

## Tool Definitions

### 1. read_file
- **Purpose**: Read contents of any file in the project
- **Parameters**: `path` (string) - relative path from project root
- **Security**: Must validate path is within project root (prevent `../` traversal)
- **Returns**: File contents or error message

### 2. list_files
- **Purpose**: List files and directories at a given path
- **Parameters**: `path` (string, default: ".") - directory to list
- **Security**: Must validate path is within project root
- **Returns**: Newline-separated list of entries

## Agentic Loop Implementation

## System Prompt Strategy

The system prompt will instruct the LLM to:
1. First use `list_files` to discover available wiki files
2. Then use `read_file` on relevant files to find answers
3. Always track which file the information comes from (for `source` field)
4. Make multiple tool calls if needed

## Security Considerations

- Use `Path.resolve()` to normalize all paths
- Compare against `PROJECT_ROOT` to prevent directory traversal
- Return clear error messages for security violations

## Output Format Changes from Task 1

Task 1 output:
```json
{
  "answer": "...",
  "tool_calls": []
}
```
Task 2 output:
```json
{
  "answer": "...",
  "source": "wiki/file.md#section",
  "tool_calls": [
    {"tool": "list_files", "args": {...}, "result": "..."},
    {"tool": "read_file", "args": {...}, "result": "..."}
  ]
}
```
