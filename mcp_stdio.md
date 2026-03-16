# How `mcp.run(transport="stdio")` Works

---

## The One-Line Summary

`mcp.run(transport="stdio")` turns the Python script into a **long-running process** that
reads MCP protocol messages from `stdin` and writes responses back to `stdout`.
The MCP Client (Inspector, `basic_client.py`, or the full agent) is the one that
**spawns this process as a child** and owns both ends of the pipe.

---

## Breaking Down the Command: `uv run mcp dev server/f1_server.py`

The full command has **three distinct layers**:

```
uv run   mcp dev   server/f1_server.py
  │         │              │
  │         │              └── The MCP server script to launch
  │         │
  │         └── A CLI sub-command from the mcp[cli] package
  │
  └── Runs a command inside the uv-managed .venv
```

### Layer 1 — `uv run`

`uv run` is not a Python command. It is the **uv project manager** finding the
correct `.venv`, activating it in a subprocess, and then running whatever comes
after it. It replaces the old pattern of manually running `.venv\Scripts\activate`.

Equivalent (old way, avoid):
```bash
.venv\Scripts\activate
mcp dev server/f1_server.py
```

Equivalent using uv (correct way):
```bash
uv run mcp dev server/f1_server.py
```

### Layer 2 — `mcp dev`

`mcp` is a **CLI tool** installed as part of the `mcp[cli]` package (the `[cli]`
extra is what adds this command-line interface). It ships several sub-commands:

| Sub-command | What it does |
|-------------|-------------|
| `mcp dev <script>` | Starts the MCP Inspector — launches the server script as a child process AND opens a browser-based testing UI |
| `mcp run <script>` | Starts the server in production mode (no Inspector UI) |
| `mcp install <script>` | Registers the server with Claude Desktop's config so it auto-starts |

`mcp dev` is specifically a **development tool**. It does two things internally:

1. Spawns `server/f1_server.py` as a child process (the MCP Server)
2. Starts a local web server (`localhost:5173`) that hosts the **MCP Inspector UI** — a browser interface that acts as an MCP Client, so tools can be called and tested manually without writing any client code

```
uv run mcp dev server/f1_server.py
         │
         ├── spawns ──► Python server/f1_server.py   (MCP Server process)
         │                      ▲  stdin/stdout pipe
         │                      │
         └── starts ──► Inspector web server          (MCP Client)
                               │
                               └── opens browser at http://localhost:5173
```

### Layer 3 — `server/f1_server.py`

The path to the server script passed to `mcp dev`. This is the process that gets
spawned as a child. `mcp dev` reads the script, calls it with the current Python
interpreter from the `.venv`, and connects its stdin/stdout to the Inspector.

---

### Why not just run `uv run python server/f1_server.py` directly?

Running the script directly with Python **works** but the terminal will appear to
freeze — the server is sitting there waiting for JSON-RPC input on stdin that never
arrives, because nothing is connected as a Client.

`mcp dev` is the shortcut that simultaneously starts the server **and** provides a
ready-made Client (the Inspector UI) so both ends of the pipe are connected from
the start.

---

## Step-by-Step: What Happens at Runtime

```
uv run mcp dev server/f1_server.py
        │
        │  1. uv resolves the .venv and launches Python
        │
        ▼
Python process starts  (server/f1_server.py)
        │
        │  2. Module-level code executes top-to-bottom:
        │       • httpx.Client(verify=False) is created
        │       • FastMCP("f1-server") is instantiated
        │       • All @mcp.tool() decorators register the 3 tools
        │         into the FastMCP registry
        │
        ▼
if __name__ == "__main__":
    mcp.run(transport="stdio")
        │
        │  3. FastMCP hands control to the MCP runtime loop.
        │     The process does NOT exit.
        │     It blocks here, waiting for input on stdin.
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│               STDIO TRANSPORT LOOP (blocking)               │
│                                                             │
│  stdin  ──────────────────────────────►  MCP message parser │
│                                              │              │
│                                    Deserialise JSON-RPC     │
│                                              │              │
│                                    Route to handler:        │
│                                      • initialize           │
│                                      • tools/list           │
│                                      • tools/call           │
│                                              │              │
│                                    Execute tool function    │
│                                    (e.g. get_driver_        │
│                                           standings(2024))  │
│                                              │              │
│                                    Serialise result         │
│                                              │              │
│  stdout ◄──────────────────────────  Write JSON-RPC response│
└─────────────────────────────────────────────────────────────┘
        │
        │  4. Loop repeats until the parent process closes the pipe
        │     (i.e. the Client disconnects or the Inspector is closed)
        │
        ▼
Process exits cleanly
```

