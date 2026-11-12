"""Unit tests for millisecond time columns in format_table_data - no database required."""
from mcp_postgresql_ops.functions import format_table_data


def test_exec_time_is_milliseconds_single_row():
    out = format_table_data([{"total_exec_time": 1500.0}])
    assert out == "total_exec_time: 1.50s"


def test_exec_time_one_hour_in_ms():
    out = format_table_data([{"total_exec_time": 3600000.0}])
    assert out == "total_exec_time: 1.00h"


def test_exec_and_blk_time_are_milliseconds_multi_row():
    rows = [
        {"mean_exec_time": 250.0, "shared_blk_read_time": 90000.0},
        {"mean_exec_time": 500.0, "shared_blk_read_time": 1000.0},
    ]
    lines = format_table_data(rows).split("\n")
    assert lines[2] == "0.25s | 1.50m"
    assert lines[3] == "0.50s | 1.00s"


def test_generic_time_and_duration_still_seconds():
    out = format_table_data([{"some_duration": 90, "other_time": 90}])
    assert "some_duration: 1.50m" in out
    assert "other_time: 1.50m" in out
