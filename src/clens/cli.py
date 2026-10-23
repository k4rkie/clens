import os
from typing import override

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("HF_HUB_VERBOSITY", "error")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse
import subprocess
import sys


class ClensCLIParser(argparse.ArgumentParser):
    COMMANDS = {
        "server": {"desc": "Manage the clens server"},
        "index": {"desc": "Index a given directory of images"},
        "find": {"desc": "Find an image from the indexed directories"},
        "match": {"desc": "Match an image from the indexed directories"},
        "version": {"desc": "Print the current clens version"},
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
    clens [COMMAND] <ARGUMENT>
    clens [COMMAND] --help

Commands:
{command_desc}

Examples:
    clens index ./Pictures

"""


def cli():
    clens_parser = ClensCLIParser(prog="clens", add_help=True)
    commands = clens_parser.add_subparsers(dest="command")

    # Server sub command
    server_parser = commands.add_parser("server")
    server_commands = server_parser.add_subparsers(dest="server_action", required=True)

    server_start_parser = server_commands.add_parser("start", help="start the clens server")
    server_start_parser.add_argument("-p","--port", type=int, default=8080, help="port to start the server on")
    server_start_parser.add_argument("-d","--detach", action="store_true",help="detach server from current shell")

    server_commands.add_parser("stop", help="stop the clens server")

    # Index sub command
    index_parser = commands.add_parser("index")
    index_parser.add_argument("path", help="directory to index")

    # Find sub command
    find_parser = commands.add_parser("find")
    find_parser.add_argument("query_term")

    # Match sub command
    match_parser = commands.add_parser("match")
    match_parser.add_argument("image")

    # Version sub command
    version = commands.add_parser("version")

    args = clens_parser.parse_args()

    match args.command:
        case "server":
            print("You chose the action:", args.server_action)
            match args.server_action:
                case "start":
                    pass
                case "stop":
                    pass
        case "index":
            pass
        case "find":
            pass
        case "match":
            pass
        case "version":
            print("clens v0.0.1")
        case _:
            clens_parser.print_help()
            sys.exit(0)
