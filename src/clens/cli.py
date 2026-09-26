import argparse


def cli():
    parser = argparse.ArgumentParser()
    sub_parser = parser.add_subparsers(dest="command")

    parser_index = sub_parser.add_parser("index", help="Index images of a directory")
    parser_index.add_argument("path", help="Path of directory to index")

    args = parser.parse_args()

    match args.command:
        case "index":
            from clens.indexer import index_files

            index_files(args.path)
        case "find":
            pass
        case _:
            parser.print_help()
