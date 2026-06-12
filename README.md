# ignition-mcp-server

> The first AI-powered development tool for Ignition SCADA — an MCP server that lets any AI agent read, understand, and interact with your Ignition projects and gateways.

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
- **Alarm Pipelines** — read alarm notification configurations with stages, profiles, and transitions
- **Named Queries** — read SQL query definitions with parameters, database targets, and types
- **Live Tag Read/Write** — read and write tag values on a running Ignition gateway via WebDev
- **Script Execution** — run Python scripts on the gateway in gateway scope
- **Tag History** — query historical tag data with time range filtering

Works with both **Ignition 8.1+ project exports** (`.zip` files) and **8.3+ filesystem-based projects** (direct directory access).

## Why This Exists

Ignition has ~300,000+ installations worldwide and **zero AI tooling** — no vendor copilot, no third-party tools, no academic research. Every other major automation platform (Siemens, Rockwell, Schneider) has AI assistants. Ignition has nothing.

This server fills that gap. It's open-source, agent-agnostic, and works offline.

Part of [Project Automate](https://github.com/md-automation/project-automate) by [Nodeblue](https://www.nodeblue.ai).

---

## Installation

Install from source:

```bash
git clone https://github.com/nodeblue-ai/ignition-mcp-server.git
cd ignition-mcp-server
pip install .
```

Requires Python 3.10+.

> **Note:** `pip install ignition-mcp-server` from PyPI is coming soon. For now, install from source as shown above.

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

### With live gateway connection

```bash
ignition-mcp-server --gateway-url https://my-gateway:8088 --gateway-username admin --gateway-password changeme
```

This enables the `read_tag`, `write_tag`, `execute_script`, and `get_history` tools. Requires the [WebDev module](https://docs.inductiveautomation.com/docs/8.1/appendix/modules/web-dev-module) on the gateway with API endpoints configured (see [Gateway Setup](#gateway-setup) below).

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

With live gateway access:

```json
{
  "mcpServers": {
    "ignition": {
      "command": "ignition-mcp-server",
      "args": ["--gateway-url", "https://my-gateway:8088"]
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

### `get_tags(project_path, tag_path?, provider?)`
Browse tags in the project. Optionally filter by folder path and tag provider.

```
get_tags("/path/to/project", "Conveyors/Line1")
get_tags("/path/to/project", "", "edge")
```

Returns tag names, types, data types, values, and documentation.

### `list_tag_providers(project_path)`
List all tag provider names in the project (e.g. `default`, `edge`, `MQTT`).

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

### `list_alarms(project_path)`
List all alarm pipeline names in the project.

### `get_alarm(project_path, pipeline_name)`
Get an alarm pipeline's configuration including stages, notification profiles, and transitions.

```
get_alarm("/path/to/project", "MainAlarmPipeline")
```

Returns pipeline stages with type (delay, notification), notification profile names, contact info, consolidation periods, and transition counts.

### `list_named_queries(project_path)`
List all named query names in the project.

### `get_named_query(project_path, query_name)`
Get a named query's SQL, parameters, database connection, and type (Query vs Update).

```
get_named_query("/path/to/project", "GetActiveFaults")
```

Returns the SQL text, parameter definitions with data types and defaults, target database, and description.

### `read_tag(tag_path)`
Read the current value of one or more tags from a live gateway. Comma-separate for multiple tags.

```
read_tag("[default]Conveyors/Line1/Speed")
read_tag("[default]Conveyors/Line1/Speed, [default]Conveyors/Line1/Running")
```

Requires `--gateway-url` at startup.

### `write_tag(tag_path, value)`
Write a value to a tag on a live gateway. Handles boolean/numeric coercion automatically.

```
write_tag("[default]Conveyors/Line1/Speed", "1800")
```

Requires `--gateway-url` at startup.

### `execute_script(code)`
Execute a Python script on the Ignition gateway in gateway scope.

```
execute_script("system.tag.readBlocking(['[default]Conveyors/Line1/Speed'])")
```

Requires `--gateway-url` at startup.

### `get_history(tag_path, start, end)`
Query historical tag data from the gateway's historian.

```
get_history("[default]Conveyors/Line1/Speed", "2026-04-12T00:00:00Z", "2026-04-12T12:00:00Z")
```

Requires `--gateway-url` at startup.

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

## Gateway Setup

The live tools (`read_tag`, `write_tag`, `execute_script`, `get_history`) require the [WebDev module](https://docs.inductiveautomation.com/docs/8.1/appendix/modules/web-dev-module) on your Ignition gateway with the following REST endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/system/webdev/api/tags/read` | POST | Read tag values |
| `/system/webdev/api/tags/write` | POST | Write tag values |
| `/system/webdev/api/script/run` | POST | Execute gateway scripts |
| `/system/webdev/api/history/query` | POST | Query tag history |

Example WebDev Python resource for `/api/tags/read`:

```python
def doPost(request, session):
    import json
    body = json.loads(request["data"])
    paths = body.get("tagPaths", [])
    values = system.tag.readBlocking(paths)
    return {
        "json": [
            {"path": str(v.path), "value": v.value, "quality": str(v.quality)}
            for v in values
        ]
    }
```

See the [Ignition WebDev docs](https://docs.inductiveautomation.com/docs/8.1/appendix/modules/web-dev-module) for full setup instructions.

---

## Roadmap

### v0.2 — Alarms & Named Queries ✅
- [x] `list_alarms` / `get_alarm` — parse alarm pipeline configurations
- [x] `list_named_queries` / `get_named_query` — parse SQL named queries with parameters

### v0.3 — Live Gateway Interaction ✅
- [x] `read_tag(tag_path)` / `write_tag(tag_path, value)` — live tag interaction via Ignition WebDev module
- [x] `execute_script(code)` — run scripts on the gateway
- [x] `get_history(tag_path, start, end)` — query tag history

### v0.4 — Cross-Platform Intelligence ✅
- [x] Cross-reference Ignition tags with Studio 5000 L5X PLC logic via [bridge-mcp-server](https://github.com/nodeblue-ai/bridge-mcp-server)
- [x] "This alarm fires when tag X goes true — here's the PLC logic that drives X"
- [x] OPC item path extraction (`opcItemPath`, `opcServer`) in tag summaries

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
├── __main__.py          # CLI entry point (stdio/SSE, gateway config)
├── server.py            # FastMCP server with all 17 tool definitions
├── project_source.py    # Read from .zip or directory (LRU-cached)
├── gateway_client.py    # HTTP client for live Ignition WebDev API
└── parsers/
    ├── tags.py          # Tag hierarchy parser (multi-provider)
    ├── views.py         # Perspective view parser
    ├── scripts.py       # Script discovery and reader
    ├── udts.py          # UDT definition parser
    ├── alarms.py        # Alarm pipeline parser
    └── named_queries.py # Named query parser

tests/
├── test_server.py       # 59 tests — parsers, project sources, error handling
├── test_gateway.py      # 13 tests — live gateway tools with mock HTTP server
└── fixtures/
    ├── sample-project/  # Synthetic Ignition project (directory)
    └── sample-project.zip
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
  <i>Built by <a href="https://www.nodeblue.ai">Nodeblue</a> — Engineering-driven technology across software, industrial automation, and applied research.</i>
</p>
