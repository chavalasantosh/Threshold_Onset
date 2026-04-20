"""Round-trip tests for threshold_onset.line_codec (stdlib only)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from threshold_onset.line_codec import decode, decode_document, encode


def test_roundtrip_flat_dict_sort_keys():
    d = {"event": "process_started", "trace_id": "abc", "n": 3}
    s = encode(d, sort_keys=True)
    assert "event:" in s
    out = decode_document(s)
    assert out == d


def test_roundtrip_tabular_rows():
    d = {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"},
        ]
    }
    s = encode(d)
    assert "{id,name,role}" in s
    out = decode_document(s)
    assert out == d


def test_roundtrip_nested():
    d = {"a": {"b": 2}, "c": [1, 2, True, None]}
    out = decode_document(encode(d, sort_keys=True))
    assert out == d


def test_decode_root_list():
    assert decode(encode([1, 2, 3])) == [1, 2, 3]
