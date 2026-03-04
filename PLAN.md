# MCP Server & Client — 14-Day Mastery Plan

> **Goal:** Go from zero AI knowledge to building MCP Servers, Clients, and a working Agentic App.
> **Time:** ~1 hour/day for 14 days
> **Stack:** Python 3.11+ (managed via **uv**), Ollama (local LLM), MCP SDK
> **All dependencies are managed via `uv` — no global installs, no venv confusion.**

---
## Environment Setup (~30 min)

### Install uv (Python project manager)
- [x] Install uv: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- [x] Verify: `uv --version`
- [x] Navigate to project folder: `cd mcp-server-client`

### Initialize project with uv
- [x] Run `uv init` (creates `pyproject.toml`, `hello.py`, `.python-version`)
- [x] Delete the generated `hello.py` (we don't need it)
- [x] Set Python version: `uv python pin 3.11` (or 3.12)
- [x] Run `uv sync` to create the `.venv` automatically

### Add project dependencies
- [x] `uv add mcp[cli]` — MCP SDK with CLI tools (includes Inspector)
- [x] `uv add ollama` — Ollama Python client
- [x] `uv add httpx` — Async HTTP client
- [x] `uv add beautifulsoup4` — HTML parsing (used Day 11)

### Install Ollama (local LLM runtime)
- [x] Download & install from [ollama.com](https://ollama.com)
- [x] Pull a model: `ollama pull llama3.2`
- [x] Verify: `ollama list` — should show `llama3.2`

### Verify everything works
- [x] `uv run python -c "import mcp; print('MCP OK')"` → prints `MCP OK`
- [x] `uv run python -c "import ollama; print('Ollama OK')"` → prints `Ollama OK`
- [x] `uv run python -c "import httpx; print('httpx OK')"` → prints `httpx OK`

### Create folder structure
- [ ] Create folders: `server/`, `client/`, `agent/`, `workspace/`
- [ ] Create empty `LEARNINGS.md`
- [ ] Update `README.md` with project description
- [ ] Commit everything

---

## Week 1 — Foundations & Your First MCP Server

### Day 1 — What are LLMs, Tokens, and Prompts?

**Concept (~20 min):**
- [ ] Read: What is an LLM (a text-prediction engine)
- [ ] Read: What are tokens (word chunks the model processes)
- [ ] Read: What is a prompt (your input to the model)
- [ ] Key insight: LLMs are **stateless** — every call is independent

**Hands-on (~40 min):**
- [ ] Create `day01_hello_llm.py`
- [ ] Use `ollama` Python library to send a prompt
- [ ] Print the response
- [ ] Experiment with 3 different prompts
- [ ] Run with: `uv run python day01_hello_llm.py`
- [ ] Commit

---

### Day 2 — APIs, JSON, and Tool Calling

**Concept (~20 min):**
- [ ] Understand REST APIs (request → response)
- [ ] Understand JSON (the universal data format)
- [ ] Key concept: **Tool calling** — LLM outputs structured JSON asking to run a function

**Hands-on (~40 min):**
- [ ] Create `day02_tool_calling.py`
- [ ] Define a function `get_weather(city: str)` returning fake data
- [ ] Use Ollama's tool-calling feature to let LLM decide when to call it
- [ ] Print the full request/response cycle
- [ ] Run with: `uv run python day02_tool_calling.py`
- [ ] Commit

---

### Day 3 — What is MCP? The Big Picture

**Concept (~20 min):**
- [ ] Read [MCP specification overview](https://modelcontextprotocol.io/introduction)
- [ ] Understand the 3 roles: **Host**, **Client**, **Server**
- [ ] Understand: MCP = standardized protocol for AI apps to discover & call tools

**Hands-on (~40 min):**
- [ ] Create `day03_notes.md`
- [ ] Draw ASCII architecture diagram: Host ↔ Client ↔ Server
- [ ] Write what each part does in your own words
- [ ] List 3 real-world MCP use cases
- [ ] Commit

---

### Day 4 — Your First MCP Server (Stdio Transport)

**Concept (~20 min):**
- [ ] Understand MCP transports: stdio vs HTTP/SSE
- [ ] Stdio = communication over stdin/stdout (simplest)
- [ ] Learn what `@mcp.tool()` decorator does

**Hands-on (~40 min):**
- [ ] Create `server/math_server.py`
- [ ] Build MCP server with tools: `add(a, b)` and `multiply(a, b)`
- [ ] Use `mcp.run()` with stdio transport
- [ ] Test with Inspector: `uv run mcp dev server/math_server.py`
- [ ] Commit

---

### Day 5 — Adding Resources and Prompts to Your Server

**Concept (~20 min):**
- [ ] MCP servers expose 3 primitives:
  - **Tools** — functions the LLM calls
  - **Resources** — data the client can read (like files, DB rows)
  - **Prompts** — reusable prompt templates
- [ ] Understand the difference between all three

**Hands-on (~40 min):**
- [ ] Create `server/notes_server.py`
- [ ] Add a resource `notes://list` returning notes from a JSON file
- [ ] Add a prompt template `summarize-notes`
- [ ] Test with Inspector: `uv run mcp dev server/notes_server.py`
- [ ] Commit

---

### Day 6 — Your First MCP Client

**Concept (~20 min):**
- [ ] Client's job: connect to server, discover tools/resources, wire into LLM
- [ ] Understand `ClientSession` and `StdioServerParameters`

**Hands-on (~40 min):**
- [ ] Create `client/basic_client.py`
- [ ] Connect to `math_server.py` using `StdioServerParameters`
- [ ] Call `list_tools()` and print available tools
- [ ] Call `add(2, 3)` programmatically and print result
- [ ] Run with: `uv run python client/basic_client.py`
- [ ] Commit

---

### Day 7 — Wiring It All Together: Client + LLM + Server

**Concept (~20 min):**
- [ ] The **agentic loop**:
  1. User query → Client sends to LLM (with tool definitions)
  2. LLM returns tool call → Client executes via MCP
  3. Result → back to LLM → final answer to user

**Hands-on (~40 min):**
- [ ] Create `client/agent_client.py`
- [ ] Build chat loop: user input → Ollama with MCP tools → execute tool calls → final answer
- [ ] Test: "What is 7 times 8?" → should trigger `multiply`
- [ ] Run with: `uv run python client/agent_client.py`
- [ ] Commit

** Week 1 Milestone Check:**
- [ ] `uv run mcp dev server/math_server.py` opens Inspector and shows tools
- [ ] Chat agent correctly calls `add`/`multiply` via MCP
- [ ] You can explain Host vs Client vs Server in your own words

---

## Week 2 — Real-World Servers, HTTP Transport & Full Agent

### Day 8 — Building a Practical MCP Server (File System)

**Concept (~20 min):**
- [ ] How to safely expose file operations as MCP tools
- [ ] Importance of restricting access (security sandboxing)

**Hands-on (~40 min):**
- [ ] Create `server/filesystem_server.py`
- [ ] Expose tools: `read_file(path)`, `list_directory(path)`, `search_files(pattern)`
- [ ] Restrict access to `workspace/` folder only
- [ ] Test with Inspector: `uv run mcp dev server/filesystem_server.py`
- [ ] Commit

---

### Day 9 — HTTP/SSE Transport

**Concept (~20 min):**
- [ ] Why HTTP transport matters (remote servers, web apps)
- [ ] Difference: stdio (local subprocess) vs Streamable HTTP/SSE (networked)

**Hands-on (~40 min):**
- [ ] Convert `math_server.py` to SSE transport → `server/math_server_sse.py`
- [ ] Runs as HTTP server on `localhost:8000`
- [ ] Update client to connect via SSE instead of stdio
- [ ] Verify both transports work
- [ ] Run server: `uv run python server/math_server_sse.py`
- [ ] Commit

---

### Day 10 — Multi-Server Client

**Concept (~20 min):**
- [ ] Real agents connect to **multiple** MCP servers simultaneously
- [ ] Client aggregates all tools from all servers

**Hands-on (~40 min):**
- [ ] Create `client/multi_server_client.py`
- [ ] Connect to `math_server` (stdio) + `filesystem_server` (stdio)
- [ ] Aggregate tools from both, pass to LLM
- [ ] Test: "List the files in workspace/ and then add up the number of files"
- [ ] Run with: `uv run python client/multi_server_client.py`
- [ ] Commit

---

### Day 11 — Building a Web Scraper MCP Server

**Concept (~20 min):**
- [ ] How to wrap external libraries (`httpx` + `beautifulsoup4`) as MCP tools
- [ ] Async tools in MCP

**Hands-on (~40 min):**
- [ ] Create `server/web_server.py`
- [ ] Expose tools: `fetch_page(url)`, `extract_text(url)`
- [ ] Use `httpx` for fetching, `beautifulsoup4` for parsing
- [ ] Test with Inspector: `uv run mcp dev server/web_server.py`
- [ ] Commit

---

### Day 12 — Error Handling, Logging, and Best Practices

**Concept (~20 min):**
- [ ] MCP error handling patterns (`isError: true`)
- [ ] Input validation, structured logging
- [ ] Writing good tool descriptions (they're part of the LLM prompt!)

**Hands-on (~40 min):**
- [ ] Add input validation to all servers
- [ ] Add try/except with proper MCP error responses
- [ ] Add Python `logging` module with clear messages
- [ ] Improve all tool descriptions to be LLM-friendly
- [ ] Run all servers through Inspector to verify
- [ ] Commit

---

### Day 13 — Capstone: Personal Assistant Agent

**Concept (~20 min):**
- [ ] How to combine everything into one agent
- [ ] Multi-step tool usage and conversation memory

**Hands-on (~40 min):**
- [ ] Create `agent/assistant.py`
- [ ] Build polished CLI agent connecting to ALL MCP servers
- [ ] Features: conversation memory, multi-step tool chains
- [ ] Test: "Fetch the Python homepage, summarize it, and save to workspace/summary.txt"
- [ ] Run with: `uv run python agent/assistant.py`
- [ ] Commit

** Week 2 Milestone Check:**
- [ ] Single client uses tools from 2+ servers in one conversation
- [ ] "Fetch X, summarize it, save to file" works end-to-end
- [ ] All servers have proper error handling and logging

---

### Day 14 — Review, Document, and Next Steps

**Concept (~20 min):**
- [ ] Where MCP fits in the ecosystem (vs LangChain, OpenAI Assistants, etc.)
- [ ] Review all concepts learned

**Hands-on (~40 min):**
- [ ] Write proper `README.md`: what each component does, how to run
- [ ] Fill in `LEARNINGS.md` with key concepts in your own words
- [ ] Tag the repo `v1.0`: `git tag v1.0 && git push --tags`
- [ ] Commit

---

## Daily Log

| Day | Date | Status | Key Takeaway |
|-----|------|--------|--------------|
| 0 | | Not started | |
| 1 | | Not started | |
| 2 | | Not started | |
| 3 | | Not started | |
| 4 | | Not started | |
| 5 | | Not started | |
| 6 | | Not started | |
| 7 | | Not started | |
| 8 | | Not started | |
| 9 | | Not started | |
| 10 | | Not started | |
| 11 | | Not started | |
| 12 | | Not started | |
| 13 | | Not started | |
| 14 | | Not started | |

---

## Repo Structure

```
mcp-server-client/
├── server/
│   ├── math_server.py          (Day 4)
│   ├── math_server_sse.py      (Day 9)
│   ├── notes_server.py         (Day 5)
│   ├── filesystem_server.py    (Day 8)
│   └── web_server.py           (Day 11)
├── client/
│   ├── basic_client.py         (Day 6)
│   ├── agent_client.py         (Day 7)
│   └── multi_server_client.py  (Day 10)
├── agent/
│   └── assistant.py            (Day 13)
├── workspace/                   (sandbox for filesystem server)
├── day01_hello_llm.py
├── day02_tool_calling.py
├── day03_notes.md
├── pyproject.toml               (uv manages this)
├── uv.lock                      (auto-generated lockfile)
├── .python-version              (pinned Python version)
├── plan.md                      ← YOU ARE HERE
├── README.md
└── LEARNINGS.md
```

---

## Quick Command Reference (uv)

| What | Command |
|------|---------|
| **Run any script** | `uv run python <script.py>` |
| **Add a dependency** | `uv add <package>` |
| **Remove a dependency** | `uv remove <package>` |
| **Sync/install all deps** | `uv sync` |
| **Run MCP Inspector** | `uv run mcp dev server/<server>.py` |
| **Install MCP server** | `uv run mcp install server/<server>.py` |
| **Open Python REPL** | `uv run python` |
| **Check installed packages** | `uv pip list` |
| **Update a package** | `uv add <package> --upgrade` |

> **Always use `uv run`** to execute scripts. This ensures the correct virtual environment and dependencies are used automatically. Never activate the `.venv` manually.

---

## Key Resources

- [MCP Official Docs](https://modelcontextprotocol.io)
- [MCP Python SDK GitHub](https://github.com/modelcontextprotocol/python-sdk)
- [Ollama Docs](https://ollama.com)
- [Ollama Python Library](https://github.com/ollama/ollama-python)
- [uv Documentation](https://docs.astral.sh/uv/)
