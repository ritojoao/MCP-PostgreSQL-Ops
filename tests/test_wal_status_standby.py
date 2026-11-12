"""get_wal_status must work on a standby (pg_current_wal_lsn() errors during recovery).

Set MCP_TEST_STANDBY_PORT (and optionally MCP_TEST_PRIMARY_PORT) to a reachable
streaming standby / primary. Connection user, password and host come from the usual
POSTGRES_* environment variables. Skipped when the variable is not set.
"""
import os

import pytest

import mcp_postgresql_ops.functions as _functions
import mcp_postgresql_ops.mcp_main as _mcp_main

get_wal_status = getattr(_mcp_main.get_wal_status, "fn", _mcp_main.get_wal_status)


def _use_port(monkeypatch, env_name):
    port = os.environ.get(env_name)
    if not port:
        pytest.skip(f"{env_name} not set")
    monkeypatch.setitem(_functions.POSTGRES_CONFIG, "port", int(port))


async def test_get_wal_status_on_standby(monkeypatch):
    _use_port(monkeypatch, "MCP_TEST_STANDBY_PORT")
    result = await get_wal_status()
    assert "Error retrieving" not in result, result
    assert "Recovery (Standby)" in result


async def test_get_wal_status_on_primary(monkeypatch):
    _use_port(monkeypatch, "MCP_TEST_PRIMARY_PORT")
    result = await get_wal_status()
    assert "Error retrieving" not in result, result
    assert "Primary" in result
