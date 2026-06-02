"""
MCP Notes Server — stores notes as plain markdown files with optional YAML frontmatter.

Tools:
  create_note(title, content, tags?)  — write a new note
  list_notes(tag?)                    — list all notes, optionally filtered by tag
  delete_note(title)                  — remove a note by title

Resource:
  notes://all                         — dump every note's content in one response
"""

import json
import re
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

NOTES_DIR = Path(__file__).parent / "notes"
NOTES_DIR.mkdir(exist_ok=True)

mcp = FastMCP("notes")


# ── helpers ──────────────────────────────────────────────────────────────────

def _slug(title: str) -> str:
    """Turn a title into a safe filename stem."""
    return re.sub(r"[^\w\-]", "_", title.strip().lower())


def _note_path(title: str) -> Path:
    return NOTES_DIR / f"{_slug(title)}.md"


def _parse_tags(text: str) -> list[str]:
    """Extract tags from a YAML-style frontmatter block if present."""
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return []
    fm = match.group(1)
    tag_line = re.search(r"^tags:\s*\[(.+?)\]", fm, re.MULTILINE)
    if not tag_line:
        return []
    return [t.strip().strip('"').strip("'") for t in tag_line.group(1).split(",")]


def _build_frontmatter(tags: list[str], created: str) -> str:
    tag_str = ", ".join(f'"{t}"' for t in tags)
    return f"---\ncreated: {created}\ntags: [{tag_str}]\n---\n"


# ── tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def create_note(title: str, content: str, tags: str = "") -> str:
    """
    Create a new markdown note.

    Args:
        title:   Note title (used as filename). Required.
        content: Body of the note. Required.
        tags:    Comma-separated tags, e.g. "work, ideas". Optional.
    """
    path = _note_path(title)
    if path.exists():
        return f"Error: a note named '{title}' already exists. Delete it first or choose a different title."

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    created = datetime.now().isoformat(timespec="seconds")
    frontmatter = _build_frontmatter(tag_list, created)
    path.write_text(f"{frontmatter}\n# {title}\n\n{content}\n", encoding="utf-8")
    return f"Note '{title}' created at {path.name}."


@mcp.tool()
def list_notes(tag: str = "") -> str:
    """
    List all notes, optionally filtered by tag.

    Args:
        tag: If provided, only notes that contain this tag are returned. Optional.
    """
    files = sorted(NOTES_DIR.glob("*.md"))
    if not files:
        return "No notes found."

    results = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        note_tags = _parse_tags(text)
        if tag and tag.lower() not in [t.lower() for t in note_tags]:
            continue
        heading = next(
            (line.lstrip("# ") for line in text.splitlines() if line.startswith("# ")),
            f.stem,
        )
        tag_display = f" [{', '.join(note_tags)}]" if note_tags else ""
        results.append(f"- {heading}{tag_display}")

    if not results:
        return f"No notes found with tag '{tag}'."
    return "\n".join(results)


@mcp.tool()
def delete_note(title: str) -> str:
    """
    Delete a note by title.

    Args:
        title: Exact title of the note to delete. Required.
    """
    path = _note_path(title)
    if not path.exists():
        return f"Error: no note named '{title}' found."
    path.unlink()
    return f"Note '{title}' deleted."


# ── resource ──────────────────────────────────────────────────────────────────

@mcp.resource("notes://all")
def all_notes() -> str:
    """Return the full content of every note as a single document."""
    files = sorted(NOTES_DIR.glob("*.md"))
    if not files:
        return "No notes yet."
    parts = []
    for f in files:
        parts.append(f"=== {f.stem} ===")
        parts.append(f.read_text(encoding="utf-8").strip())
        parts.append("")
    return "\n".join(parts)


# ── entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
