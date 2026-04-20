"""
Serialize and parse nested mappings and sequences into a compact line-oriented text form.

Indentation uses two spaces per level. Arrays declare a length in brackets; when every
element is a mapping with the same keys and only leaf values, a header line lists field
names and following lines hold comma-separated cells. Otherwise list entries use a leading
hyphen. Intended for logs, health checks, and saved reports.

Stdlib only; no extra packages.
"""

from __future__ import annotations

import math
import re 
from typing import Any, Dict, List, Optional, Tuple, Union

JsonValue = Union[None, bool, int, float, str, Dict[str, Any], List[Any]]

INDENT_UNIT = "  "


def _canonical_float(x: float) -> str:
    if math.isnan(x) or math.isinf(x):
        return "null"
    if x == 0.0:
        return "0"
    if abs(x - round(x)) < 1e-15 and abs(x) < 1e15:
        return str(int(round(x)))
    s = ("%.15f" % x).rstrip("0").rstrip(".")
    if s == "-0":
        return "0"
    return s


def _encode_primitive(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return _canonical_float(value)
    if isinstance(value, str):
        return _quote_string(value)
    raise TypeError(f"Not JSON-encodable: {type(value)!r}")


def _quote_string(s: str) -> str:
    if s == "":
        return '""'
    needs = (
        '"' in s
        or "\\" in s
        or "\n" in s
        or "\r" in s
        or "\t" in s
        or "," in s
        or ":" in s
        or s != s.strip()
        or (s and s[0] in "0123456789+-")
        or s in ("null", "true", "false")
    )
    if not needs and re.match(r"^[A-Za-z_][A-Za-z0-9_.]*$", s):
        return s
    out = []
    for ch in s:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def _encode_key(k: str) -> str:
    if re.match(r"^[A-Za-z_][A-Za-z0-9_.]*$", k) and k not in ("null", "true", "false"):
        return k
    return _quote_string(k)


def _uniform_tabular_fields(rows: List[dict]) -> Optional[List[str]]:
    if not rows:
        return []
    keys0 = list(rows[0].keys())
    for row in rows:
        if not isinstance(row, dict) or list(row.keys()) != keys0:
            return None
        for v in row.values():
            if isinstance(v, (dict, list)):
                return None
    return keys0


def _is_primitive_json(x: Any) -> bool:
    if x is None:
        return True
    if isinstance(x, bool):
        return True
    if isinstance(x, (int, float, str)):
        return True
    return False


def _emit_dict(obj: Dict[str, Any], depth: int, sort_keys: bool) -> List[str]:
    keys = sorted(obj.keys(), key=lambda x: str(x)) if sort_keys else list(obj.keys())
    lines: List[str] = []
    indent = INDENT_UNIT * depth
    for k in keys:
        v = obj[k]
        ek = _encode_key(str(k))
        if isinstance(v, dict):
            lines.append(f"{indent}{ek}:")
            lines.extend(_emit_dict(v, depth + 1, sort_keys))
        elif isinstance(v, list):
            lines.extend(_emit_array(ek, v, depth, sort_keys))
        else:
            lines.append(f"{indent}{ek}: {_encode_primitive(v)}")
    return lines


def _emit_array(name: str, items: List[Any], depth: int, sort_keys: bool) -> List[str]:
    indent = INDENT_UNIT * depth
    n = len(items)
    prefix = name
    if n == 0:
        return [f"{indent}{prefix}[0]:"]

    if all(_is_primitive_json(x) for x in items):
        body = ",".join(_encode_primitive(x) for x in items)
        return [f"{indent}{prefix}[{n}]: {body}"]

    if all(isinstance(x, dict) for x in items):
        rows = [x for x in items if isinstance(x, dict)]
        fields = _uniform_tabular_fields(rows)
        if fields is not None:
            hdr = f"{indent}{prefix}[{n}]{{{','.join(fields)}}}:"
            out = [hdr]
            row_indent = INDENT_UNIT * (depth + 1)
            for row in rows:
                cells = [_encode_primitive(row[f]) for f in fields]
                out.append(row_indent + ",".join(cells))
            return out

    out = [f"{indent}{prefix}[{n}]:"]
    child = depth + 1
    for el in items:
        out.extend(_emit_list_item(el, child, sort_keys))
    return out


def _emit_list_item(el: Any, depth: int, sort_keys: bool) -> List[str]:
    indent = INDENT_UNIT * depth
    if isinstance(el, bool):
        return [f"{indent}- {_encode_primitive(el)}"]
    if el is None or isinstance(el, (int, float, str)):
        return [f"{indent}- {_encode_primitive(el)}"]
    if isinstance(el, list):
        n = len(el)
        if n == 0:
            return [f"{indent}- [0]:"]
        if all(_is_primitive_json(x) for x in el):
            body = ",".join(_encode_primitive(x) for x in el)
            return [f"{indent}- [{n}]: {body}"]
        lines = [f"{indent}- [{n}]:"]
        for sub in el:
            lines.extend(_emit_list_item(sub, depth + 1, sort_keys))
        return lines
    if isinstance(el, dict):
        return _emit_list_item_dict(el, depth, sort_keys)
    raise TypeError(f"Unsupported list item: {type(el)!r}")


def _emit_list_item_dict(obj: Dict[str, Any], depth: int, sort_keys: bool) -> List[str]:
    indent = INDENT_UNIT * depth
    keys = sorted(obj.keys(), key=lambda x: str(x)) if sort_keys else list(obj.keys())
    if not keys:
        return [f"{indent}-"]
    k0 = keys[0]
    v0 = obj[k0]
    ek0 = _encode_key(str(k0))
    lines: List[str] = []
    if isinstance(v0, dict):
        lines.append(f"{indent}- {ek0}:")
        lines.extend(_emit_dict(v0, depth + 1, sort_keys))
    elif isinstance(v0, list):
        n = len(v0)
        if n == 0:
            lines.append(f"{indent}- {ek0}[0]:")
        elif all(_is_primitive_json(x) for x in v0):
            body = ",".join(_encode_primitive(x) for x in v0)
            lines.append(f"{indent}- {ek0}[{n}]: {body}")
        else:
            lines.append(f"{indent}- {ek0}[{n}]:")
            for sub in v0:
                lines.extend(_emit_list_item(sub, depth + 2, sort_keys))
    else:
        lines.append(f"{indent}- {ek0}: {_encode_primitive(v0)}")
    cont = depth + 1
    for k in keys[1:]:
        vk = obj[k]
        ek = _encode_key(str(k))
        if isinstance(vk, dict):
            lines.append(f"{INDENT_UNIT * cont}{ek}:")
            lines.extend(_emit_dict(vk, cont + 1, sort_keys))
        elif isinstance(vk, list):
            lines.extend(_emit_array(ek, vk, cont, sort_keys))
        else:
            lines.append(f"{INDENT_UNIT * cont}{ek}: {_encode_primitive(vk)}")
    return lines


def encode(obj: Any, *, sort_keys: bool = False) -> str:
    """Serialize a JSON-compatible value to text (UTF-8, lines separated by newline)."""
    if isinstance(obj, dict):
        lines = _emit_dict(obj, 0, sort_keys)
    elif isinstance(obj, list):
        lines = _emit_array("", obj, 0, sort_keys)
    else:
        lines = [_encode_primitive(obj)]
    text = "\n".join(lines)
    return text + ("\n" if text else "")


def _leading_depth(line: str) -> Tuple[int, str]:
    n = 0
    i = 0
    while i < len(line) and line[i] == " ":
        n += 1
        i += 1
    if n % 2 != 0:
        raise ValueError("Invalid indentation (must be a multiple of 2 spaces)")
    return n // 2, line[i:]


def _parse_scalar(token: str) -> Any:
    t = token.strip()
    if not t:
        return ""
    if t == "null":
        return None
    if t == "true":
        return True
    if t == "false":
        return False
    if t[0] == '"':
        if len(t) < 2 or t[-1] != '"':
            raise ValueError(f"Bad string token: {token!r}")
        inner = t[1:-1]
        return (
            inner.replace("\\\\", "\\")
            .replace('\\"', '"')
            .replace("\\n", "\n")
            .replace("\\r", "\r")
            .replace("\\t", "\t")
        )
    if re.match(r"^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?$", t):
        if "." in t or "e" in t.lower():
            return float(t)
        try:
            return int(t)
        except ValueError:
            return float(t)
    return t


def _split_csv_row(line: str) -> List[str]:
    out: List[str] = []
    i = 0
    cur: List[str] = []
    while i < len(line):
        c = line[i]
        if c == '"':
            cur.append(c)
            i += 1
            while i < len(line):
                if line[i] == "\\" and i + 1 < len(line):
                    cur.append(line[i])
                    cur.append(line[i + 1])
                    i += 2
                    continue
                cur.append(line[i])
                if line[i] == '"':
                    i += 1
                    break
                i += 1
            continue
        if c == ",":
            out.append("".join(cur).strip())
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    out.append("".join(cur).strip())
    return out


def _parse_tabular_array(
    lines: List[Tuple[int, str]], pos: int, depth: int, name: str, n_expect: int, fields: List[str]
) -> Tuple[List[Dict[str, Any]], int]:
    rows: List[Dict[str, Any]] = []
    pos += 1
    for _ in range(n_expect):
        if pos >= len(lines):
            break
        d, row_line = lines[pos]
        if d != depth + 1 or row_line.startswith("- "):
            break
        cells = _split_csv_row(row_line)
        row: Dict[str, Any] = {}
        for i, f in enumerate(fields):
            row[f] = _parse_scalar(cells[i]) if i < len(cells) else None
        rows.append(row)
        pos += 1
    return rows, pos


def _parse_list_items(lines: List[Tuple[int, str]], pos: int, item_depth: int) -> Tuple[List[Any], int]:
    items: List[Any] = []
    while pos < len(lines):
        d, txt = lines[pos]
        if d < item_depth:
            break
        if d == item_depth:
            if not txt.startswith("- "):
                break
            item, pos = _parse_list_item_line(lines, pos, item_depth)
            items.append(item)
        else:
            break
    return items, pos


def _parse_list_item_line(lines: List[Tuple[int, str]], pos: int, item_depth: int) -> Tuple[Any, int]:
    d, txt = lines[pos]
    if d != item_depth or not txt.startswith("- "):
        raise ValueError("Expected list item")
    rest = txt[2:].strip()
    if not rest:
        pos += 1
        nested, pos = _parse_object(lines, pos, item_depth + 1)
        return nested, pos
    if ":" not in rest:
        return _parse_scalar(rest), pos + 1

    key_part, after = rest.split(":", 1)
    key_part = key_part.strip()
    after = after.strip()

    m_anon = re.match(r"^\[(\d+)\]$", key_part)
    if m_anon:
        if after:
            parts = _split_csv_row(after) if ("," in after or '"' in after) else [p.strip() for p in after.split(",")]
            arr = [_parse_scalar(p) for p in parts]
            return arr, pos + 1
        pos += 1
        return _parse_list_items(lines, pos, item_depth + 1)

    m_named = re.match(r"^([^[]+)\[(\d+)\]$", key_part)
    if m_named and after:
        parts = _split_csv_row(after) if ("," in after or '"' in after) else [p.strip() for p in after.split(",")]
        return {m_named.group(1): [_parse_scalar(p) for p in parts]}, pos + 1

    if m_named and not after:
        n_expect = int(m_named.group(2))
        name = m_named.group(1)
        pos += 1
        sub_items, pos = _parse_list_items(lines, pos, item_depth + 1)
        return {name: sub_items}, pos

    k = key_part
    if not after:
        pos += 1
        nested, pos = _parse_object(lines, pos, item_depth + 1)
        return {k: nested}, pos

    val = _parse_scalar(after)
    pos += 1
    obj: Dict[str, Any] = {k: val}
    while pos < len(lines):
        d2, t2 = lines[pos]
        if d2 <= item_depth:
            break
        if d2 == item_depth + 1 and not t2.startswith("- "):
            if ":" in t2:
                sk, safter = t2.split(":", 1)
                sk = sk.strip()
                safter = safter.strip()
                if not safter:
                    pos += 1
                    nested, pos = _parse_object(lines, pos, item_depth + 2)
                    obj[sk] = nested
                else:
                    obj[sk] = _parse_scalar(safter)
                    pos += 1
            else:
                break
        else:
            break
    return obj, pos


def _parse_object(lines: List[Tuple[int, str]], pos: int, depth: int) -> Tuple[Dict[str, Any], int]:
    obj: Dict[str, Any] = {}
    n = len(lines)
    while pos < n:
        d, text = lines[pos]
        if d < depth:
            break
        if d > depth:
            raise ValueError(f"Unexpected deeper indent at line {pos}")
        if text.startswith("- "):
            break

        if ":" not in text:
            raise ValueError(f"Expected key: value at line {pos}")

        key_part, rest = text.split(":", 1)
        key_part = key_part.strip()
        rest = rest.strip()

        m_tab = re.match(r"^([^[]+)\[(\d+)\]\{([^}]*)\}$", key_part)
        if m_tab:
            name, nrows, fields_s = m_tab.group(1), int(m_tab.group(2)), m_tab.group(3)
            fields = [f.strip() for f in fields_s.split(",") if f.strip()]
            rows, pos = _parse_tabular_array(lines, pos, d, name, nrows, fields)
            obj[name] = rows
            continue

        m_arr = re.match(r"^([^[]*)\[(\d+)\]$", key_part)
        if m_arr:
            name, n_expect = m_arr.group(1), int(m_arr.group(2))
            store_key = name if name else "_"
            if rest:
                parts = _split_csv_row(rest) if ("," in rest or '"' in rest) else [p.strip() for p in rest.split(",")]
                obj[store_key] = [_parse_scalar(p) for p in parts]
                pos += 1
                continue
            pos += 1
            items, pos = _parse_list_items(lines, pos, d + 1)
            obj[store_key] = items
            continue

        name = key_part
        if rest:
            obj[name] = _parse_scalar(rest)
            pos += 1
            continue

        pos += 1
        nested, pos = _parse_object(lines, pos, depth + 1)
        obj[name] = nested

    return obj, pos


def decode_document(text: str) -> Dict[str, Any]:
    """Parse a document made of top-level key lines into one mapping object."""
    raw_lines = text.splitlines()
    lines: List[Tuple[int, str]] = []
    for ln in raw_lines:
        if not ln.strip():
            continue
        d, rest = _leading_depth(ln)
        lines.append((d, rest))
    if not lines:
        return {}
    doc, _ = _parse_object(lines, 0, 0)
    return doc


def decode(text: str) -> Any:
    """Parse serialized text from :func:`encode` back into Python values."""
    t = text.strip()
    if not t:
        return None
    if "\n" not in t and ":" not in t:
        return _parse_scalar(t)
    doc = decode_document(text)
    if len(doc) == 1 and "_" in doc:
        return doc["_"]
    return doc
