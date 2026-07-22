# chebupelka-node

Node.js 22 port of the minimal coding agent from [`chebupelka/chebupelka.py`](../chebupelka/chebupelka.py).

## Features

- **Tool calling** — the model calls the `bash` tool to execute shell commands
- **Agent loop** — keeps calling tools until the task is solved
- **OpenAI-compatible API** — works with Ollama, vLLM, LM Studio, or any server exposing an OpenAI-compatible endpoint
- **Zero dependencies** — uses only Node.js built-ins (`fetch`, `child_process`)

## Quick Start

```bash
# Run with a task
node index.js "Write a Python script that recursively finds all .py files in the current directory"
```

## Configuration

All settings can be overridden via environment variables:

| Variable             | Description                   | Default                         |
|----------------------|-------------------------------|---------------------------------|
| `LLM_BASE_URL`       | URL of your LLM server        | `http://192.168.0.118:8080/v1`  |
| `LLM_API_KEY`        | Authorization key             | `llama.cpp`                     |
| `LLM_MODEL`          | Model name                    | `Qwen3.6-27B-Q4_K_M.gguf`      |
| `MAX_TURNS`          | Maximum agent iterations      | `1000`                          |
| `COMMAND_TIMEOUT_MS` | Bash command timeout (ms)     | `120000`                        |

### Example — Ollama

```bash
LLM_BASE_URL=http://localhost:11434/v1 \
LLM_API_KEY=ollama \
LLM_MODEL=qwen3.6-35b-a3b \
node index.js "your task here"
```

## How It Works

```
User -> Agent Loop -> LLM (chat/completions API)
                    ↕
          Tool calls (bash)
            ↓
      Command result
            ↑
      Back to loop with result
```

1. User provides a task via CLI arguments
2. Agent sends the conversation history to the LLM
3. If the model wants to call a tool — the command runs locally via `child_process.exec`
4. Result is sent back to the model, loop repeats
5. When the model stops calling tools — task is done

## Extending Tools

Add a new function to `TOOLS_MAP` and describe it in `LLM_TOOLS`:

```js
// In LLM_TOOLS:
{
  type: "function",
  function: {
    name: "read_file",
    description: "Read the contents of a file.",
    parameters: {
      type: "object",
      properties: {
        path: { type: "string", description: "File path." },
      },
      required: ["path"],
    },
  },
}

// In TOOLS_MAP:
const TOOLS_MAP = { bash: runBash, read_file: readFile };
```

## Requirements

- Node.js ≥ 22
