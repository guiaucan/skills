"""Servidor MCP do Harness — interface do Operador."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from harness import Harness

_harness = Harness()
mcp = FastMCP("harness")


@mcp.tool()
def register_workspace(path: str) -> str:
    """Registra um Workspace local no Harness.

    Args:
        path: Caminho absoluto ou relativo de uma pasta local existente.
    """
    workspace = _harness.register_workspace(path)
    return str(workspace.path)


@mcp.tool()
def list_workspaces() -> list[str]:
    """Lista os Workspaces registrados no Harness."""
    return [str(w.path) for w in _harness.list_workspaces()]


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
