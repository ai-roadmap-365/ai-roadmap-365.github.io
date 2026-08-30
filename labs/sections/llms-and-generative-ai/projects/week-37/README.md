# Project: Week 37 -- Command-Line AI Assistant

## Overview
Build an enterprise-grade, streaming, modular Command-Line AI Assistant in Python. The assistant integrates the full LLM API engineering stack developed across Days 253–259: an asynchronous Read-Eval-Print Loop (REPL) using `prompt_toolkit` and `rich`, real-time Server-Sent Events (SSE) token streaming with in-place Markdown repainting, JSON Schema tool execution with sandboxed filesystem operations, a sliding context window memory manager with prompt cache breakpoints, token bucket traffic shaping, and a real-time multi-model financial cost meter.

## Learning objectives
- Architect an asynchronous, non-blocking terminal REPL with multi-line input, history buffers, and slash commands (`/help`, `/cost`, `/clear`, `/model`, `/export`, `/exit`).
- Implement real-time token streaming with sub-500ms TTFT and live 60Hz Markdown rendering via `rich.live`.
- Integrate a sandboxed local tool execution router supporting file reading, safe arithmetic, and read-only shell execution.
- Maintain multi-turn conversational memory with an automated context sliding window and prompt cache breakpoints (`cache_control: ephemeral`).
- Enforce token bucket rate limiting and maintain a live multi-tier token expenditure ledger.
- Execute automated regression test suites verifying memory sliding, tool routing, streaming token assembly, and cost calculations.

## Architecture
```
assistant_cli/
  ├── __init__.py
  ├── repl.py                 # Interactive asynchronous prompt_toolkit loop
  ├── stream_renderer.py      # Rich Live 60Hz Markdown stream repainter
  ├── memory_manager.py       # Pinned system context + sliding deque window
  ├── tool_router.py          # Pydantic schema validation & sandboxed tool dispatch
  ├── cost_ledger.py          # Token bucket rate limiter & multi-model pricing tracker
  └── gateway.py              # Multi-provider client wrapper (Claude, OpenAI, Local)
tests/
  ├── test_memory_manager.py  # Sliding window and turn eviction assertions
  ├── test_tool_router.py     # Tool dispatch and path sandboxing assertions
  └── test_cost_ledger.py     # Token pricing matrices and token bucket assertions
```

## Core Functional Components

### 1. Asynchronous REPL & Terminal Interface (`repl.py`)
- Powered by `prompt_toolkit.PromptSession` for multi-line inputs and arrow-key history recall.
- Custom styling with formatted `❯ ` prompt symbols and dynamic session status bars.
- Comprehensive slash command router:
  - `/help`: Lists available commands, active model, and registered tools.
  - `/cost`: Prints a formatted table of total input, cached, and output tokens, along with total USD cost.
  - `/clear`: Clears conversation history buffer while keeping the pinned system prompt intact.
  - `/model <id>`: Hot-swaps the underlying LLM engine between fast and reasoning models.
  - `/export <path>`: Exports the complete conversation history to a structured Markdown log.
  - `/exit`: Terminated gracefully with a session summary card.

### 2. Live Markdown Streamer (`stream_renderer.py`)
- Employs `rich.live.Live` with `rich.markdown.Markdown` to repaint arriving token chunks dynamically.
- Eliminates duplicate terminal lines and delivers a smooth typewriter reading experience.
- Handles `Ctrl+C` (SIGINT) gracefully to cancel active streams without exiting the REPL.

### 3. Memory & Context Manager (`memory_manager.py`)
- Pins the system prompt and tool definitions permanently at message index 0 with prompt caching breakpoints.
- Implements an automated sliding window (`deque(maxlen=N)`) to evict the oldest non-system turns when history exceeds configured limits.
- Automatically generates memory summaries when conversations exceed token budget thresholds.

### 4. Tool Execution Dispatcher (`tool_router.py`)
- Dispatches model tool calls to local Python functions with strict Pydantic argument validation.
- Sandboxes file reading tools to the current workspace root (`is_safe_path`).
- Supports multi-tool recursive loops: executes tool calls, appends tool responses, and triggers completion turns automatically.

### 5. Token Bucket & Financial Cost Meter (`cost_ledger.py`)
- Tracks prompt tokens, cache read tokens, and completion tokens across Anthropic, OpenAI, and local backends.
- Calculates exact dollar costs per turn using official pricing matrices.
- Enforces client-side Token Bucket rate limiting to shape burst traffic and prevent HTTP 429 errors.

## Expected output
When executing the CLI assistant demo and automated test suite:
```
======================================================================
WEEK 37 PROJECT: COMMAND-LINE AI ASSISTANT VERIFICATION SUITE
======================================================================
[1/4] Testing Memory Manager & System Pinning:
      - System Prompt Pinned at Index 0: PASSED
      - Sliding Window Eviction (Turns > 8): PASSED (Oldest turns pruned)
      - Cache Breakpoint Metadata Present: PASSED

[2/4] Testing Sandboxed Tool Dispatcher:
      - Tool 'read_file' Execution: PASSED (Returned file content)
      - Path Traversal Block ('../../etc/passwd'): PASSED (PermissionError caught)
      - Safe Math Calculator: PASSED (Evaluated 45 * 12 = 540)

[3/4] Testing Real-Time Stream Renderer:
      - Live Markdown Repainting: PASSED (60Hz buffer update verified)
      - SIGINT Interception: PASSED (Stream cancelled, REPL restored)

[4/4] Testing Cost Ledger & Rate Limiter:
      - 10k Cached + 500 Input + 200 Output Tokens: $0.0075 [PASS]
      - Token Bucket Burst Smoothing: PASSED (10 tokens refilled at 2/sec)
      - Full Jitter Backoff Calculation: PASSED (Interval within bounds)

======================================================================
ALL 4 PROJECT SUBSYSTEMS VERIFIED -- 12 TESTS PASSED (100% GREEN)
======================================================================
```

## Validation
Execute the project regression suite to verify complete compliance:
```bash
pytest tests/ -v
```
All tests must pass with 0 errors, validating memory sliding, tool sandboxing, streaming repainting, and cost metering.
