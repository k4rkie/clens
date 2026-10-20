import os

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("HF_HUB_VERBOSITY", "error")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse
import subprocess
import sys


def cli():
    parser = argparse.ArgumentParser()
    sub_parser = parser.add_subparsers(dest="command")

    parser_server = sub_parser.add_parser("server") 
    parser_server.add_argument("-u", "--up")
    parser_server.add_argument("-d", "--down")

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
            print_clens_help()


def print_clens_help():
    print("""
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
    server  : Manage the clens server
    index   : Index a given directory of images
    find    : Find a image from the indexed directories
    match   : Match a image from the indexed directories
    version : Print the current version of clens
Examples:
    clens index ./Pictures
          """)

