<?php

declare(strict_types=1);

namespace Chebupelka;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\GuzzleException;

final class Agent
{
    private readonly Client $client;

    /** @var array<int, array<string, mixed>> */
    private array $messages;

    public function __construct(
        private readonly string $baseUrl,
        private readonly string $apiKey,
        private readonly string $model,
    ) {
        $this->client = new Client([
            'base_uri' => $this->baseUrl,
            'headers' => [
                'Content-Type' => 'application/json',
                'Authorization' => 'Bearer ' . $this->apiKey,
            ],
        ]);
        $this->messages = [];
    }

    public function run(string $userMessage): void
    {
        $this->messages = [
            ['role' => 'system', 'content' => Config::SYSTEM_PROMPT],
            ['role' => 'user', 'content' => $userMessage],
        ];

        for ($turn = 1; $turn <= Config::MAX_TURNS; $turn++) {
            $this->printTurnHeader($turn);
            ['content' => $content, 'tool_calls' => $toolCalls] = $this->callLLM();

            if ($content !== '') {
                echo "\n🤖 " . $content . PHP_EOL;
            }

            if ($toolCalls === []) {
                if ($content === '') {
                    echo '(no text output)' . PHP_EOL;
                }
                echo '✅ Agent finished' . PHP_EOL;
                return;
            }

            $prefix = $content !== '' ? "\n" : '';

            foreach ($toolCalls as $toolCall) {
                $functionName = $toolCall['function']['name'];
                $arguments = json_decode($toolCall['function']['arguments'], true, 512, JSON_THROW_ON_ERROR);
                $toolCallId = $toolCall['id'];

                echo $prefix . "🔧 Tool: {$functionName}(" . json_encode($arguments, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . ')' . PHP_EOL;

                $result = Tools::call($functionName, $arguments);
                $display = mb_strlen($result) > 500 ? mb_substr($result, 0, 500) . '...' : $result;
                echo '   → ' . $display . PHP_EOL;

                // Build assistant message with a single tool_call for proper API formatting
                $assistantMessage = [
                    'role' => 'assistant',
                    'tool_calls' => [$toolCall],
                ];
                if ($content !== '') {
                    $assistantMessage['content'] = $content;
                }
                $this->messages[] = $assistantMessage;

                $this->messages[] = [
                    'role' => 'tool',
                    'tool_call_id' => $toolCallId,
                    'content' => $result,
                ];
            }
        }

        echo "\n⚠️  Max turns (" . Config::MAX_TURNS . ') reached. Stopping.' . PHP_EOL;
    }

    /**
     * @return array{content: string, tool_calls: array<int, array<string, mixed>>}
     */
    private function callLLM(): array
    {
        $payload = [
            'model' => $this->model,
            'messages' => $this->cleanMessagesForPayload($this->messages),
            'tools' => Config::toolsDefinition(),
            'tool_choice' => 'auto',
            'temperature' => Config::LLM_TEMPERATURE,
            'max_tokens' => Config::LLM_MAX_TOKENS,
        ];

        try {
            $response = $this->client->post('chat/completions', [
                'json' => $payload,
            ]);
        } catch (GuzzleException $e) {
            throw new \RuntimeException('LLM request failed: ' . $e->getMessage());
        }

        /** @var array<string, mixed> $body */
        $body = json_decode($response->getBody()->getContents(), true, 512, JSON_THROW_ON_ERROR);
        /** @var array<string, mixed> $message */
        $message = $body['choices'][0]['message'];

        $content = (string) ($message['content'] ?? '');
        $content = trim($content);
        /** @var array<int, array<string, mixed>> $toolCalls */
        $toolCalls = $message['tool_calls'] ?? [];

        return [
            'content' => $content,
            'tool_calls' => $toolCalls,
        ];
    }

    private function printTurnHeader(int $turn): void
    {
        echo PHP_EOL . str_repeat('=', 60) . PHP_EOL;
        echo "🔄 Turn {$turn}" . PHP_EOL;
        echo str_repeat('=', 60) . PHP_EOL;
    }

    /**
     * Clean messages for API payload — remove null/empty content fields.
     *
     * @param array<int, array<string, mixed>> $messages
     * @return array<int, array<string, mixed>>
     */
    private function cleanMessagesForPayload(array $messages): array
    {
        $cleaned = [];
        foreach ($messages as $msg) {
            $copy = $msg;
            // If content is empty string, treat as null for cleaner API payload
            if (isset($copy['content']) && $copy['content'] === '') {
                unset($copy['content']);
            }
            $cleaned[] = $copy;
        }
        return $cleaned;
    }
}
