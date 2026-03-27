"""
THRESHOLD_ONSET — Universal File Input

Accepts any file: text, image, video, binary.
Converts to token sequence for pipeline (text) or byte chunks (binary).
"""

from pathlib import Path
from typing import List, Tuple, Optional

# Default chunk size for binary (bytes per "token")
DEFAULT_BINARY_CHUNK = 8
# Max file size (bytes) to prevent memory exhaustion
DEFAULT_MAX_FILE_BYTES = 50 * 1024 * 1024  # 50 MB


def load_file(path: Path, max_bytes: int = DEFAULT_MAX_FILE_BYTES) -> Tuple[bytes, bool]:
    """
    Load any file as bytes.

    Args:
        path: File path.
        max_bytes: Max bytes to read (truncate if larger).

    Returns:
        (bytes, is_text) — is_text=True if valid UTF-8.
    """
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")

    size = path.stat().st_size
    if size > max_bytes:
        size = max_bytes  # Read only first max_bytes

    with open(path, "rb") as f:
        data = f.read(size)

    # Try UTF-8 decode
    try:
        data.decode("utf-8")
        is_text = True
    except UnicodeDecodeError:
        is_text = False

    return data, is_text


def bytes_to_tokens(
    data: bytes,
    mode: str = "auto",
    binary_chunk: int = DEFAULT_BINARY_CHUNK,
) -> List[str]:
    """
    Convert raw bytes to token list for pipeline.

    Args:
        data: Raw file bytes.
        mode: "text" | "bytes" | "auto"
            - text: decode UTF-8, split on whitespace (words).
            - bytes: chunk into binary_chunk-byte blocks, hex each.
            - auto: use text if valid UTF-8, else bytes.
        binary_chunk: Bytes per chunk when mode is bytes.

    Returns:
        List of token strings (for TokenAction hashing).
    """
    if mode == "bytes":
        return _bytes_to_chunk_tokens(data, binary_chunk)

    if mode == "text":
        try:
            text = data.decode("utf-8")
            return text.split()
        except UnicodeDecodeError:
            return _bytes_to_chunk_tokens(data, binary_chunk)

    # auto
    try:
        text = data.decode("utf-8")
        return text.split()
    except UnicodeDecodeError:
        return _bytes_to_chunk_tokens(data, binary_chunk)


def _bytes_to_chunk_tokens(data: bytes, chunk_size: int) -> List[str]:
    """Chunk bytes into hex strings."""
    tokens = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i : i + chunk_size]
        tokens.append(chunk.hex())
    return tokens


def _extract_docx_text(path: Path) -> Optional[str]:
    """Extract text from .docx using stdlib (zip + XML). Returns None if fails."""
    try:
        import zipfile
        import xml.etree.ElementTree as ET

        with zipfile.ZipFile(path, "r") as z:
            xml_content = z.read("word/document.xml")
        root = ET.fromstring(xml_content)
        parts = []
        for t in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"):
            if t.text:
                parts.append(t.text)
            if t.tail:
                parts.append(t.tail)
        return " ".join(parts).strip() if parts else None
    except Exception:  # pylint: disable=broad-exception-caught
        return None


def file_to_input_string(
    path: Path,
    mode: str = "auto",
    binary_chunk: int = DEFAULT_BINARY_CHUNK,
    max_bytes: int = DEFAULT_MAX_FILE_BYTES,
) -> Tuple[str, str]:
    """
    Load any file and convert to string for pipeline.

    Pipeline expects a string; tokenize_text will split it.
    For text: pass decoded UTF-8 (preserves content for tokenization).
    For binary: pass space-joined hex chunks (tokenize splits to chunks).
    For .docx: extract text via zip+XML (stdlib only).

    Args:
        path: File path.
        mode: "text" | "bytes" | "auto"
        binary_chunk: Bytes per chunk for binary.
        max_bytes: Max file size to read.

    Returns:
        (input_string, input_type) — input_type is "text" or "binary".
    """
    path = Path(path).resolve()
    suffix = path.suffix.lower()

    # .docx: try text extraction first
    if suffix == ".docx" and mode != "bytes":
        text = _extract_docx_text(path)
        if text:
            return text, "text"

    data, is_text = load_file(path, max_bytes)

    if mode == "bytes" or (mode == "auto" and not is_text):
        tokens = _bytes_to_chunk_tokens(data, binary_chunk)
        return " ".join(tokens), "binary"

    text = data.decode("utf-8")
    return text, "text"


def _looks_like_windows_drive(s: str) -> bool:
    """True only for ``X:\\`` or ``X:/`` style absolute paths (single ASCII letter)."""
    return (
        len(s) >= 3
        and s[0].isascii()
        and s[0].isalpha()
        and s[1] == ":"
        and s[2] in ("/", "\\")
    )


def is_file_path(s: str, base: Optional[Path] = None) -> bool:
    """Return True if s looks like a file path that exists."""
    if not s or len(s) > 4096:
        return False
    s = s.strip()
    if not s:
        return False
    # Corpus paragraphs / prose — never treat as paths
    if "\n" in s or "\r" in s:
        return False
    # Multiple tokens without path separators → sentence, not a filesystem path.
    # Do not use ``\":\" in s`` (Tamil/English often contains ":" e.g. times, § refs).
    if " " in s and "/" not in s and "\\" not in s:
        if not _looks_like_windows_drive(s):
            return False
    try:
        p = Path(s)
        if not p.is_absolute() and base is not None:
            p = (base / p).resolve()
        else:
            p = p.resolve()
    except OSError:
        return False
    try:
        return p.exists() and p.is_file()
    except OSError:
        # Windows: WinError 1113 if path cannot be encoded to the ANSI code page
        return False
