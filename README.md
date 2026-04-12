# ignition-mcp-server

> The first AI-powered development tool for Ignition SCADA — an MCP server that lets any AI agent read and understand your Ignition projects.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/protocol-MCP-green.svg)](https://modelcontextprotocol.io/)

---

## What This Does

`ignition-mcp-server` connects AI agents (Claude, GPT, local LLMs) to your Ignition SCADA projects via the [Model Context Protocol](https://modelcontextprotocol.io/). It gives the AI structured access to:

- **Tags** — browse tag hierarchies, filter by folder path, see data types and values
- **Perspective Views** — read component trees, bindings, event handlers, and styles
- **Scripts** — read project library scripts and gateway event scripts with scope info
- **UDTs** — list and inspect User Defined Type definitions with member details

Works with both **Ignition 8.1+ project exports** (`.zip` files) and **8.3+ filesystem-based projects** (direct directory access).

## Why This Exists

Ignition has ~300,000+ installations worldwide and **zero AI tooling** — no vendor copilot, no third-party tools, no academic research. Every other major automation platform (Siemens, Rockwell, Schneider) has AI assistants. Ignition has nothing.

This server fills that gap. It's open-source, agent-agnostic, and works offline.

Part of [Project Automate](https://github.com/nodeblue-ai/project-automate) by [Nodeblue](https://www.nodeblue.ai).

---

## Installation

```bash
pip install ignition-mcp-server
```

Or install from source:

```bash
git clone https://github.com/nodeblue-ai/ignition-mcp-server.git
cd ignition-mcp-server
pip install .
```

Requires Python 3.10+.

---

## Quick Start

### stdio (local — kiro-cli, Claude Desktop, Claude Code)

```bash
ignition-mcp-server
```

### SSE (remote — server on one machine, agent on another)

```bash
ignition-mcp-server --transport sse --port 8080
```

---

## Configuration

### kiro-cli

Add to your `~/.kiro/settings.json`:

```json
{
  "mcpServers": {
    "ignition": {
      "command": "ignition-mcp-server",
      "args": []
    }
  }
}
```

### Claude Desktop

Add to your Claude Desktop MCP config:

```json
{
  "mcpServers": {
    "ignition": {
      "command": "ignition-mcp-server",
      "args": []
    }
  }
}
```

### SSE (remote)

Start the server on your engineering workstation:

```bash
ignition-mcp-server --transport sse --host 0.0.0.0 --port 8080
```

Connect from any MCP client using the SSE URL: `http://<host>:8080/sse`

---

## Available Tools

### `ping`
Health check. Returns `"pong"`.

### `get_tags(project_path, tag_path?)`
Browse tags in the project. Optionally filter by folder path.

```
get_tags("/path/to/project", "Conveyors/Line1")
```

Returns tag names, types, data types, values, and documentation.

### `list_views(project_path)`
List all Perspective view paths in the project.

### `get_view(project_path, view_path)`
Get a Perspective view's component tree with bindings and events.

```
get_view("/path/to/project", "Overview")
```

Returns component hierarchy, property bindings, and event handler counts.

### `list_scripts(project_path)`
List all scripts with their scope (gateway, client, all).

### `get_script(project_path, script_path)`
Get the source code of a project script.

```
get_script("/path/to/project", "ignition/script-python/utils")
```

### `list_udts(project_path)`
List all UDT (User Defined Type) definition names.

### `get_udt(project_path, udt_name?)`
Get UDT definition(s) with member details, parameters, and documentation.

```
get_udt("/path/to/project", "Motor_UDT")
```

---

## Supported Project Formats

| Format | How to Use |
|---|---|
| **Project directory** (8.1+ or 8.3+) | Point `project_path` to the project folder containing `project.json` |
| **Project export** (`.zip`) | Point `project_path` to the `.zip` file exported from Ignition Gateway or Designer |
| **8.3 filesystem** | Point to `data/projects/<ProjectName>/` on the Gateway |

---

## Example Conversation

```
You: What tags are under the Conveyors folder?

Agent calls: get_tags("/projects/MyPlant", "Conveyors")

Agent: The Conveyors folder contains 2 items:
- Line1 (Folder) — 3 child tags: Running (Boolean), Speed (Float4), Faulted (Boolean)
- Line2_Motor (UDT Instance) — type: Motor_UDT

You: What does the Motor_UDT look like?

Agent calls: get_udt("/projects/MyPlant", "Motor_UDT")

Agent: Motor_UDT has 3 members:
- Running (Boolean) — Motor running status
- Faulted (Boolean) — Motor fault status
- Speed_RPM (Float4) — Motor speed in RPM
Parameters: MotorName (String)

You: Show me the Overview view

Agent calls: get_view("/projects/MyPlant", "Overview")

Agent: The Overview view has a flex container with 3 children:
1. titleLabel (ia.display.label) — bound to view.params.title
2. speedDisplay (ia.display.led-display) — bound to tag [default]Conveyors/Line1/Speed
3. startButton (ia.input.button) — has 1 onClick event handler
```

---

## Roadmap

### v0.2 — Alarms & Named Queries
- [ ] `get_alarms(project_path)` — parse alarm pipeline configurations
- [ ] `get_named_queries(project_path)` — parse SQL named queries with parameters

### v0.3 — Live Gateway Interaction
- [ ] `read_tag(tag_path)` / `write_tag(tag_path, value)` — live tag interaction via Ignition WebDev module
- [ ] `execute_script(code)` — run scripts on the gateway
- [ ] `get_history(tag_path, start, end)` — query tag history

### v0.4 — Cross-Platform Intelligence
- [ ] Cross-reference Ignition tags with Studio 5000 L5X PLC logic
- [ ] "This alarm fires when tag X goes true — here's the PLC logic that drives X"
- [ ] Multi-project indexing for cross-site analysis

### Future
- [ ] RAG pipeline over Ignition documentation + project corpus
- [ ] Ignition script generation (gateway timer scripts, Perspective bindings)
- [ ] Perspective view scaffolding from natural language descriptions
- [ ] Local LLM support for air-gapped deployments

---

## Development

```bash
git clone https://github.com/nodeblue-ai/ignition-mcp-server.git
cd ignition-mcp-server
pip install -e .
pip install pytest
pytest tests/ -v
```

### Project Structure

```
src/ignition_mcp_server/
├── __init__.py
├── __main__.py          # CLI entry point (stdio/SSE)
├── server.py            # FastMCP server with all tool definitions
├── project_source.py    # Read from .zip or directory
└── parsers/
    ├── tags.py          # Tag hierarchy parser
    ├── views.py         # Perspective view parser
    ├── scripts.py       # Script discovery and reader
    └── udts.py          # UDT definition parser

tests/
├── test_server.py       # 31 tests covering all tools + both source types
└── fixtures/
    ├── sample-project/  # Synthetic Ignition project (directory)
    └── sample-project.zip  # Same project as .zip
```

---

## Contributing

Contributions welcome. This is an open-source project under MIT license.

If you have real Ignition project exports you can share (or anonymized versions), those are especially valuable for testing edge cases.

---

## License

[MIT](LICENSE)

---

<p align="center">
  <i>Built by <a href="https://www.nodeblue.ai">Nodeblue</a> — part of <a href="https://github.com/nodeblue-ai/project-automate">Project Automate</a></i>
</p>
