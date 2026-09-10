"""Servidor MCP do Harness — interface do Operador."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from harness import Agent, Harness, Run

_harness = Harness()
mcp = FastMCP("harness")


def _run_payload(run: Run) -> dict[str, str]:
    payload = {
        "id": run.id,
        "workspace_path": str(run.workspace_path),
        "agent": run.agent.value,
        "status": run.status.value,
    }
    if run.proposed_message is not None:
        payload["proposed_message"] = run.proposed_message
    return payload


@mcp.tool()
def register_workspace(path: str) -> str:
    """Registra um Workspace local no Harness.

    Args:
        path: Caminho absoluto ou relativo de uma pasta local existente (repo git).
    """
    workspace = _harness.register_workspace(path)
    return str(workspace.path)


@mcp.tool()
def list_workspaces() -> list[str]:
    """Lista os Workspaces registrados no Harness."""
    return [str(w.path) for w in _harness.list_workspaces()]


@mcp.tool()
def set_denylist(patterns: list[str]) -> list[str]:
    """Define a Denylist do Harness (paths/padrões que o Committer nunca inclui).

    Args:
        patterns: Lista de padrões (ex.: [".env", "*.secret"]).
    """
    _harness.set_denylist(patterns)
    return _harness.list_denylist()


@mcp.tool()
def start_run(workspace_path: str, agent: str) -> dict[str, str]:
    """Dispara um Run de um Agent num Workspace registrado.

    Args:
        workspace_path: Path do Workspace registrado.
        agent: Nome do Agent (stub, coder, reviewer, committer).
    """
    run = _harness.start_run(workspace_path, Agent(agent))
    return _run_payload(run)


@mcp.tool()
def cancel_run(run_id: str) -> dict[str, str]:
    """Cancela um Run em andamento. Não altera o Workspace.

    Args:
        run_id: Identificador do Run.
    """
    return _run_payload(_harness.cancel_run(run_id))


@mcp.tool()
def reject_commit_message(run_id: str) -> dict[str, str]:
    """Rejeita a mensagem proposta pelo Committer; o mesmo Run propõe outra.

    Args:
        run_id: Identificador do Run do Committer.
    """
    return _run_payload(_harness.reject_commit_message(run_id))


@mcp.tool()
def confirm_commit(run_id: str) -> dict[str, str]:
    """Confirma a mensagem do Committer e cria o commit (sem push).

    Args:
        run_id: Identificador do Run do Committer.
    """
    return _run_payload(_harness.confirm_commit(run_id))


@mcp.tool()
def list_historico(workspace_path: str) -> list[dict[str, str]]:
    """Lista o Histórico de Runs de um Workspace.

    Args:
        workspace_path: Path do Workspace.
    """
    return [_run_payload(run) for run in _harness.list_historico(workspace_path)]


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