---

## The JSON-RPC Wire Format

Every message on the pipe is a single line of **JSON-RPC 2.0**.
Below are the three most important exchanges.

### A — Handshake (initialize)

Client → Server:
```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","clientInfo":{"name":"mcp-inspector"}}}
```

Server → Client:
```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","serverInfo":{"name":"f1-server"},"capabilities":{"tools":{}}}}
```

### B — Tool Discovery (tools/list)

Client → Server:
```json
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
```

Server → Client:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "get_driver_standings",
        "description": "Returns the Formula 1 World Drivers Championship standings...",
        "inputSchema": {
          "type": "object",
          "properties": { "season": { "type": "integer" } },
          "required": ["season"]
        }
      },
      ...
    ]
  }
}
```

> The `description` field comes directly from the function's docstring.
> The `inputSchema` is auto-generated from the type annotations (`season: int`).

### C — Tool Execution (tools/call)

Client → Server:
```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_driver_standings","arguments":{"season":2024}}}
```

Server → Client:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      { "type": "text", "text": "P1  Verstappen  437 pts  (Red Bull)\nP2  Norris  374 pts  (McLaren)\n..." }
    ]
  }
}
```

---

## Why stdio and Not HTTP?

| Aspect | stdio | HTTP/SSE (Day 9) |
|--------|-------|-----------------|
| Setup complexity | Zero — no port, no server config | Requires binding to a port |
| Works across a network | No — process must be local | Yes — any machine on the network |
| Multiple simultaneous clients | No — one pipe, one client | Yes |
| Latency | Negligible (in-process pipe) | Small network overhead |
| Best suited for | Local tools, CLI agents, learning | Remote APIs, shared servers |

stdio is the **default and simplest** transport. The MCP Inspector and most
local clients use it. HTTP/SSE is introduced in Day 9 when remote access matters.

---

## What the MCP Inspector Does Differently

When running `uv run mcp dev server/f1_server.py`, the **Inspector** is a
web-based wrapper that acts as the Client. It:

1. Spawns `f1_server.py` as a child process (same as any MCP Client would)
2. Opens a browser UI at `http://localhost:5173`
3. Sends `tools/list` immediately so the UI can render all available tools
4. Lets the tool arguments be filled in manually via form fields
5. Sends `tools/call` when the **Run Tool** button is pressed
6. Displays the raw JSON-RPC response alongside the formatted result

The server itself has no knowledge that it is talking to the Inspector vs.
`basic_client.py` vs. `agent/f1_assistant.py` — it just reads stdin and
writes stdout regardless of who is on the other end.

---

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Running `python f1_server.py` directly without a Client | Terminal appears frozen — no output | This is correct behaviour. The server is waiting on stdin. Connect a Client or use the Inspector. |
| `print()` statements inside tool functions | Client receives garbled responses | Never use `print()` in an MCP server. Use the `logging` module — logs go to `stderr`, not `stdout`. |
| Missing `if __name__ == "__main__":` guard | Server starts when imported by tests or other modules | Always wrap `mcp.run()` in the guard. |
| Forgetting `@mcp.tool()` decorator | Tool does not appear in `tools/list` | The decorator is what registers the function with FastMCP. |
