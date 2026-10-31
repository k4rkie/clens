import configparser
import os

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("HF_HUB_VERBOSITY", "error")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse
import sys
from clens.app_config import AppConfig
from pathlib import Path
from typing import override
import logging
from clens.paths import CONFIG_FILE
from clens.runtime import RuntimeState
from importlib.metadata import version
from clens.logger_config import configure_logging


class ClensCLIParser(argparse.ArgumentParser):
    COMMANDS = {
        "server": {
            "desc": "Manage the clens server",
            "arguments": {
                "start": {
                    "desc": "Start the clens server",
                    "arguments": {},
                    "options": {
                        "-p, --port": "Port to start the server on",
                    },
                    "flags": {
                        "-d, --detach": "Detach server from the current shell session",
                    },
                    "req_server": False,
                },
                "stop": {
                    "desc": "Stop the clens server",
                    "arguments": {},
                    "options": {},
                    "flags": {},
                    "req_server": False,
                },
                "status": {
                    "desc": "Get the status of the clens server",
                    "arguments": {},
                    "options": {},
                    "flags": {},
                    "req_server": False,
                },
            },
            "options": {},
            "flags": {},
            "req_server": False,
        },
        "index": {
            "desc": "Index a given directory of images",
            "arguments": {
                "path": {
                    "desc": "Directory of images to index",
                    "arguments": {},
                    "options": {},
                    "flags": {},
                },
            },
            "options": {},
            "flags": {},
            "req_server": True,
        },
        "find": {
            "desc": "Find an image from the indexed directories",
            "arguments": {
                "query_term": {
                    "desc": "Query term to search for",
                    "arguments": {},
                    "options": {},
                    "flags": {},
                }
            },
            "options": {"-c, --count": "Number of images to find (default: 5)"},
            "flags": {"-p, --plain": "Output plain tab-seperated result"},
            "req_server": True,
        },
        "match": {
            "desc": "Match an image from the indexed directories",
            "arguments": {
                "image_path": {
                    "desc": "Image to find matches for",
                    "arguments": {},
                    "options": {},
                    "flags": {},
                }
            },
            "options": {"-c, --count": "Numbers of images to find (default: 5)"},
            "flags": {"-p, --plain": "Output plain tab-seperated result"},
            "req_server": True,
        },
        "version": {
            "desc": "Print the current clens version",
            "arguments": {},
            "options": {},
            "flags": {},
            "req_server": False,
        },
    }

    def __init__(self, *args, custom_help: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_help = custom_help

    @override
    def format_help(self) -> str:
        if self.custom_help:
            return self.custom_help
        if self.prog != "clens":
            return super().format_help()
        command_desc = ""
        for command in self.COMMANDS.keys():
            command_desc += f"    {command}: {self.COMMANDS[command]['desc']}\n"

        return f"""
clens: Local semantic image search tool

Description:
    Clens is a semantic image search tool that allows users 
    to index a given directory of images and search through it 
    using natural language, search for matching images using 
    another image etc. locally on their device.

Usage:
    clens [COMMAND] <ARGUMENT> <...options>
    clens [COMMAND] --help

Commands:
{command_desc}

Examples:
    clens server start --port 6969 --detach

    clens index ./Pictures

    clens find "a dog with a hat"

"""


configure_logging()

logger = logging.getLogger(__name__)

config = AppConfig.load_from_file(CONFIG_FILE)
config.save_to_file()


def cli():

    clens_parser = ClensCLIParser(prog="clens", add_help=True)
    commands = clens_parser.add_subparsers(dest="command")

    # Server sub command
    server_parser = commands.add_parser(
        "server",
        custom_help=format_custom_help(
            "clens server", ClensCLIParser.COMMANDS["server"]
        ),
    )
    server_commands = server_parser.add_subparsers(dest="server_action")

    server_start_parser = server_commands.add_parser(
        "start",
        custom_help=format_custom_help(
            "clens server start",
            ClensCLIParser.COMMANDS["server"]["arguments"]["start"],
        ),
    )
    server_start_parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=config.preferences.default_port,
    )
    server_start_parser.add_argument(
        "-d",
        "--detach",
        action="store_true",
    )

    server_commands.add_parser(
        "stop",
        custom_help=format_custom_help(
            "clens server stop",
            ClensCLIParser.COMMANDS["server"]["arguments"]["stop"],
        ),
    )
    server_commands.add_parser(
        "status",
        custom_help=format_custom_help(
            "clens server status",
            ClensCLIParser.COMMANDS["server"]["arguments"]["status"],
        ),
    )

    # Index sub command
    index_parser = commands.add_parser(
        "index",
        custom_help=format_custom_help("clens index", ClensCLIParser.COMMANDS["index"]),
    )
    index_parser.add_argument(
        "path",
        nargs="?",
        default=None,
    )

    # Find sub command
    find_parser = commands.add_parser(
        "find",
        custom_help=format_custom_help("clens find", ClensCLIParser.COMMANDS["find"]),
    )
    find_parser.add_argument(
        "query_term",
        nargs="?",
        default=None,
    )
    find_parser.add_argument(
        "-p",
        "--plain",
        action="store_true",
    )
    find_parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=5,
    )

    # Match sub command
    match_parser = commands.add_parser(
        "match",
        custom_help=format_custom_help("clens match", ClensCLIParser.COMMANDS["match"]),
    )
    match_parser.add_argument(
        "image_path",
        nargs="?",
        default=None,
    )
    match_parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=5,
    )
    match_parser.add_argument(
        "-p",
        "--plain",
        action="store_true",
    )

    # Version sub command
    version_parser = commands.add_parser(
        "version",
        custom_help=format_custom_help(
            "clens version", ClensCLIParser.COMMANDS["version"]
        ),
    )

    args = clens_parser.parse_args()

    if args.command is not None and clens_parser.COMMANDS[args.command]["req_server"]:
        if not RuntimeState.load_runtime().is_running(timeout=1.0):
            logger.error("Clens server is not running!")
            logger.info("Start the server first with: clens server start")
            sys.exit(1)

    match args.command:
        case "server":
            match args.server_action:
                case "start":
                    from clens.command_handlers import cmd_start_server

                    cmd_start_server(args.port, args.detach)
                case "stop":
                    from clens.command_handlers import cmd_stop_server

                    cmd_stop_server()
                case "status":
                    from clens.command_handlers import cmd_server_status

                    cmd_server_status()
                case _:
                    server_parser.print_help()
                    sys.exit(0)

        case "index":
            if args.path is None:
                index_parser.print_help()
                sys.exit(0)
            from clens.command_handlers import cmd_index_images

            cmd_index_images(args.path)
        case "find":
            if args.query_term is None:
                find_parser.print_help()
                sys.exit(0)
            from clens.command_handlers import cmd_find_images

            cmd_find_images(args.query_term, args.count, args.plain)
        case "match":
            if args.image_path is None:
                match_parser.print_help()
                sys.exit(0)
            from clens.command_handlers import cmd_match_image

            cmd_match_image(args.image_path, args.count, args.plain)
        case "version":
            print(f"clens v{version('clens-cli')}")
        case _:
            clens_parser.print_help()
            sys.exit(0)


