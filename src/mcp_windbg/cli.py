"""Direct CLI for WinDbg/CDB crash dump analysis.

Run with: uv run mcp-windbg-cli <command>
"""

import argparse
import glob
import os
import sys
from typing import Optional

from .cdb_session import CDBSession, CDBError, get_local_dumps_path


def _print_lines(lines: list[str]) -> None:
    for line in lines:
        print(line)


def _create_session(
    dump_path: Optional[str] = None,
    remote: Optional[str] = None,
    cdb_path: Optional[str] = None,
    symbols_path: Optional[str] = None,
    timeout: int = 30,
    verbose: bool = False,
) -> CDBSession:
    """Create a CDB session, exiting on failure."""
    try:
        return CDBSession(
            dump_path=dump_path,
            remote_connection=remote,
            cdb_path=cdb_path,
            symbols_path=symbols_path,
            timeout=timeout,
            verbose=verbose,
        )
    except (CDBError, FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list_dumps(args: argparse.Namespace) -> None:
    """List crash dump files in a directory."""
    directory = args.directory
    if directory is None:
        directory = get_local_dumps_path()
        if directory is None:
            print("Error: No directory specified and no default dump path found.", file=sys.stderr)
            sys.exit(1)

    if not os.path.isdir(directory):
        print(f"Error: Directory not found: {directory}", file=sys.stderr)
        sys.exit(1)

    pattern = (
        os.path.join(directory, "**", "*.*dmp") if args.recursive
        else os.path.join(directory, "*.*dmp")
    )
    dump_files = sorted(glob.glob(pattern, recursive=args.recursive))

    if not dump_files:
        print(f"No crash dump files found in {directory}")
        return

    print(f"Found {len(dump_files)} crash dump(s) in {directory}:\n")
    for i, f in enumerate(dump_files):
        try:
            size_mb = round(os.path.getsize(f) / (1024 * 1024), 2)
        except (OSError, IOError):
            size_mb = "unknown"
        print(f"  {i + 1}. {f} ({size_mb} MB)")


def cmd_analyze(args: argparse.Namespace) -> None:
    """Open and analyze a crash dump."""
    include_all = args.all
    session = _create_session(
        dump_path=args.dump_path,
        cdb_path=args.cdb_path,
        symbols_path=args.symbols_path,
        timeout=args.timeout,
        verbose=args.verbose,
    )
    try:
        print("### Crash Information")
        _print_lines(session.send_command(".lastevent"))
        print()

        print("### Crash Analysis")
        _print_lines(session.send_command("!analyze -v"))
        print()

        if include_all or args.stack:
            print("### Stack Trace")
            _print_lines(session.send_command("kb"))
            print()

        if include_all or args.modules:
            print("### Loaded Modules")
            _print_lines(session.send_command("lm"))
            print()

        if include_all or args.threads:
            print("### Threads")
            _print_lines(session.send_command("~"))
            print()
    except CDBError as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
    finally:
        session.shutdown()


def cmd_run(args: argparse.Namespace) -> None:
    """Run a single WinDbg command."""
    session = _create_session(
        dump_path=args.dump_path,
        remote=args.remote,
        cdb_path=args.cdb_path,
        symbols_path=args.symbols_path,
        timeout=args.timeout,
        verbose=args.verbose,
    )
    try:
        _print_lines(session.send_command(args.command))
    except CDBError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        session.shutdown()


def cmd_shell(args: argparse.Namespace) -> None:
    """Interactive WinDbg shell (REPL)."""
    session = _create_session(
        dump_path=args.dump_path,
        remote=args.remote,
        cdb_path=args.cdb_path,
        symbols_path=args.symbols_path,
        timeout=args.timeout,
        verbose=args.verbose,
    )
    target = args.dump_path or args.remote
    print(f"WinDbg interactive shell — {target}")
    print("Type 'quit' or 'exit' to close. Ctrl+C to abort.\n")

    try:
        while True:
            try:
                cmd = input("windbg> ")
            except EOFError:
                break

            stripped = cmd.strip().lower()
            if stripped in ("quit", "exit", "q"):
                break
            if not cmd.strip():
                continue

            try:
                _print_lines(session.send_command(cmd))
            except CDBError as e:
                print(f"Error: {e}", file=sys.stderr)
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        session.shutdown()
        print("Session closed.")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mcp-windbg-cli",
        description="WinDbg/CDB crash dump analysis CLI (no MCP required)",
    )
    parser.add_argument("--cdb-path", type=str, help="Custom path to cdb.exe")
    parser.add_argument("--symbols-path", type=str, help="Custom symbols path")
    parser.add_argument("--timeout", type=int, default=30, help="Command timeout in seconds (default: 30)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose CDB output")

    subparsers = parser.add_subparsers(dest="subcommand")

    # list-dumps
    p_list = subparsers.add_parser("list-dumps", help="List crash dump files")
    p_list.add_argument("--directory", type=str, help="Directory to search (default: Windows crash dump path)")
    p_list.add_argument("--recursive", action="store_true", help="Search subdirectories recursively")

    # analyze
    p_analyze = subparsers.add_parser("analyze", help="Analyze a crash dump file")
    p_analyze.add_argument("dump_path", help="Path to crash dump file")
    p_analyze.add_argument("--stack", action="store_true", help="Include stack traces")
    p_analyze.add_argument("--modules", action="store_true", help="Include loaded modules")
    p_analyze.add_argument("--threads", action="store_true", help="Include thread information")
    p_analyze.add_argument("--all", action="store_true", help="Include stack, modules, and threads")

    # cmd
    p_cmd = subparsers.add_parser("cmd", help="Run a single WinDbg command")
    p_cmd_target = p_cmd.add_mutually_exclusive_group(required=True)
    p_cmd_target.add_argument("--dump", dest="dump_path", help="Path to crash dump file")
    p_cmd_target.add_argument("--remote", help="Remote connection string")
    p_cmd.add_argument("-c", "--command", required=True, help="WinDbg command to execute")

    # shell
    p_shell = subparsers.add_parser("shell", help="Interactive WinDbg shell")
    p_shell_target = p_shell.add_mutually_exclusive_group(required=True)
    p_shell_target.add_argument("--dump", dest="dump_path", help="Path to crash dump file")
    p_shell_target.add_argument("--remote", help="Remote connection string")

    args = parser.parse_args()

    if args.subcommand is None:
        parser.print_help()
        sys.exit(1)

    handlers = {
        "list-dumps": cmd_list_dumps,
        "analyze": cmd_analyze,
        "cmd": cmd_run,
        "shell": cmd_shell,
    }
    handlers[args.subcommand](args)
