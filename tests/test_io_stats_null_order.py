"""get_io_stats / get_per_backend_io_stats must not rank NULL-sum rows first.

In pg_stat_io (and pg_stat_get_backend_io) reads/writes/extends are NULL for
untracked combinations. `reads + writes + extends` is then NULL and
`ORDER BY ... DESC` puts NULL first, so LIMIT drops the rows with real I/O.
Offline: the query text is captured with a mocked execute_query.
"""
import asyncio
import re
from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import Client

from mcp_postgresql_ops import mcp_main
from mcp_postgresql_ops.version_compat import PostgreSQLVersion


def _captured_queries(tool, major, args=None):
    captured = []

    async def fake_execute_query(query, *a, **kw):
        captured.append(query)
        return []

    async def run():
        version = PostgreSQLVersion(major, 0, 0)
        with patch.object(mcp_main, "get_postgresql_version", new_callable=AsyncMock, return_value=version), \
                patch.object(mcp_main, "execute_query", side_effect=fake_execute_query):
            async with Client(mcp_main.mcp) as client:
                await client.call_tool(tool, args or {})

    asyncio.run(run())
    return captured


def _order_by(query):
    match = re.search(r"ORDER BY(.*?)LIMIT", query, re.IGNORECASE | re.DOTALL)
    assert match, query
    return match.group(1)


@pytest.mark.parametrize("major", [16, 17, 18])
def test_get_io_stats_order_by_coalesces_each_term(major):
    queries = _captured_queries("get_io_stats", major)
    order = _order_by(queries[0])
    for col in ("reads", "writes", "extends"):
        assert f"COALESCE({col}, 0)" in order
    assert "DESC" in order


def test_get_per_backend_io_stats_order_by_coalesces_each_term():
    queries = _captured_queries("get_per_backend_io_stats", 18)
    order = _order_by(queries[0])
    for col in ("bio.reads", "bio.writes"):
        assert f"COALESCE({col}, 0)" in order
