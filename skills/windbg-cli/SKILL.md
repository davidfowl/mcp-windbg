---
name: windbg-cli
description: Analyze Windows crash dumps and debug processes using WinDbg/CDB. Use when the user wants to triage crash dumps, inspect threads, view stack traces, or run WinDbg debugger commands.
allowed-tools: Bash(windbg:*), Bash(uv:*)
---

# Windows Crash Dump Analysis with WinDbg/CDB

Use this skill to analyze Windows crash dumps (.dmp files) and debug remote processes using the WinDbg/CDB debugger engine.

## Quick start

```bash
# List available crash dumps (checks Windows default dump folder)
uv run --from windbg-cli windbg list-dumps

# Analyze a crash dump with full details
uv run --from windbg-cli windbg analyze C:\path\to\crash.dmp --all

# Run a single WinDbg command against a dump
uv run --from windbg-cli windbg cmd --dump C:\path\to\crash.dmp -c "!analyze -v"

# Interactive WinDbg shell
uv run --from windbg-cli windbg shell --dump C:\path\to\crash.dmp
```

## Core workflow

1. Discover crash dumps with `list-dumps`
2. Run initial analysis with `analyze --all`
3. Extract additional metadata with targeted `cmd` calls
4. Use `shell` for interactive exploration when needed

## Commands

### List Crash Dumps

```bash
# List dumps in the Windows default crash dump folder
uv run --from windbg-cli windbg list-dumps

# List dumps in a specific directory
uv run --from windbg-cli windbg list-dumps --directory C:\CrashDumps

# Search recursively
uv run --from windbg-cli windbg list-dumps --directory C:\CrashDumps --recursive
```

### Analyze a Crash Dump

```bash
# Full analysis (stack, modules, threads)
uv run --from windbg-cli windbg analyze C:\path\to\crash.dmp --all

# Only include stack traces
uv run --from windbg-cli windbg analyze C:\path\to\crash.dmp --stack

# Only include loaded modules
uv run --from windbg-cli windbg analyze C:\path\to\crash.dmp --modules

# Only include thread information
uv run --from windbg-cli windbg analyze C:\path\to\crash.dmp --threads

# With custom symbols path and timeout
uv run --from windbg-cli windbg --symbols-path "SRV*C:\Symbols*https://msdl.microsoft.com/download/symbols" --timeout 120 analyze C:\path\to\crash.dmp --all
```

### Run a Single WinDbg Command

```bash
# Crash analysis
uv run --from windbg-cli windbg cmd --dump C:\path\to\crash.dmp -c "!analyze -v"

# OS version and platform
uv run --from windbg-cli windbg cmd --dump C:\path\to\crash.dmp -c "vertarget"

# Call stack
uv run --from windbg-cli windbg cmd --dump C:\path\to\crash.dmp -c "k"

# Dump creation time
uv run --from windbg-cli windbg cmd --dump C:\path\to\crash.dmp -c ".time"

# Process environment
uv run --from windbg-cli windbg cmd --dump C:\path\to\crash.dmp -c "!peb"

# Registers
uv run --from windbg-cli windbg cmd --dump C:\path\to\crash.dmp -c "r"

# Loaded modules
uv run --from windbg-cli windbg cmd --dump C:\path\to\crash.dmp -c "lm"

# All threads
uv run --from windbg-cli windbg cmd --dump C:\path\to\crash.dmp -c "~"

# Stack trace with parameters
uv run --from windbg-cli windbg cmd --dump C:\path\to\crash.dmp -c "kb"
```

### Run Commands Against a Remote Debug Session

```bash
# Connect to a remote debug server
uv run --from windbg-cli windbg cmd --remote "tcp:Port=5005,Server=192.168.0.100" -c "kb"

# Interactive remote debugging
uv run --from windbg-cli windbg shell --remote "tcp:Port=5005,Server=192.168.0.100"
```

### Interactive Shell

```bash
# Open interactive WinDbg session on a dump
uv run --from windbg-cli windbg shell --dump C:\path\to\crash.dmp

# Type WinDbg commands at the prompt:
#   windbg> !analyze -v
#   windbg> kb
#   windbg> lm
#   windbg> quit
```

## Global Options

```bash
# Custom CDB path (if not auto-detected)
uv run --from windbg-cli windbg --cdb-path "C:\path\to\cdb.exe" ...

# Custom symbols path
uv run --from windbg-cli windbg --symbols-path "SRV*C:\Symbols*https://msdl.microsoft.com/download/symbols" ...

# Increase timeout for large dumps or slow symbol downloads
uv run --from windbg-cli windbg --timeout 120 ...

# Verbose CDB output for debugging
uv run --from windbg-cli windbg --verbose ...
```

## Common Crash Dump Locations

```
# Windows Error Reporting default
%LOCALAPPDATA%\CrashDumps\

# Configured via registry
HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps

# IIS / ASP.NET crash dumps
C:\Windows\System32\LogFiles\
```

## Example: Full Crash Dump Triage

```bash
# 1. Find available dumps
uv run --from windbg-cli windbg list-dumps

# 2. Run full analysis
uv run --from windbg-cli windbg --timeout 120 analyze C:\Users\me\AppData\Local\CrashDumps\myapp.exe.1234.dmp --all

# 3. Get OS/platform details
uv run --from windbg-cli windbg cmd --dump C:\Users\me\AppData\Local\CrashDumps\myapp.exe.1234.dmp -c "vertarget"

# 4. Get dump timestamp
uv run --from windbg-cli windbg cmd --dump C:\Users\me\AppData\Local\CrashDumps\myapp.exe.1234.dmp -c ".time"

# 5. Get process environment
uv run --from windbg-cli windbg cmd --dump C:\Users\me\AppData\Local\CrashDumps\myapp.exe.1234.dmp -c "!peb"

# 6. Get registers
uv run --from windbg-cli windbg cmd --dump C:\Users\me\AppData\Local\CrashDumps\myapp.exe.1234.dmp -c "r"
```

## Tips

- Use `--timeout 120` for large dumps or when symbols need to download.
- Each `cmd` invocation starts a fresh CDB session. Use `shell` for repeated commands on the same dump to avoid re-loading.
- Set `CDB_PATH` environment variable if cdb.exe is not in a standard location.
- The `--symbols-path` flag accepts the same format as the `_NT_SYMBOL_PATH` environment variable.
