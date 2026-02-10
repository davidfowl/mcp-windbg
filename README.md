# mcp-windbg

WinDbg/CDB crash dump analysis CLI tools with **SKILLS** for coding agents.

> Forked from [svnscha/mcp-windbg](https://github.com/svnscha/mcp-windbg) — the original MCP server for WinDbg crash analysis.

## Available Skills

| Skill | Description |
|-------|-------------|
| [windbg-cli](skills/windbg-cli/SKILL.md) | Analyze Windows crash dumps and debug processes using WinDbg/CDB |

## What are Skills?

Skills are lightweight prompts that teach coding agents how to use CLI tools effectively. They provide:

- **Token-efficient** workflows that don't bloat LLM context
- **Purpose-built commands** for specific tasks
- **Best practices** for common scenarios

## Requirements

- Windows with [Debugging Tools for Windows](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/) or [WinDbg from Microsoft Store](https://apps.microsoft.com/detail/9pgjgd53tn86)
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

## Installing the Skill

### GitHub Copilot CLI (recommended)

```bash
/plugin marketplace add davidfowl/mcp-windbg
/plugin install windbg-cli@mcp-windbg
```

### Claude Code

```bash
mkdir -p .claude/skills/windbg-cli
curl -o .claude/skills/windbg-cli/SKILL.md \
  https://raw.githubusercontent.com/davidfowl/mcp-windbg/main/skills/windbg-cli/SKILL.md
```

## Quick Start

```bash
# List available crash dumps
uv run --from mcp-windbg mcp-windbg-cli list-dumps

# Analyze a dump with full details
uv run --from mcp-windbg mcp-windbg-cli analyze C:\path\to\crash.dmp --all

# Run a single WinDbg command
uv run --from mcp-windbg mcp-windbg-cli cmd --dump C:\path\to\crash.dmp -c "!analyze -v"

# Interactive WinDbg shell
uv run --from mcp-windbg mcp-windbg-cli shell --dump C:\path\to\crash.dmp
```

## CLI Commands

| Command | Purpose |
|---------|---------|
| `list-dumps` | Discover crash dump files in a directory |
| `analyze` | One-shot crash dump analysis with optional `--stack`, `--modules`, `--threads`, `--all` |
| `cmd` | Run a single WinDbg command against a `--dump` or `--remote` target |
| `shell` | Interactive WinDbg REPL for a `--dump` or `--remote` target |

### Global Options

```
--cdb-path PATH        Custom path to cdb.exe
--symbols-path PATH    Custom symbols path
--timeout SECONDS      Command timeout (default: 30)
--verbose              Enable verbose CDB output
```

## Skills-less Operation

You can also point your agent directly at the tool's help:

```
Analyze C:\dumps\app.dmp using mcp-windbg-cli.
Check uv run --from mcp-windbg mcp-windbg-cli --help for available commands.
```

## License

MIT
