"""CLI entry point for ignition-mcp-server."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Ignition MCP Server")
    parser.add_argument(
        "--transport", choices=["stdio", "sse"], default="stdio",
        help="MCP transport (default: stdio)",
    )
    parser.add_argument("--host", default="0.0.0.0", help="SSE host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="SSE port (default: 8080)")
    parser.add_argument(
        "--gateway-url",
        help="Ignition gateway URL for live tools (e.g. https://gateway:8088)",
    )
    parser.add_argument("--gateway-username", default="", help="Gateway auth username")
    parser.add_argument("--gateway-password", default="", help="Gateway auth password")
    parser.add_argument(
        "--enable-writes",
        action="store_true",
        help=(
            "Enable live write tools (write_tag, execute_script) against the gateway. "
            "Disabled by default — writes can actuate real equipment."
        ),
    )
    args = parser.parse_args()

    from ignition_mcp_server.server import configure_gateway, mcp

    if args.gateway_url:
        configure_gateway(
            args.gateway_url,
            args.gateway_username,
            args.gateway_password,
            enable_writes=args.enable_writes,
        )

    if args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
