# Changelog

## [0.4.0] - 2026-04-12

### Added
- **Cross-platform intelligence** — new [project-automate-bridge](https://github.com/nodeblue-ai/project-automate-bridge) package correlates Ignition OPC tags with Studio 5000 L5X PLC logic end-to-end.
- **OPC item path support** — `get_tags()` now includes `opcItemPath` and `opcServer` in tag summaries for OPC-sourced tags, enabling cross-platform correlation.
- 1 new test (72 total in test_server.py, 85 total with test_gateway.py).

## [0.3.1] - 2026-04-12

### Fixed
- **Structured error handling** — all tools now return `{"error": "..."}` JSON instead of throwing raw Python exceptions. Bad project paths, missing views, gateway connection failures all produce clean error messages for the AI agent.
- **ZipProjectSource file handle leak** — added `__del__`, `__enter__`/`__exit__` context manager support. Zip files are now properly closed.
- **Repeated project parsing** — `open_project()` is now LRU-cached (maxsize=16). Multiple tool calls against the same project reuse the parsed source instead of re-reading from disk/zip each time.

### Added
- **Multi-provider tag support** — `get_tags()` now accepts a `provider` parameter (default: `"default"`). Real Ignition projects can have multiple tag providers (e.g. `default`, `edge`, `MQTT`).
- **`list_tag_providers(project_path)`** — new tool to discover all tag provider names in a project.
- 13 new tests: cache behavior, context manager, multi-provider tags, structured error handling (71 total).

## [0.3.0] - 2026-04-12

### Added
- **Live gateway interaction** via Ignition WebDev module REST API
- **`read_tag`** — read current values of one or more tags from a live gateway (comma-separated for multiple)
- **`write_tag`** — write a value to a tag with automatic boolean/numeric coercion
- **`execute_script`** — execute Python scripts on the gateway in gateway scope
- **`get_history`** — query historical tag data with ISO 8601 time range
- **`GatewayClient`** — HTTP client module wrapping WebDev API endpoints with auth support
- CLI options: `--gateway-url`, `--gateway-username`, `--gateway-password`
- Gateway setup documentation with WebDev endpoint examples
- 13 new tests with mock HTTP server (58 total)

## [0.2.0] - 2026-04-12

### Added
- **`list_alarms` / `get_alarm`** — parse alarm pipeline configurations including stages, notification profiles, contact info, consolidation periods, and transitions
- **`list_named_queries` / `get_named_query`** — parse SQL named query definitions with parameters, database targets, query types (Query/Update), and descriptions
- Synthetic alarm pipeline fixtures (MainAlarmPipeline with 3-stage delay→email→escalation flow, EscalationPipeline disabled)
- Synthetic named query fixtures (GetActiveFaults, LogFault, GetMotorHistory with parameterized SQL)
- 14 new tests (45 total)

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
