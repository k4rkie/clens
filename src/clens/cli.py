import argparse


def cli():
    parser = argparse.ArgumentParser()
    sub_parser = parser.add_subparsers(dest="command")

    parser_index = sub_parser.add_parser("index", help="Index images of a directory")
    parser_index.add_argument("path", help="Path of directory to index")

    parser_find = sub_parser.add_parser("find", help="Find images via text")
    parser_find.add_argument("search_text", help="Term to search for")

    args = parser.parse_args()

    match args.command:
        case "index":
            from clens.indexer import index_files

            index_files(args.path)
        case "find":
            from clens.search import search_images

            search_images(str(args.search_text))
        case _:
            parser.print_help()
