# Coding Agent (PHP 8.2 Port)

Minimal coding agent that communicates with an LLM via an OpenAI-compatible API and executes bash commands.

## Features

- **Tool calling** — The model calls tools (by default `bash`).
- **Interaction loop** — The agent calls tools until the task is solved.
- **OpenAI-compatible API** — Works with Ollama, vLLM, LM Studio, and any server with an OpenAI-compatible interface.
- **No SDK dependency** — Only `guzzlehttp/guzzle` for HTTP requests.

## Quick Start

```bash
# Install dependencies
composer install

# Run with a task
php cli.php "Write a Python script that recursively finds all .py files in the current directory"
```

## Configuration

Edit the constants in [`src/Config.php`](src/Config.php):

| Constant           | Description                        |
|--------------------|------------------------------------|
| `LLM_BASE_URL`     | Your LLM server URL                |
| `LLM_API_KEY`      | Authorization key                  |
| `LLM_MODEL`        | Model name                         |
| `MAX_TURNS`        | Maximum agent loop iterations      |
| `COMMAND_TIMEOUT`  | Bash command timeout (seconds)     |

### Example with Ollama

```php
public const string LLM_BASE_URL = 'http://localhost:11434/v1';
public const string LLM_API_KEY = 'ollama';
public const string LLM_MODEL = 'qwen3.6-35b-a3b';
```

## How It Works

```
User → Agent Loop → LLM (chat/completions API)
                    ↕
          Tool calls (bash)
                    ↓
              Command result
                    ↑
          Back to loop with result
```

1. User provides a task via CLI
2. Agent sends message history to the LLM
3. If the model wants to call a tool — it is executed locally via `proc_open`
4. The result is sent back to the model, and the loop continues
5. When the model stops calling tools — the task is complete

## Adding Tools

Add a new `match` branch in [`src/Tools.php`](src/Tools.php)::call() and a new entry in [`src/Config.php`](src/Config.php)::toolsDefinition():

```php
// In Config.php toolsDefinition():
[
    'type' => 'function',
    'function' => [
        'name' => 'read_file',
        'description' => 'Read the contents of a file.',
        'parameters' => [
            'type' => 'object',
            'properties' => [
                'path' => ['type' => 'string', 'description' => 'File path.'],
            ],
            'required' => ['path'],
        ],
    ],
],

// In Tools.php call():
'read_file' => file_get_contents($arguments['path'] ?? ''),
```

## Requirements

- PHP ≥ 8.2
- `guzzlehttp/guzzle` — the only runtime dependency
