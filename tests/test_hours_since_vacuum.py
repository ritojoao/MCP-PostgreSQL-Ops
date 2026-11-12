"""Check hours_since_* queries use total epoch hours, not the hour component - no database required."""
import re
from pathlib import Path

import mcp_postgresql_ops.mcp_main as mcp_main

SRC = Path(mcp_main.__file__).read_text(encoding="utf-8")


def test_no_extract_hours_from_interval():
    assert not re.search(r"extract\(\s*hours?\s+from", SRC, re.IGNORECASE)


def test_epoch_based_hours_used():
    assert re.search(r"floor\(extract\(epoch from now\(\) - .+?\)/3600\)::int", SRC, re.IGNORECASE)