def format_custom_help(prog: str, cmd_data) -> str:
    prog_name = prog if prog.startswith("clens") else f"clens {prog}"
    desc = cmd_data.get("desc", "")
    args = cmd_data.get("arguments", {})
    options = cmd_data.get("options", {})
    flags = cmd_data.get("flags", {})

    usage_parts = [prog_name, "[-h]"]

    for flag_key in flags.keys():
        short = flag_key.split(",")[0].strip()
        usage_parts.append(f"[{short}]")

    for opt_key in options.keys():
        parts = [p.strip() for p in opt_key.split(",")]
        short = parts[0]
        val_name = parts[-1].lstrip("-").upper()
        usage_parts.append(f"[{short} {val_name}]")

    has_subcommands = len(args) > 1 or any(
        isinstance(v, dict)
        and (v.get("options") or v.get("flags") or v.get("arguments"))
        for v in args.values()
    )

    if args:
        if has_subcommands:
            usage_parts.append(f"{{{','.join(args.keys())}}}")
        else:
            usage_parts.extend(f"<{k}>" for k in args.keys())

    sections = [
        f"\n{prog_name}: {desc}\n",
        f"Usage:\n    {' '.join(usage_parts)}\n",
    ]

    if args:
        header = "Commands:" if has_subcommands else "Arguments:"
        lines = [f"{header}"]
        max_w = max(len(k) for k in args.keys())
        for k, v in args.items():
            arg_desc = v.get("desc", "") if isinstance(v, dict) else str(v)
            lines.append(f"    {k:<{max_w}}    {arg_desc}")
        sections.append("\n".join(lines) + "\n")

    if options:
        lines = ["Options:"]
        max_w = max(len(k) for k in options.keys())
        for k, v in options.items():
            lines.append(f"    {k:<{max_w}}    {v}")
        sections.append("\n".join(lines) + "\n")

    all_flags = {**flags, "-h, --help": "Show this help message and exit\n"}
    lines = ["Flags:"]
    max_w = max(len(k) for k in all_flags.keys())
    for k, v in all_flags.items():
        lines.append(f"    {k:<{max_w}}    {v}")
    sections.append("\n".join(lines) + "\n")

    return "\n".join(sections)
