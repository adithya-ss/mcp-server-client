# What is MCP? The Big Picture


### The 3 Roles in MCP

| Role | Who | Responsibility |
|------|-----|----------------|
| **Host** | The end user / application shell | Initiates the session, owns the LLM conversation, decides what servers to connect to |
| **Client** | The code that wraps the LLM loop | Connects to one or more MCP Servers, discovers their tools/resources, forwards LLM tool-call requests to the right server, and returns results |
| **Server** | A focused capability provider | Exposes a fixed set of tools, resources, and prompt templates over a standard protocol; has no knowledge of the LLM or the user |

**Key insight:** The Server never talks to the LLM. The Client is the bridge. The Host is just the entry point that starts it all.

---

### ASCII Architecture — F1 Race Intelligence Hub

```
┌─────────────────────────────────────────────────────────────────────┐
│  HOST  (the user running the terminal / VS Code)                    │
│                                                                     │
│   $ uv run python agent/f1_assistant.py                             │
│   > "Who led the 2024 WDC after the Italian GP?"                    │
└────────────────────────┬────────────────────────────────────────────┘
                         │  user input
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  CLIENT  —  agent/f1_assistant.py                                   │
│                                                                     │
│  1. Collects all tool definitions from every connected server       │
│  2. Sends user query + tool list to Ollama (local LLM)              │
│  3. Receives tool-call response from LLM                            │
│  4. Routes the call to the correct MCP Server                       │
│  5. Returns the tool result back to the LLM for a final answer      │
│  6. Maintains conversation history across turns                     │
└──────┬────────────────────┬──────────────────────┬──────────────────┘
       │ stdio              │ stdio                │ stdio
       ▼                    ▼                      ▼
┌──────────────┐   ┌────────────────────┐   ┌─────────────────────┐
│   SERVER 1   │   │      SERVER 2      │   │      SERVER 3       │
│ f1_server.py │   │ f1_live_server.py  │   │ filesystem_server   │
│              │   │                    │   │       .py           │
│ Tools:       │   │ Tools:             │   │ Tools:              │
│ • get_driver │   │ • get_latest_      │   │ • read_file()       │
│   _standings │   │   session()        │   │ • write_file()      │
│ • get_race_  │   │ • get_lap_times()  │   │ • list_directory()  │
│   schedule   │   │ • get_pit_stops()  │   │ • search_files()    │
│ • get_race_  │   │ • get_race_        │   │                     │
│   result     │   │   control_         │   │ Restricted to:      │
│ • get_       │   │   messages()       │   │   workspace/        │
│   constructor│   │                    │   │                     │
│   _standings │   │ Resource:          │   │                     │
│              │   │   OpenF1 API       │   │                     │
│ Resource:    │   │   (real-time)      │   │                     │
│ f1://drivers │   │                    │   │                     │
│   /current   │   │                    │   │                     │
│              │   │                    │   │                     │
│ Prompt:      │   │                    │   │                     │
│ analyze-     │   │                    │   │                     │
│   driver     │   │                    │   │                     │
└──────┬───────┘   └──────────┬─────────┘   └──────────┬──────────┘
       │                      │                         │
       ▼                      ▼                         ▼
 Jolpica-F1 API         OpenF1 API               workspace/
 (historical data,      (session telemetry,       (local files:
  no key needed)         no key needed)            .txt, .json)
```

---

### Each Part's Role — Explained in F1 Terms

### Host
The Host is the entry point — the person sitting at the terminal running `uv run python agent/f1_assistant.py` and typing queries like *"Who won the 2024 Monaco GP?"*. In a real product, the Host could be a chat UI, a VS Code extension, or Claude Desktop. The Host owns the session but delegates all intelligence to the Client.

### Client
The Client (`f1_assistant.py`) is the brain of the operation. It:
- Connects to all three servers at startup and collects every available tool
- Packs those tool definitions into the Ollama API request so the LLM knows what it can call
- Receives the LLM's decision ("call `get_race_result(2024, 8)` on `f1_server`")
- Executes that tool call against the correct server via the MCP protocol
- Feeds the result back into the conversation so the LLM can form a natural language answer

The Client never hard-codes any F1 logic — it only orchestrates.

### Server
Each Server is a narrow, focused capability provider:

- **`f1_server.py`** — wraps the Jolpica-F1 REST API. Knows everything about historical seasons: standings, schedules, and race results. Stateless — each tool call is independent.
- **`f1_live_server.py`** — wraps the OpenF1 REST API. Provides session-level telemetry: lap times, pit stop windows, race control messages (safety car, VSC, flags).
- **`filesystem_server.py`** — provides sandboxed file I/O. Allows the agent to persist analysis, save standings snapshots, and read back previously stored notes. Access is strictly restricted to the `workspace/` folder.

No server knows about Ollama, the user, or other servers. They simply expose tools and wait to be called.

---

### 3 Real F1 Use Cases for This Hub

**Use case 1 — Championship tracker**
> *"Who is leading the 2026 Formula 1 Drivers Championship and by how many points over second place?"*

The Client calls `get_driver_standings(2026)` on `f1_server`, retrieves live standings from Jolpica, and the LLM formats a clean summary.

---

**Use case 2 — Race deep-dive with file save**
> *"Get the full lap-time breakdown for Verstappen in the 2024 Monaco GP, identify the fastest lap, and save the analysis to workspace/monaco_verstappen.txt"*

The Client:
1. Calls `get_latest_session(2024, "monaco")` on `f1_live_server` to get the session key
2. Calls `get_lap_times(session_key, 1)` to retrieve all 78 laps
3. Calls `write_file("monaco_verstappen.txt", ...)` on `filesystem_server` to persist the result

---

**Use case 3 — Historical pattern query**
> *"List every British Grand Prix winner since 2010 and highlight any driver who won it more than once"*

The Client loops `get_race_result(season, round)` for the relevant rounds across seasons 2010–2025 on `f1_server`, collects all results, and the LLM identifies the repeat winners.
