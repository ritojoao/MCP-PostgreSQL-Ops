"""Unit tests for get_per_backend_io_stats WAL query on PG 18 (no database required)."""
from unittest.mock import AsyncMock, patch

import pytest

from mcp_postgresql_ops import mcp_main
from mcp_postgresql_ops.version_compat import PostgreSQLVersion

# Removed from pg_stat_wal and pg_stat_get_backend_wal() in PG 18
# (WAL write/sync stats moved to pg_stat_io with object = 'wal').
REMOVED_PG18_WAL_COLUMNS = ["wal_write", "wal_sync", "wal_write_time", "wal_sync_time"]


def _tool_fn():
    tool = mcp_main.get_per_backend_io_stats
    return getattr(tool, "fn", tool)


@pytest.mark.asyncio
async def test_backend_wal_query_uses_only_pg18_columns():
    queries = []

    async def fake_execute(query, *args, **kwargs):
        queries.append(query)
        return []

    with patch.object(mcp_main, "get_postgresql_version", new_callable=AsyncMock,
                      return_value=PostgreSQLVersion(18, 0, 0)), \
         patch.object(mcp_main, "execute_query", side_effect=fake_execute):
        await _tool_fn()(limit=5)

    wal_queries = [q for q in queries if "pg_stat_get_backend_wal" in q]
    assert len(wal_queries) == 1
    for col in REMOVED_PG18_WAL_COLUMNS:
        assert f"bwal.{col}" not in wal_queries[0]
    for col in ["wal_records", "wal_fpi", "wal_bytes", "wal_buffers_full"]:
        assert f"bwal.{col}" in wal_queries[0]
