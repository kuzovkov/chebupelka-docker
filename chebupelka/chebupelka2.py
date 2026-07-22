"""Minimal coding agent loop — one tool: bash."""
"""MCP servers support"""
import json, sys, subprocess
import requests
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack
from pprint import pprint

LLM_BASE_URL = "http://192.168.0.118:8080/v1"
LLM_API_KEY = "llama.cpp"
LLM_MODEL = "Qwen3.6-27B-Q4_K_M.gguf"
LLM_HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {LLM_API_KEY}"}
MAX_TURNS = 1000

SYSTEM_PROMPT = """\
You are a coding agent. Your job is to help the user with programming tasks.

You have access to built-in tool: `bash` — which executes shell commands and returns stdout/stderr.
Also you have access to tools from plugged MCP servers, full list of them will be provided 
as "Allowed tools"

Workflow:
1. Plan what needs to be done.
2. Use `bash` to read files, run commands, write code, etc.
3. After gathering enough information or completing the task, give your final answer in natural language.
4. To finish, reply with a regular message (no tool call).
Every bash command runs in a new session. You cannot change directories between commands. 
Use absolute paths or chain commands like cd /tmp && ls

Be concise. Explain what you're doing before each command."""

LLM_TOOLS = [
    {"type": "function",
     "function": {"name": "bash",
                  "description": "Execute a shell command and return the output.",
                  "parameters": {"type": "object",
                                 "properties": {
                                     "command": {"type": "string", "description": "The bash command to execute."}
                                 },
                                 "required": ["command"]}
                 }
            }]


async def call_tool_hybrid(name: str, arguments: dict, mcp_tool_map: dict) -> str:
    # 1. Сначала проверяем встроенные (хардкод) инструменты
    if name == "bash":
        return run_bash(**arguments) # Ваша старая синхронная функция
        
    # 2. Проверяем, есть ли этот инструмент в MCP серверах
    elif name in mcp_tool_map:
        session = mcp_tool_map[name] # Находим нужную сессию
        try:
            result = await session.call_tool(name, arguments)
            # Конвертируем ответ MCP в текст для LLM
            output = "\n".join(c.text for c in result.content if c.type == "text")
            return output
        except Exception as e:
            return f"Error executing MCP tool {name}: {e}"     
    # 3. Защита от ошибок
    else:
        return f"Error: unknown tool '{name}'"

async def load_mcp_servers_from_json(config_path: str):
    """
    Читает config.json, подключается ко всем серверам и возвращает:
    1. stack - менеджер контекста (чтобы потом закрыть все соединения)
    2. all_tools - объединенный список инструментов (Local + MCP1 + MCP2)
    3. mcp_tool_map - словарь: {имя_инструмента: сессия_сервера}
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    stack = AsyncExitStack()
    mcp_tool_map = {}  # Карта: какой инструмент какому серверу принадлежит
    all_tools = list(LLM_TOOLS) # Начинаем с базового bash
    servers = config.get("mcpServers", {})
    
    for server_name, server_config in servers.items():
        print(f" Подключаемся к MCP серверу: {server_name}...🔌")      
        # 1. Формируем параметры запуска
        params = StdioServerParameters(
            command=server_config["command"],
            args=server_config.get("args", []),
            env=server_config.get("env")
        )
        
        try:
            # 2. Открываем соединение
            stdio_transport = await stack.enter_async_context(stdio_client(params))
            read, write = stdio_transport
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            
            # 3. Запрашиваем инструменты у этого сервера
            response = await session.list_tools()
            for tool in response.tools:
                # Добавляем инструмент в общий список для LLM
                all_tools.append({
                    "type": "function", 
                    "function": {"name": tool.name, "description": tool.description, "parameters": tool.inputSchema}
                })
                # Запоминаем, что этот инструмент нужно слать в эту сессию
                mcp_tool_map[tool.name] = session
                
            print(f" {server_name} подключен (инструментов: ✅ {len(response.tools)})")
        except Exception as e:
            print(f" Ошибка подключения к {server_name}: {e}❌")
    return stack, all_tools, mcp_tool_map

def run_bash(command: str) -> str:
    try:
        command_result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
        out = command_result.stdout + (f"\nSTDERR:\n{command_result.stderr}" if command_result.stderr else "")
        full_output = f"Exit code: {command_result.returncode}\n{out}"
        # Обрезаем до ~8000 символов, чтобы не убить контекст LLM
        if len(full_output) > 8000:
            return full_output[:8000] + "\n...[OUTPUT TRUNCATED]..."
        return full_output
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 120s"

def call_llm(messages, tools):
    payload = {"model": LLM_MODEL, "messages": messages, "tools": tools, "tool_choice": "auto",
               "temperature": 0.1, "max_tokens": 4096}
    llm_http_response = requests.post(f"{LLM_BASE_URL}/chat/completions", json=payload, headers=LLM_HEADERS)
    llm_http_response.raise_for_status()
    msg = llm_http_response.json()["choices"][0]["message"]
    content = (msg.get("content") or "").strip()
    tool_calls = msg.get("tool_calls") or []
    return content, tool_calls


async def agent_loop(user_message: str, tools: list, mcp_tool_map: dict) -> None:
    messages: list[dict[str, object]] = [
        {"role": "system", "content": SYSTEM_PROMPT +  f". Allowed tools: {str(tools)}"}, 
        {"role": "user", "content": user_message}
    ]
    for turn in range(1, MAX_TURNS + 1):
        print(f"\n{'='*60}\n🔄 Turn {turn}\n{'='*60}")
        content, tool_calls = call_llm(messages, tools)
        if content:
            print(f"\n🤖 {content}")
        if not tool_calls:
            print("(no text output)" if not content else "")
            print("✅ Agent finished")
            return
        prefix = "\n" if content else ""
        messages.append({
            "role": "assistant", 
            "content": content or None, 
            "tool_calls": tool_calls
        })
        for tool_call in tool_calls:
            function = tool_call["function"]["name"]
            try:
                arguments = json.loads(tool_call["function"]["arguments"])
            except json.JSONDecodeError:
                arguments = {}
                result = "Error: Invalid JSON arguments provided by LLM."
                messages.append({"role": "assistant", "content": result or None, "tool_calls": [tool_call]})
                continue
            tool_call_id = tool_call["id"]
            print(f"{prefix}🔧 Tool: {function}({json.dumps(arguments, ensure_ascii=False)})")
            result = await call_tool_hybrid(function, arguments, mcp_tool_map)
            print(f"   → {result[:500]}{'...' if len(result)>500 else ''}")
            messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": result})
    print(f"\n⚠️  Max turns ({MAX_TURNS}) reached. Stopping.")


async def main(user_message):
    config_file = "mcp_settings.json"
    # Загружаем всё из JSON (stack будет держать соединения открытыми)
    stack, tools, tool_map = await load_mcp_servers_from_json(config_file)
    # pprint(tools)
    # pprint(tool_map) 
    try:
        # Передаем динамические инструменты и карту маршрутов в ваш цикл агента
        await agent_loop(
            user_message,
            tools=tools,
            mcp_tool_map=tool_map
        )
    finally:
        # Корректно закрываем все процессы MCP серверов при выходе
        await stack.aclose()

if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not prompt.strip():
        print("No task provided. Exiting.")
        sys.exit(1)
    asyncio.run(main(prompt))
