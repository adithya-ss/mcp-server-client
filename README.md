# MCP-SERVER-CLIENT
> Project to learn the concepts of Agentic AI and experiment with the development of a MCP Server and Client.

**What is an LLM?**
<br>An LLMs (Large Language Models) are programs which can recognize and generate texts, among other tasks. 

**What are Tokens?**
<br>Token in LLM are the fundamental and smallest units of a prompt. LLMs can tokenize the prompt into words, parts of words or even individual characters. Every prompt is converted into tokens, a response is generated first in the form of tokens and then sent back to the users in a readable text format.

**What is Tool Calling?**
<br>A pattern where the LLM outputs a structured JSON request to invoke a function, rather than answering directly. The calling application executes the function and feeds the result back to the LLM for a final response.

**What is MCP (Model Context Protocol)?**
<br>A standard protocol that lets an AI application discover and call tools exposed by separate server processes. Separates the LLM loop (Client) from the capability providers (Servers).

**MCP Roles**
- **Host** — the entry point that starts the session (e.g. the terminal or a chat UI)
- **Client** — manages the LLM conversation and routes tool calls to the correct server
- **Server** — a focused process that exposes tools, resources, and prompt templates

**Stdio Transport**
<br>The simplest MCP transport. The client spawns the server as a child process and communicates via stdin/stdout using JSON-RPC 2.0 messages.

**HTTP/SSE Transport**
<br>A networked MCP transport where the server runs as an HTTP server, allowing multiple clients to connect remotely.

---

