from __future__ import annotations

import base64
import io
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict

import pandas as pd
import streamlit as st


SEARCH_TRIGGER_KEYWORDS = {
    "find",
    "search",
    "show",
    "document",
    "doc",
    "contract",
    "invoice",
    "report",
    "handbook",
    "slide",
    "presentation",
    "prd",
}


def _default_root() -> Path:
    """Resolve a sensible default data root. Prefer dummy_data/, fallback to sample_data/."""
    app_root = Path.cwd()
    cand = app_root / "dummy_data"
    if cand.exists() and cand.is_dir():
        return cand
    fallback = app_root / "sample_data"
    return fallback if fallback.exists() and fallback.is_dir() else cand


def scan_dummy_data(root: str | Path | None = None) -> List[Dict]:
    """Scan a folder for files and collect lightweight metadata.

    Returns a list of dicts with: path, name, ext, size_kb, modified_iso.
    """
    root_path = Path(root) if root else _default_root()
    if not root_path.exists() or not root_path.is_dir():
        return []

    records: List[Dict] = []
    for entry in sorted(root_path.glob("**/*")):
        if entry.is_file():
            try:
                stat = entry.stat()
                records.append(
                    {
                        "path": str(entry.resolve()),
                        "name": entry.name,
                        "ext": entry.suffix.lower(),
                        "size_kb": round(stat.st_size / 1024, 1),
                        "modified_iso": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                    }
                )
            except OSError:
                # Skip unreadable files
                continue
    return records


def _tokenize(text: str) -> List[str]:
    return [t for t in ''.join(ch if ch.isalnum() else ' ' for ch in text.lower()).split() if t]


def looks_like_search(query: str) -> bool:
    tokens = set(_tokenize(query))
    return any(k in tokens or k in query.lower() for k in SEARCH_TRIGGER_KEYWORDS)


def search_files(query: str, records: List[Dict], k: int = 5) -> List[Dict]:
    if not query or not records:
        return []
    q_tokens = set(_tokenize(query))
    scored: List[tuple[int, Dict]] = []
    for rec in records:
        name_tokens = set(_tokenize(rec.get("name", "")))
        overlap = len(q_tokens & name_tokens)
        # Also give a small boost for substring match
        if overlap == 0 and any(t in rec.get("name", "").lower() for t in q_tokens):
            overlap = 1
        if overlap > 0:
            scored.append((overlap, rec))
    scored.sort(key=lambda x: (-x[0], x[1].get("name", "")))
    return [rec for _, rec in scored[:k]]


def _render_pdf(path: Path) -> None:
    try:
        # Prefer st.pdf when available; fallback to iframe
        if hasattr(st, "pdf"):
            st.pdf(str(path))
        else:
            with open(path, "rb") as f:
                data = f.read()
            b64 = base64.b64encode(data).decode("utf-8")
            html = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="600px"></iframe>'
            st.components.v1.html(html, height=620)
    except Exception:
        st.warning("Preview not available")


def render_preview(path: Path) -> None:
    ext = path.suffix.lower()
    try:
        if ext == ".txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(1000)
            st.code(content)
        elif ext == ".csv":
            df = pd.read_csv(path)
            st.dataframe(df.head())
        elif ext in {".xlsx", ".xls"}:
            df = pd.read_excel(path)
            st.dataframe(df.head())
        elif ext in {".png", ".jpg", ".jpeg"}:
            st.image(str(path))
        elif ext == ".pdf":
            _render_pdf(path)
        else:
            st.info("Preview not supported.")
    except Exception:
        st.warning("Preview not available")


def render_results(results: List[Dict]) -> None:
    if not results:
        st.info("No related documents found.")
        return

    for rec in results:
        path = Path(rec["path"]) if rec.get("path") else None
        with st.container(border=True):
            cols = st.columns([3, 2])
            with cols[0]:
                icon = _icon_for_ext(rec.get('ext',''))
                st.markdown(f"{icon} **{rec.get('name','')}**")
                meta = f"{rec.get('ext','')} • {rec.get('size_kb', 0)} KB • {rec.get('modified_iso','')}"
                st.caption(meta)
            with cols[1]:
                if path and path.exists():
                    with open(path, "rb") as f:
                        data = f.read()
                    dl_label = f"Download"
                    st.download_button(label=dl_label, data=data, file_name=path.name, mime=_guess_mime(path.suffix.lower()))

            if path and path.exists():
                with st.expander("Preview"):
                    render_preview(path)


def _guess_mime(ext: str) -> str:
    return {
        ".txt": "text/plain",
        ".csv": "text/csv",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".pdf": "application/pdf",
    }.get(ext, "application/octet-stream")


def _icon_for_ext(ext: str) -> str:
    mapping = {
        ".txt": "📝",
        ".csv": "📈",
        ".xlsx": "📊",
        ".xls": "📊",
        ".png": "🖼️",
        ".jpg": "🖼️",
        ".jpeg": "🖼️",
        ".pdf": "📄",
    }
    return mapping.get(ext.lower(), "📄")


