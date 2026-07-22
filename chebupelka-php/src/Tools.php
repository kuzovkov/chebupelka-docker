<?php

declare(strict_types=1);

namespace Chebupelka;

final class Tools
{
    public static function bash(string $command): string
    {
        $descriptors = [
            0 => ['pipe', 'r'],
            1 => ['pipe', 'w'],
            2 => ['pipe', 'w'],
        ];

        $process = proc_open('bash -c ' . escapeshellarg($command), $descriptors, $pipes);

        if (!is_resource($process)) {
            return 'Error: could not start process';
        }

        fclose($pipes[0]); // close stdin

        // Read stdout and stderr
        $stdout = stream_get_contents($pipes[1]);
        $stderr = stream_get_contents($pipes[2]);

        $status = proc_close($process);

        $output = (string) $stdout;
        if (trim((string) $stderr) !== '') {
            $output .= "\nSTDERR:\n" . $stderr;
        }

        return "Exit code: {$status}\n" . $output;
    }

    /**
     * @param array<string, mixed> $arguments
     */
    public static function call(string $name, array $arguments): string
    {
        return match ($name) {
            'bash' => self::bash($arguments['command'] ?? ''),
            default => "Error: unknown tool '{$name}'",
        };
    }
}
