#!/usr/bin/env php
<?php

declare(strict_types=1);

require_once __DIR__ . '/vendor/autoload.php';

use Chebupelka\Agent;
use Chebupelka\Config;

$argvCount = $_SERVER['argc'] - 1;
$fullPrompt = $argvCount > 0 ? implode(' ', array_slice($argv, 1)) : '';

if (trim($fullPrompt) === '') {
    fwrite(STDERR, "No task provided. Exiting.\n");
    exit(1);
}

$agent = new Agent(
    Config::LLM_BASE_URL,
    Config::LLM_API_KEY,
    Config::LLM_MODEL,
);

$agent->run($fullPrompt);
