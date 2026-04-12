# Changelog

## [0.1.0] - 2026-04-12

### Added
- Initial release of ignition-mcp-server
- **Project source abstraction** — read Ignition projects from `.zip` exports or filesystem directories (8.1+ and 8.3+)
- **`get_tags`** — browse tag hierarchies with folder path filtering
- **`list_views` / `get_view`** — list and inspect Perspective views with component trees, bindings, and events
- **`list_scripts` / `get_script`** — discover and read project library and gateway event scripts
- **`list_udts` / `get_udt`** — list and inspect UDT definitions with member details
- **`ping`** — health check tool
- **stdio and SSE transport** — works with kiro-cli, Claude Desktop, Claude Code, and remote MCP clients
- **CLI entry point** — `ignition-mcp-server` command with `--transport`, `--host`, `--port` options
- Synthetic test fixtures with 31 passing tests
- MIT license
