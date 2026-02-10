---
description: 'Analyze Windows crash dumps using the windbg command-line tool (no MCP server required)'
---

Use the `windbg` command-line tool to analyze Windows crash dumps directly from the terminal.

## Available Commands

```
uv run windbg list-dumps [--directory DIR] [--recursive]
uv run windbg analyze <dump_path> [--stack] [--modules] [--threads] [--all]
uv run windbg cmd -c <command> (--dump <path> | --remote <conn>)
uv run windbg shell (--dump <path> | --remote <conn>)
```

## WORKFLOW - Execute in this exact sequence:

### Step 1: Dump File Identification
**If no dump file path provided:**
- Run `uv run windbg list-dumps` to discover available crash dumps.
- If the user specifies a directory, use `--directory <path>` and optionally `--recursive`.

### Step 2: Comprehensive Dump Analysis
**Analyze the specified dump file:**

```powershell
uv run windbg analyze <dump_path> --all
```

This automatically runs `!analyze -v`, `.lastevent`, and includes stack traces, modules, and threads.

If the dump is very large (>5GB) or analysis takes too long, the command may timeout. Inform the user and suggest increasing `--timeout`.

**Then extract additional metadata by running individual commands:**

```powershell
uv run windbg cmd --dump <dump_path> -c "vertarget"
uv run windbg cmd --dump <dump_path> -c ".time"
uv run windbg cmd --dump <dump_path> -c "!peb"
uv run windbg cmd --dump <dump_path> -c "r"
uv run windbg cmd --dump <dump_path> -c "k"
```

### Step 3: Generate Structured Analysis Report

## REQUIRED OUTPUT FORMAT:

```markdown
# Crash Dump Analysis Report
**Analysis Date:** [Current Date]
**Dump File:** [filename.dmp]
**File Path:** [Full path to dump file]

## Executive Summary
- **Crash Type:** [Exception type - Access Violation, Heap Corruption, etc.]
- **Severity:** [Critical/High/Medium/Low]
- **Root Cause:** [Brief description of the identified issue]
- **Recommended Action:** [Immediate next steps]

## Dump Metadata
- **File Size:** [MB]
- **Creation Time:** [Date/Time from .time command]
- **OS Build:** [Windows version and build from vertarget]
- **Platform:** [x86/x64/ARM64]
- **Process Name:** [Process name and PID]
- **Process Path:** [Full executable path]
- **Command Line:** [Process command line arguments]
- **Working Directory:** [Process working directory]

## Crash Analysis
**Exception Details:**
- **Exception Code:** [0xC0000005, etc.]
- **Exception Address:** [0x12345678]
- **Faulting Module:** [module.dll or module.exe]
- **Module Version:** [File version]
- **Module Timestamp:** [Build timestamp]
- **Module Base Address:** [0x12345678]

**Call Stack Analysis:**
[Full call stack from kb output]

**Thread Information:**
- **Crashing Thread ID:** [Thread ID]
- **Thread Count:** [Total threads]
- **Other Notable Threads:** [List any threads of interest]

## Root Cause Analysis
- **What happened:** [Technical description of the failure]
- **Why it happened:** [Analysis of contributing factors]
- **Code location:** [Specific function/line if identifiable]

## Recommendations
### Immediate Actions
1. [Specific action item 1]
2. [Specific action item 2]

### Prevention Measures
1. [Code changes to prevent recurrence]
2. [Additional validation/checks needed]
```

## TIPS:
- Use `--timeout 120` for large dumps or slow symbol downloads.
- Use `--symbols-path` to specify a custom symbol server path.
- Use `shell` subcommand for interactive exploration when you need to run many ad-hoc commands.
- Each `cmd` invocation starts a fresh CDB session; use `shell` for repeated commands on the same dump.
