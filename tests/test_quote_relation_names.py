"""Unit tests: relation names built in SQL must be quoted — no database required."""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "mcp_postgresql_ops"

# schema||'.'||name passed to a size function or a regclass cast, without quote_ident
SIZE_CALL = re.compile(
    r"pg_(?:total_relation_size|relation_size|indexes_size|table_size)\(\s*(?!quote_ident)[\w.]+\s*\|\|\s*'\.'\s*\|\|",
    re.IGNORECASE,
)
REGCLASS_CAST = re.compile(r"\(\s*(?!quote_ident)[\w.]+\s*\|\|\s*'\.'\s*\|\|[^)]*\)\s*::\s*regclass", re.IGNORECASE)


def _sources():
    for name in ("mcp_main.py", "functions.py"):
        yield name, (SRC / name).read_text(encoding="utf-8")


def test_no_unquoted_name_in_size_functions():
    offenders = [(n, m.group(0)) for n, t in _sources() for m in SIZE_CALL.finditer(t)]
    assert not offenders, offenders


def test_no_unquoted_name_in_regclass_cast():
    offenders = [(n, m.group(0)) for n, t in _sources() for m in REGCLASS_CAST.finditer(t)]
    assert not offenders, offenders


def test_patterns_detect_the_old_code():
    assert SIZE_CALL.search("pg_total_relation_size(schemaname||'.'||tablename)")
    assert SIZE_CALL.search("pg_relation_size(schemaname || '.' || relname)")
    assert REGCLASS_CAST.search("(pt.schemaname||'.'||pt.tablename)::regclass")
    assert not SIZE_CALL.search("pg_total_relation_size(quote_ident(schemaname)||'.'||quote_ident(tablename))")
