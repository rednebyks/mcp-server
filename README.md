# MCP Notes Server

A local MCP server that lets Claude Desktop create, list, and delete markdown notes stored on disk.

---

## Setup

**Requirements:** Python 3.10+

**Option A — with [uv](https://github.com/astral-sh/uv)**

```bash
cd mcp-server
uv venv
uv pip install -r requirements.txt
.venv/bin/python server.py   # Ctrl-C to stop
```

**Option B — plain Python**

```bash
cd mcp-server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py   # Ctrl-C to stop
```

### Connect to Claude Desktop

Merge the following into `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "notes": {
      "command": "/ABSOLUTE/PATH/TO/mcp-server/.venv/bin/python",
      "args": ["/ABSOLUTE/PATH/TO/mcp-server/server.py"]
    }
  }
}
```

Replace the paths with the actual absolute paths on your machine (see `claude_desktop_config.json` in this repo for a ready-made example).

Restart Claude Desktop after saving the config. You should see a hammer icon indicating the tools are available.

---

## Tools

| Tool | Required args | Optional args | What it does |
|---|---|---|---|
| `create_note` | `title`, `content` | `tags` (comma-separated) | Creates a `.md` file in `notes/` with YAML frontmatter |
| `list_notes` | — | `tag` | Lists all notes; filters by tag if provided |
| `delete_note` | `title` | — | Deletes the note file matching the title |

## Resources

| URI | What it returns |
|---|---|
| `notes://all` | Full content of every note concatenated into one document |

Notes are stored as plain markdown files under the `notes/` directory next to `server.py`.

---

## Example Dialogs

### 1 — Creating a tagged note

> **User:** Create a note titled "Sprint Goals" with content "Ship the auth refactor and close 3 bugs" and tag it "work".
>
> **Claude:** *(calls `create_note` with title="Sprint Goals", content="Ship the auth refactor and close 3 bugs", tags="work")*
>
> Note 'Sprint Goals' created at sprint_goals.md.

### 2 — Listing notes by tag

> **User:** Show me all notes tagged "work".
>
> **Claude:** *(calls `list_notes` with tag="work")*
>
> - Sprint Goals [work]

### 3 — Deleting a note

> **User:** Delete the "Sprint Goals" note.
>
> **Claude:** *(calls `delete_note` with title="Sprint Goals")*
>
> Note 'Sprint Goals' deleted.

---

## Limitations

- No full-text search inside note bodies — `list_notes` only filters by tag.
- Note titles are slugified for filenames; two titles that differ only in punctuation may collide.
- No update/edit tool — delete and re-create to replace a note.
- Notes are local only; no sync or backup mechanism.
