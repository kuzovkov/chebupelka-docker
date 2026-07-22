<?php

declare(strict_types=1);

namespace Chebupelka;

final class Config
{
    public const LLM_BASE_URL = 'http://192.168.0.118:8080/v1';
    public const LLM_API_KEY = 'llama.cpp';
    public const LLM_MODEL = 'Qwen3.6-27B-Q4_K_M.gguf';
    public const MAX_TURNS = 1000;
    public const COMMAND_TIMEOUT = 120;
    public const LLM_MAX_TOKENS = 4096;
    public const LLM_TEMPERATURE = 0.1;

    public const SYSTEM_PROMPT = <<<'PROMPT'
You are a coding agent. Your job is to help the user with programming tasks.

You have access to ONE tool: `bash` — which executes shell commands and returns stdout/stderr.

Workflow:
1. Plan what needs to be done.
2. Use `bash` to read files, run commands, write code, etc.
3. After gathering enough information or completing the task, give your final answer in natural language.
4. To finish, reply with a regular message (no tool call).

Be concise. Explain what you're doing before each command.
PROMPT;

    /** @return array<int, array<string, mixed>> */
    public static function toolsDefinition(): array
    {
        return [
            [
                'type' => 'function',
                'function' => [
                    'name' => 'bash',
                    'description' => 'Execute a shell command and return the output.',
                    'parameters' => [
                        'type' => 'object',
                        'properties' => [
                            'command' => [
                                'type' => 'string',
                                'description' => 'The bash command to execute.',
                            ],
                        ],
                        'required' => ['command'],
                    ],
                ],
            ],
        ];
    }
}
