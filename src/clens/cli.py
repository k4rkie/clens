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
from clens.paths import CONFIG_FILE, RUNTIME_FILE
from clens.runtime import RuntimeState


class ClensCLIParser(argparse.ArgumentParser):
    COMMANDS = {
        "server": {"desc": "Manage the clens server", "req_server": False},
        "index": {"desc": "Index a given directory of images", "req_server": True},
        "find": {
            "desc": "Find an image from the indexed directories",
            "req_server": True,
        },
        "match": {
            "desc": "Match an image from the indexed directories",
            "req_server": True,
        },
        "version": {"desc": "Print the current clens version", "req_server": False},
    }

    @override
    def format_help(self) -> str:
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
    clens start server --port 6969 --detach

    clens index ./Pictures

    clens find "a dog with a hat"

"""


logging.basicConfig(
    level=logging.INFO,
    format=" [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)
runtime_state = RuntimeState().load_runtime()

config = AppConfig.load_from_file(CONFIG_FILE)
config.save_to_file()


def cli():

    clens_parser = ClensCLIParser(prog="clens", add_help=True)
    commands = clens_parser.add_subparsers(dest="command")

    # Server sub command
    server_parser = commands.add_parser("server")
    server_commands = server_parser.add_subparsers(dest="server_action", required=True)

    server_start_parser = server_commands.add_parser(
        "start", help="Start the clens server"
    )
    server_start_parser.add_argument(
        "-H",
        "--host",
        type=str,
        default=config.preferences.default_host,
        help="Host to start the server on",
    )
    server_start_parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=config.preferences.default_port,
        help="Port to start the server on",
    )
    server_start_parser.add_argument(
        "-d", "--detach", action="store_true", help="Detach server from current shell"
    )

    server_commands.add_parser("stop", help="Stop the clens server")
    server_commands.add_parser("status", help="Get the clens server status")

    # Index sub command
    index_parser = commands.add_parser("index")
    index_parser.add_argument("path", help="Directory to index")

    # Find sub command
    find_parser = commands.add_parser("find")
    find_parser.add_argument("query_term")
    find_parser.add_argument(
        "-p", "--plain", action="store_true", help="Output plain tab-seperated result"
    )
    find_parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=5,
        help="Number of images to find (Default: 5)",
    )

    # Match sub command
    match_parser = commands.add_parser("match")
    match_parser.add_argument("image_path", help="image to find matches for")
    match_parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=5,
        help="Numbers of images to find (Default: 5)",
    )
    match_parser.add_argument(
        "-p", "--plain", action="store_true", help="Output plain tab-seperated result"
    )

    # Version sub command
    version = commands.add_parser("version")

    args = clens_parser.parse_args()

    if args.command is not None and clens_parser.COMMANDS[args.command]["req_server"]:
        if not RUNTIME_FILE.exists():
            logger.error("Clens server is not running!")
            logger.info("Start the server first with: clens server start")
            sys.exit(1)

    match args.command:
        case "server":
            match args.server_action:
                case "start":
                    from clens.command_handlers import cmd_start_server

                    cmd_start_server(args.host, args.port, args.detach)
                case "stop":
                    from clens.command_handlers import cmd_stop_server

                    cmd_stop_server()
                case "status":
                    from clens.command_handlers import cmd_server_status

                    cmd_server_status()

        case "index":
            from clens.command_handlers import cmd_index_images

            cmd_index_images(args.path)
        case "find":
            from clens.command_handlers import cmd_find_images

            cmd_find_images(args.query_term, args.count, args.plain)
        case "match":
            from clens.command_handlers import cmd_match_image

            cmd_match_image(args.image_path, args.count, args.plain)
        case "version":
            print("clens v0.0.1")
        case _:
            clens_parser.print_help()
            sys.exit(0)
