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
        "find": {"desc": "Find a image from the indexed directories"},
        "match": {"desc": "Match a image from the indexed directories"},
        "version": {"desc": "Print the current clens version"},
    }

    @override
    def format_help(self) -> str:
        command_desc = ""
        for command in self.COMMANDS.keys():
            command_desc += f"    {command}: {self.COMMANDS[command]['desc']}\n"

        return f"""
clens: Local semantic image search tool

Description:
    Clens is a semantic image seach tool that allows users 
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
    parser = ClensCLIParser(prog="clens", add_help=True)
    sub_parser = parser.add_subparsers(dest="command")

    parser_server = sub_parser.add_parser("server")
    parser_server.add_argument("start")
    parser_server.add_argument("stop")

    parser_index = sub_parser.add_parser("index")
    parser_index.add_argument("path")

    parser_find = sub_parser.add_parser("find")
    parser_find.add_argument("query_term")

    args = parser.parse_args()

    match args.command:
        case "server":
            pass
        case "index":
            pass
        case "find":
            pass
        case _:
            parser.print_help()
            sys.exit(0)
