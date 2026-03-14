#!/usr/bin/env python3
"""
Agent that calls LLM and returns JSON response with tools (read_file, list_files).
"""
import os
import sys
import json
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Настройка логирования в stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Константы
PROJECT_ROOT = Path(__file__).parent.absolute()
MAX_TOOL_CALLS = 10

class ToolResult:
    """Represents result of a tool call"""
    def __init__(self, tool: str, args: Dict[str, Any], result: str):
        self.tool = tool
        self.args = args
        self.result = result
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool": self.tool,
            "args": self.args,
            "result": self.result
        }

def load_config() -> Dict[str, str]:
    """Load configuration from .env.agent.secret"""
    env_path = PROJECT_ROOT / '.env.agent.secret'
    if not env_path.exists():
        logger.error(".env.agent.secret file not found!")
        logger.error("Please create it from .env.agent.example")
        sys.exit(1)
    
    load_dotenv(env_path)
    
    config: Dict[str, Optional[str]] = {
        'api_key': os.getenv('LLM_API_KEY'),
        'api_base': os.getenv('LLM_API_BASE'),
        'model': os.getenv('LLM_MODEL', 'qwen3-coder-plus')
    }
    
    missing = [k for k, v in config.items() if not v]
    if missing:
        logger.error(f"Missing config variables in .env.agent.secret: {missing}")
        sys.exit(1)
    
    return {k: v for k, v in config.items() if v is not None}  # type: ignore

def safe_path(path: str) -> Path:
    """
    Ensure path is within project root (security)
    Raises ValueError if path tries to escape project root
    """
    # Нормализуем путь и убираем ../ попытки
    requested_path = (PROJECT_ROOT / path).resolve()
    
    # Проверяем, что путь внутри PROJECT_ROOT
    if not str(requested_path).startswith(str(PROJECT_ROOT)):
        raise ValueError(f"Access denied: path '{path}' is outside project root")
    
    return requested_path

def read_file(path: str) -> str:
    """Read a file from the project repository"""
    try:
        file_path = safe_path(path)
        
        if not file_path.exists():
            return f"Error: File '{path}' does not exist"
        
        if not file_path.is_file():
            return f"Error: '{path}' is not a file"
        
        # Читаем файл
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
        
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def list_files(path: str = ".") -> str:
    """List files and directories at a given path"""
    try:
        dir_path = safe_path(path)
        
        if not dir_path.exists():
            return f"Error: Path '{path}' does not exist"
        
        if not dir_path.is_dir():
            return f"Error: '{path}' is not a directory"
        
        # Получаем список файлов и директорий
        entries = []
        for entry in sorted(dir_path.iterdir()):
            if entry.is_dir():
                entries.append(f"{entry.name}/")
            else:
                entries.append(entry.name)
        
        return "\n".join(entries)
        
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error listing files: {str(e)}"

def get_tool_definitions() -> List[Dict[str, Any]]:
    """Return tool definitions for OpenAI function calling"""
    return [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a file from the project repository. Use this to read wiki files and find answers.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to the file from project root (e.g., 'wiki/git-workflow.md')"
                        }
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List files and directories at a given path. Use this to discover what wiki files are available.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative directory path from project root (default: '.')",
                            "default": "."
                        }
                    },
                    "required": []
                }
            }
        }
    ]

def execute_tool(tool_call: Any) -> ToolResult:
    """Execute a tool call and return the result"""
    tool_name = tool_call.function.name
    try:
        args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        args = {}
    
    logger.info(f"Executing tool: {tool_name} with args: {args}")
    
    if tool_name == "read_file":
        path = args.get("path", "")
        result = read_file(path)
    elif tool_name == "list_files":
        path = args.get("path", ".")
        result = list_files(path)
    else:
        result = f"Error: Unknown tool '{tool_name}'"
    
    return ToolResult(tool_name, args, result)

