/**
 * Minimal coding agent loop — one tool: bash.
 * Node.js 22 port of chebupelka Python agent.
 */
import { spawn } from "node:child_process";

// ── Configuration ──────────────────────────────────────────────────────────
const LLM_BASE_URL = process.env.LLM_BASE_URL || "http://192.168.0.118:8080/v1";
const LLM_API_KEY = process.env.LLM_API_KEY || "llama.cpp";
const LLM_MODEL = process.env.LLM_MODEL || "Qwen3.6-27B-Q4_K_M.gguf";
const MAX_TURNS = parseInt(process.env.MAX_TURNS, 10) || 1000;
const TIMEOUT_MS = parseInt(process.env.COMMAND_TIMEOUT_MS, 10) || 120_000;

// ── System Prompt ─────────────────────────────────────────────────────────
const SYSTEM_PROMPT = `\
You are a coding agent. Your job is to help the user with programming tasks.

You have access to ONE tool: \`bash\` — which executes shell commands and returns stdout/stderr.

Workflow:
1. Plan what needs to be done.
2. Use \`bash\` to read files, run commands, write code, etc.
3. After gathering enough information or completing the task, give your final answer in natural language.
4. To finish, reply with a regular message (no tool call).

Be concise. Explain what you're doing before each command.`;

// ── Tool Definitions ──────────────────────────────────────────────────────
const LLM_TOOLS = [
  {
    type: "function",
    function: {
      name: "bash",
      description: "Execute a shell command and return the output.",
      parameters: {
        type: "object",
        properties: {
          command: { type: "string", description: "The bash command to execute." },
        },
        required: ["command"],
      },
    },
  },
];

// ── Tool Implementations ──────────────────────────────────────────────────
function runBash(command) {
  return new Promise((resolve) => {
    const child = spawn("/bin/bash", ["-c", command]);
    const timer = setTimeout(() => { child.kill(); resolve("Error: command timed out after 120s"); }, TIMEOUT_MS);

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => { stdout += chunk.toString(); });
    child.stderr.on("data", (chunk) => { stderr += chunk.toString(); });

    child.on("exit", (code) => {
      clearTimeout(timer);
      const result = stdout + (stderr ? `\nSTDERR:\n${stderr}` : "");
      resolve(`Exit code: ${code ?? -1}\n${result}`);
    });

    child.on("error", (err) => {
      clearTimeout(timer);
      resolve(`Error: ${err.message}`);
    });
  });
}

const TOOLS_MAP = { bash: runBash };

async function callTool(name, arguments_) {
  const fn = TOOLS_MAP[name];
  if (!fn) return `Error: unknown tool '${name}'`;
  try {
    return await fn(...Object.values(arguments_));
  } catch (err) {
    return `Error calling ${name}: ${err.message}`;
  }
}

// ── LLM Call ──────────────────────────────────────────────────────────────
async function callLLM(messages) {
  const payload = {
    model: LLM_MODEL,
    messages,
    tools: LLM_TOOLS,
    tool_choice: "auto",
    temperature: 0.1,
    max_tokens: 4096,
  };

  const response = await fetch(`${LLM_BASE_URL}/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${LLM_API_KEY}`,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`LLM request failed (${response.status}): ${body}`);
  }

  const data = await response.json();
  const msg = data.choices[0].message;
  const content = (msg.content || "").trim();
  const toolCalls = msg.tool_calls || [];
  return [content, toolCalls];
}

// ── Agent Loop ────────────────────────────────────────────────────────────
async function agentLoop(userMessage) {
  const messages = [
    { role: "system", content: SYSTEM_PROMPT },
    { role: "user", content: userMessage },
  ];

  for (let turn = 1; turn <= MAX_TURNS; turn++) {
    console.log(`\n${"=".repeat(60)}`);
    console.log(`🔄 Turn ${turn}`);
    console.log("=".repeat(60));

    const [content, toolCalls] = await callLLM(messages);

    if (content) console.log(`\n🤖 ${content}`);

    if (toolCalls.length === 0) {
      if (!content) console.log("(no text output)");
      console.log("✅ Agent finished");
      return;
    }

    const prefix = content ? "\n" : "";
    for (const toolCall of toolCalls) {
      const function_ = toolCall.function;
      const fnName = function_.name;
      const args = JSON.parse(function_.arguments);
      const toolCallId = toolCall.id;

      console.log(`${prefix}🔧 Tool: ${fnName}(${JSON.stringify(args)})`);

      const result = await callTool(fnName, args);
      const display = result.length > 500 ? result.slice(0, 500) + "..." : result;
      console.log(`   → ${display}`);

      messages.push({
        role: "assistant",
        content: content || null,
        tool_calls: [toolCall],
      });
      messages.push({
        role: "tool",
        tool_call_id: toolCallId,
        content: result,
      });
    }
  }

  console.log(`\n⚠️  Max turns (${MAX_TURNS}) reached. Stopping.`);
}

// ── CLI Entry ─────────────────────────────────────────────────────────────
const prompt = process.argv.slice(2).join(" ");
if (!prompt.trim()) {
  console.error("No task provided. Exiting.");
  process.exit(1);
}

agentLoop(prompt).catch((err) => {
  console.error("Fatal:", err.message);
  process.exit(1);
});
