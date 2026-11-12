"""Unit test for get_wal_status standby handling (no database required)."""
import re
from unittest.mock import patch

from mcp_postgresql_ops import mcp_main


def _tool_fn():
    tool = mcp_main.get_wal_status
    return getattr(tool, "fn", tool)


async def test_wal_status_query_handles_standby_and_primary():
    queries = []

    async def fake_execute(query, *args, **kwargs):
        queries.append(query)
        return []

    with patch.object(mcp_main, "execute_query", side_effect=fake_execute):
        await _tool_fn()()

    lsn_queries = [q for q in queries if "pg_current_wal_lsn" in q or "pg_last_wal_replay_lsn" in q]
    assert len(lsn_queries) == 1
    sql = re.sub(r"--[^\n]*", "", lsn_queries[0])  # drop SQL comments
    # Replay LSN on a standby, current LSN on a primary, chosen via pg_is_in_recovery()
    case = re.compile(
        r"CASE WHEN pg_is_in_recovery\(\) THEN pg_last_wal_replay_lsn\(\) "
        r"ELSE pg_current_wal_lsn\(\) END",
        re.IGNORECASE,
    )
    assert case.search(sql)
    # No unguarded pg_current_wal_lsn() call (it errors during recovery)
    assert len(re.findall(r"pg_current_wal_lsn\(\)", sql)) == len(case.findall(sql))