def extract_source_from_answer(answer: str, tool_calls: List[ToolResult]) -> str:
    """
    Try to extract source from answer or tool calls
    Default to wiki index if not found
    """
    # Проверяем, есть ли упоминание файла в tool_calls
    for tc in tool_calls:
        if tc.tool == "read_file" and "wiki/" in tc.args.get("path", ""):
            path = tc.args.get("path", "")
            # Пытаемся найти секцию (якорь) в ответе
            # Пока просто возвращаем путь к файлу
            return path
    
    # Проверяем, есть ли упоминание файла в самом ответе
    import re
    wiki_files = re.findall(r'wiki/[\w\-\.]+\.md', answer)
    if wiki_files:
        return wiki_files[0]
    
    return "wiki/README.md"

def call_llm_with_tools(messages: List[Dict[str, Any]], config: Dict[str, str], 
                        tool_defs: List[Dict[str, Any]]) -> Any:
    """Call LLM with tools"""
    client = OpenAI(
        api_key=config['api_key'],
        base_url=config['api_base']
    )
    
    response = client.chat.completions.create(
        model=config['model'],
        messages=messages,
        tools=tool_defs if tool_defs else None,
        tool_choice="auto" if tool_defs else None,
        temperature=0.7,
        max_tokens=1000
    )
    
    return response.choices[0].message

def agentic_loop(question: str, config: Dict[str, str]) -> tuple[str, str, List[ToolResult]]:
    """
    Main agentic loop:
    1. Send question + tools to LLM
    2. If tool calls -> execute, add results, repeat
    3. If no tool calls -> final answer
    """
    # Системный промпт с инструкциями
    system_prompt = """You are a helpful assistant that helps users navigate project documentation.
You have access to two tools:
1. list_files - to discover what files are available in the wiki
2. read_file - to read specific wiki files and find answers

Strategy:
1. First, use list_files to see what's in the wiki directory
2. Then, use read_file on relevant files to find the answer
3. Always include the source (file path) in your final answer
4. You can make multiple tool calls if needed

When you have enough information, provide the answer and source in this format:
The answer, and mention which file you found it in.

You have a maximum of 10 tool calls."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]
    
    tool_defs = get_tool_definitions()
    tool_calls_made: List[ToolResult] = []
    
    for _ in range(MAX_TOOL_CALLS):
        logger.info(f"Calling LLM (tool calls so far: {len(tool_calls_made)})")
        
        # Вызываем LLM
        message = call_llm_with_tools(messages, config, tool_defs)
        
        # Если нет tool_calls - это финальный ответ
        if not message.tool_calls:
            answer = message.content or ""
            source = extract_source_from_answer(answer, tool_calls_made)
            return answer, source, tool_calls_made
        
        # Есть tool calls - выполняем их
        logger.info(f"LLM requested {len(message.tool_calls)} tool calls")
        
        # Добавляем сообщение с запросом tools
        messages.append({
            "role": "assistant",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        })
        
        # Выполняем каждый tool call
        for tool_call in message.tool_calls:
            result = execute_tool(tool_call)
            tool_calls_made.append(result)
            
            # Добавляем результат в messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result.result
            })
    
    # Если достигнут лимит tool calls
    logger.warning(f"Reached maximum tool calls ({MAX_TOOL_CALLS})")
    
    # Пробуем получить финальный ответ
    final_messages = messages + [{"role": "user", "content": "Please provide your final answer based on the information you have."}]
    message = call_llm_with_tools(final_messages, config, [])  # No tools this time
    
    answer = message.content or "I couldn't find a complete answer within the tool call limit."
    source = extract_source_from_answer(answer, tool_calls_made)
    
    return answer, source, tool_calls_made

def format_response(answer: str, source: str, tool_calls: List[ToolResult]) -> str:
    """Format response as JSON with answer, source, and tool_calls"""
    response_dict: Dict[str, Any] = {
        "answer": answer,
        "source": source,
        "tool_calls": [tc.to_dict() for tc in tool_calls]
    }
    return json.dumps(response_dict, ensure_ascii=False)

def main() -> None:
    """Main entry point"""
    if len(sys.argv) < 2:
        logger.error("Usage: uv run agent.py 'your question here'")
        sys.exit(1)
    
    question = sys.argv[1]
    
    # Загрузка конфигурации
    config = load_config()
    
    # Запуск агента
    answer, source, tool_calls = agentic_loop(question, config)
    
    # Вывод результата
    print(format_response(answer, source, tool_calls))
    logger.info(f"Done. Made {len(tool_calls)} tool calls")

if __name__ == "__main__":
    main()