# MCP Server & Client — 14-Day Mastery Plan
## Theme: F1 Race Intelligence Hub

> **Goal:** Go from zero AI knowledge to building MCP Servers, Clients, and a working Agentic App.
</br>**Theme:** Build a personal F1 Race Intelligence Hub — query real championship data, live timing, and race history via a conversational AI agent.
</br>**APIs used:** [OpenF1](https://openf1.org) (real-time telemetry, no key) + [Jolpica-F1](https://api.jolpi.ca/ergast/f1/) (historical data, no key) — both 100% free and open-source.
</br>**Stack:** Python 3.11+ (managed via **uv**), Ollama (local LLM), MCP SDK
></br></br>**All dependencies are managed via `uv` — no global installs, no venv confusion.**

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
- [x] Create folders: `server/`, `client/`, `agent/`, `workspace/`
- [x] Update `README.md` with project description
- [x] Commit everything

---

## Week 1 — Foundations & The First MCP Server

### Day 1 — What are LLMs, Tokens, and Prompts?

**Concept (~20 min):**
- [x] Read: What is an LLM (a text-prediction engine)
- [x] Read: What are tokens (word chunks which the model processes)
- [x] Read: What is a prompt (input sent to the model)
- [x] Key insight: LLMs are **stateless** — every call is independent

**Hands-on (~40 min):**
- [x] Create `llm_intro.py` - To learn how to send prompts to the LLM (Ollama3.2).
- [x] Use `ollama` Python library to send a prompt
- [x] Print the response
- [x] Experiment with 3 different prompts
- [x] Run with: `uv run python llm_intro.py`
- [x] Commit

---

### Day 2 — APIs, JSON, and Tool Calling

**Concept (~20 min):**
- [x] Understand REST APIs (request → response)
- [x] Understand JSON (the universal data format)
- [x] Key concept: **Tool calling** — LLM outputs structured JSON asking to run a function

**Hands-on (~40 min):**
- [x] Create `day02_tool_calling.py`
- [x] Define a function `get_weather(city: str)` returning fake data
- [x] Use Ollama's tool-calling feature to let LLM decide when to call it
- [x] Print the full request/response cycle
- [x] Run with: `uv run python day02_tool_calling.py`
- [x] Commit

---

### Day 3 — What is MCP? The Big Picture

**Concept (~20 min):**
- [x] Read [MCP specification overview](https://modelcontextprotocol.io/introduction)
- [x] Understand the 3 roles: **Host**, **Client**, **Server**
- [x] Understand: MCP = standardized protocol for AI apps to discover & call tools

**Hands-on (~40 min):**
- [x] Create `day03_notes.md`
- [x] Draw ASCII architecture diagram in F1 context:
  ```
  User (Host)
    └── agent_client.py (Client)
          ├── f1_server.py     ← Jolpica API: standings, results
          ├── f1_live_server.py ← OpenF1 API: lap times, pit stops
          └── filesystem_server.py ← saves analysis to workspace/
  ```
- [x] Describe each part's role in plain terms using the F1 scenario
- [x] List 3 F1-specific MCP use cases (e.g. "Ask the agent who leads the 2024 WDC")
- [x] Commit

---

### Day 4 — First MCP Server: F1 Historical Data (Stdio Transport)

**Concept (~20 min):**
- [x] Understand MCP transports: stdio vs HTTP/SSE
- [x] Stdio = communication over stdin/stdout (simplest)
- [x] Learn what `@mcp.tool()` decorator does
- [x] Explore the [Jolpica-F1 API](https://api.jolpi.ca/ergast/f1/) — free, no key, returns JSON

**Hands-on (~40 min):**
- [x] Create `server/f1_server.py`
- [x] Build MCP server with 3 tools using `httpx` to call Jolpica:
  - `get_driver_standings(season: int)` → WDC standings for any year
  - `get_race_schedule(season: int)` → all rounds for a season
  - `get_race_result(season: int, round: int)` → finishing order for one race
- [x] Use `mcp.run()` with stdio transport
- [x] Test with Inspector: `uv run mcp dev server/f1_server.py`
- [x] In Inspector, call `get_driver_standings(2024)` and verify Verstappen appears
- [x] Commit

---

### Day 5 — Adding Resources and Prompts to the F1 Server

**Concept (~20 min):**
- [x] MCP servers expose 3 primitives:
  - **Tools** — functions the LLM calls
  - **Resources** — data the client can read (like files, DB rows)
  - **Prompts** — reusable prompt templates
- [x] Understand the difference between all three

**Hands-on (~40 min):**
- [x] Extend `server/f1_server.py` (no new file needed):
  - Add a 4th tool: `get_constructor_standings(season: int)` → WCC standings
  - Add a **resource** `f1://drivers/current` that returns the current season's driver list as JSON
  - Add a **prompt template** `analyze-driver` that takes a `driver_name` argument and returns a structured analysis prompt
- [x] Test with Inspector: `uv run mcp dev server/f1_server.py`
- [x] In Inspector, read the `f1://drivers/current` resource and verify
- [x] In Inspector, render the `analyze-driver` prompt with `driver_name=Leclerc`
- [x] Commit

---

### Day 6 — First MCP Client: Querying the F1 Server

**Concept (~20 min):**
- [x] Client's job: connect to server, discover tools/resources, wire into LLM
- [x] Understand `ClientSession` and `StdioServerParameters`

**Hands-on (~40 min):**
- [x] Create `client/basic_client.py`
- [x] Connect to `f1_server.py` using `StdioServerParameters`
- [x] Call `list_tools()` and print all available F1 tools
- [x] Call `get_driver_standings(2024)` programmatically and print the top 5 drivers
- [x] Call `get_race_result(2024, 1)` and print the Bahrain GP result
- [x] Read the `f1://drivers/current` resource and print the driver list
- [x] Run with: `uv run python client/basic_client.py`
- [x] Commit

---

### Day 7 — Wiring It All Together: F1 Chat Agent + LLM + Server

**Concept (~20 min):**
- [x] The **agentic loop**:
  1. User query → Client sends to LLM (with tool definitions)
  2. LLM returns tool call → Client executes via MCP
  3. Result → back to LLM → final answer to user

**Hands-on (~40 min):**
- [x] Create `client/agent_client.py`
- [x] Build chat loop: user input → Ollama (with F1 tool definitions) → execute MCP tool calls → final natural language answer
- [x] Test query 1: *"Who won the 2024 Formula 1 championship?"* → should trigger `get_driver_standings(2024)`
- [x] Test query 2: *"What was the result of the Monaco GP in 2023?"* → should trigger `get_race_result(2023, 8)`
- [x] Test query 3: *"Which constructor won the most championships in the 2020s?"* → should trigger `get_constructor_standings`
- [x] Run with: `uv run python client/agent_client.py`
- [x] Commit

**Week 1 Milestone Check:**
- [x] `uv run mcp dev server/f1_server.py` opens Inspector and shows all 4 tools + 1 resource + 1 prompt
- [x] Chat agent correctly answers *"Who led the 2024 WDC?"* by calling `get_driver_standings`
- [x] Be able to explain Host vs Client vs Server using the F1 hub as an example

---

## Week 2 — Real-World Servers, HTTP Transport & Full Agent

### Day 8 — Race Analysis File Server: Persisting Race Intelligence

**Concept (~20 min):**
- [ ] How to safely expose file operations as MCP tools
- [ ] Importance of restricting access (security sandboxing)
- [ ] Why the agent needs a file server: persist race analysis, standings snapshots, notes

**Hands-on (~40 min):**
- [ ] Create `server/filesystem_server.py`
- [ ] Expose 4 tools (all paths restricted to `workspace/` folder only):
  - `read_file(path)` → read any text file in workspace
  - `write_file(path, content)` → write/overwrite a file
  - `list_directory(path)` → list files and folders
  - `search_files(pattern)` → glob search for files by name pattern
- [ ] Test with Inspector: `uv run mcp dev server/filesystem_server.py`
- [ ] In Inspector, call `write_file("race_notes.txt", "Bahrain 2024: Verstappen dominant")` and verify the file appears in `workspace/`
- [ ] Commit

---

### Day 9 — HTTP/SSE Transport: The F1 Server Goes Remote

**Concept (~20 min):**
- [ ] Why HTTP transport matters (remote servers, web apps, multiple clients)
- [ ] Difference: stdio (local subprocess) vs Streamable HTTP/SSE (networked)
- [ ] Real-world analogy: an F1 server could run on a home server, accessible from any device

**Hands-on (~40 min):**
- [ ] Copy and convert `f1_server.py` to SSE transport → `server/f1_server_sse.py`
  - Change transport from `stdio` to `sse`, bind to `localhost:8000`
- [ ] Create `client/f1_sse_client.py` that connects via `SseServerParameters` instead of `StdioServerParameters`
- [ ] Verify both transports return the same data for `get_driver_standings(2024)`
- [ ] Run server: `uv run python server/f1_server_sse.py`
- [ ] Run client: `uv run python client/f1_sse_client.py`
- [ ] Commit

---

### Day 10 — Multi-Server Client: F1 Data + File Storage Combined

**Concept (~20 min):**
- [ ] Real agents connect to **multiple** MCP servers simultaneously
- [ ] Client aggregates all tools from all servers into one unified tool list for the LLM

**Hands-on (~40 min):**
- [ ] Create `client/multi_server_client.py`
- [ ] Connect to `f1_server.py` (stdio) AND `filesystem_server.py` (stdio) simultaneously
- [ ] Aggregate tools from both, pass the combined list to Ollama
- [ ] Test query 1: *"Get the 2024 constructor standings and save them to workspace/constructors_2024.txt"*
  → should call `get_constructor_standings(2024)` then `write_file(...)`
- [ ] Test query 2: *"What files are currently saved in the workspace?"*
  → should call `list_directory(".")`
- [ ] Run with: `uv run python client/multi_server_client.py`
- [ ] Commit

---

### Day 11 — Live Timing Server: OpenF1 Real-Time Data

**Concept (~20 min):**
- [ ] How to wrap external APIs as async MCP tools
- [ ] Async tools in MCP with `async def` + `await`
- [ ] Explore the [OpenF1 API](https://openf1.org) — real session data including lap times, pit stops, telemetry, weather

**Hands-on (~40 min):**
- [ ] Create `server/f1_live_server.py` using `async def` tools throughout
- [ ] Expose 4 tools calling the OpenF1 API:
  - `get_latest_session(year: int, circuit_key: str)` → find a session key for a given GP
  - `get_lap_times(session_key: int, driver_number: int)` → lap-by-lap times for a driver
  - `get_pit_stops(session_key: int)` → all pit stop data for a race session
  - `get_race_control_messages(session_key: int)` → safety car, VSC, flag messages
- [ ] Test with Inspector: `uv run mcp dev server/f1_live_server.py`
- [ ] In Inspector, fetch lap times for a known session (e.g. 2024 Monaco GP) and verify real data returns
- [ ] Commit

---

### Day 12 — Error Handling, Logging, and Best Practices

**Concept (~20 min):**
- [ ] MCP error handling patterns (`isError: true`)
- [ ] Input validation and structured logging
- [ ] Writing good tool descriptions — they are injected directly into the LLM prompt, so clarity matters!

**Hands-on (~40 min):**
- [ ] Add input validation to all F1 servers:
  - `season` must be between 1950 and the current year
  - `round` must be ≥ 1 and ≤ 24
  - `driver_number` must be a valid positive integer
- [ ] Wrap all `httpx` calls in try/except — return `isError: true` with a clear message on API failure (e.g. network timeout, 404)
- [ ] Add Python `logging` module to all servers with INFO-level logs for each tool call and ERROR-level for failures
- [ ] Improve all tool `description=` strings to be specific, e.g.: *"Returns the Formula 1 World Drivers Championship standings for the given season year. Use this when asked about championship points, rankings, or who won a season."*
- [ ] Run all servers through Inspector to verify error responses display correctly
- [ ] Commit

---

### Day 13 — Capstone: F1 Race Intelligence Agent

**Concept (~20 min):**
- [ ] How to combine everything into one polished agent
- [ ] Multi-step tool chains and conversation memory (passing chat history back to the LLM)

**Hands-on (~40 min):**
- [ ] Create `agent/f1_assistant.py`
- [ ] Build a polished CLI chat agent that connects to ALL 3 servers simultaneously:
  - `f1_server.py` (historical standings & results)
  - `f1_live_server.py` (lap times, pit stops, race control)
  - `filesystem_server.py` (save analysis to `workspace/`)
- [ ] Features: conversation memory (pass full chat history each turn), multi-step tool chains
- [ ] Test scenario 1: *"Compare Verstappen and Norris's 2024 season points race by race and save the comparison to workspace/2024_title_fight.txt"*
- [ ] Test scenario 2: *"Who had the most pit stops in the 2024 Monaco GP? Save the pit stop data to workspace/monaco_2024_pitstops.txt"*
- [ ] Test scenario 3: *"Give me the last 5 winners of the British Grand Prix"*
- [ ] Run with: `uv run python agent/f1_assistant.py`
- [ ] Commit

**Week 2 Milestone Check:**
- [ ] Single agent uses tools from all 3 servers in one conversation
- [ ] *"Get 2024 standings and save to file"* works end-to-end in one natural language query
- [ ] All servers have proper error handling and logging
- [ ] The agent maintains context across multiple turns (follow-up questions work)

---

### Day 14 — Review, Document, and Next Steps

**Concept (~20 min):**
- [ ] Where MCP fits in the ecosystem (vs LangChain, OpenAI Assistants, etc.)
- [ ] Review all concepts learned
- [ ] Ideas for extending the F1 hub: driver head-to-head comparisons, season prediction, alert when qualifying starts

**Hands-on (~40 min):**
- [ ] Write proper `README.md` documenting:
  - The 3 servers and what each exposes
  - How to run each server and the full agent
  - Example queries supported by the agent
- [ ] Fill in `LEARNINGS.md` with key concepts explained in plain terms
- [ ] Tag the repo `v1.0`: `git tag v1.0 && git push --tags`
- [ ] Commit

---

## Repo Structure

```
mcp-server-client/
├── server/
│   ├── f1_server.py            (Days 4 & 5 — Jolpica API: standings, results, constructors)
│   ├── f1_server_sse.py        (Day 9  — same server, HTTP/SSE transport)
│   ├── f1_live_server.py       (Day 11 — OpenF1 API: lap times, pit stops, race control)
│   └── filesystem_server.py   (Day 8  — safe file read/write restricted to workspace/)
├── client/
│   ├── basic_client.py         (Day 6  — connect to f1_server, call tools directly)
│   ├── agent_client.py         (Day 7  — single-server LLM chat agent)
│   ├── f1_sse_client.py        (Day 9  — connects to f1_server_sse via HTTP)
│   └── multi_server_client.py  (Day 10 — f1_server + filesystem_server combined)
├── agent/
│   └── f1_assistant.py         (Day 13 — full agent: all 3 servers + conversation memory)
├── workspace/                   (sandbox: all agent-generated files saved here)
├── llm_intro.py                 (Day 1)
├── tool_calls.py                (Day 2)
├── day03_notes.md               (Day 3)
├── pyproject.toml               (uv manages this)
├── uv.lock                      (auto-generated lockfile)
├── .python-version              (pinned Python version)
├── PLAN.md                      ← CURRENT FILE
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

**MCP & Framework**
- [MCP Official Docs](https://modelcontextprotocol.io)
- [MCP Python SDK GitHub](https://github.com/modelcontextprotocol/python-sdk)
- [Ollama Docs](https://ollama.com)
- [Ollama Python Library](https://github.com/ollama/ollama-python)
- [uv Documentation](https://docs.astral.sh/uv/)

**F1 APIs (free, no key required)**
- [OpenF1 API](https://openf1.org) — real-time & historical telemetry, lap times, pit stops, weather
- [OpenF1 API Docs](https://openf1.org/#introduction) — swagger-style reference for all endpoints
- [Jolpica-F1 API](https://api.jolpi.ca/ergast/f1/) — community replacement for Ergast: standings, race results, constructors
- [Jolpica GitHub](https://github.com/jolpica/jolpica-f1) — source & docs
