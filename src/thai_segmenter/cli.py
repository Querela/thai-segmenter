"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mthai_segmenter` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``thai_segmenter.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``thai_segmenter.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import argparse
import sys


def run_clean(args):
    pass


def run_sentence_segmentation(args):
    pass


def run_tokenize(args):
    pass


def run_tokenize_postag(args):
    pass


# ----------------------------------------------------------------------------


def build_parser():
    # - shared arguments
    shared_inout_parser = argparse.ArgumentParser(add_help=False)
    group = shared_inout_parser.add_argument_group("In-/Output")
    group.add_argument(
        "-i",
        "--input",
        type=argparse.FileType("r", encoding="utf-8"),
        default=sys.stdin,
        help="Input file.",
    )
    group.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w", encoding="utf-8"),
        default=sys.stdout,
        help="Output file.",
    )

    # ------------------------------------
    # - add sub commands

    parser = argparse.ArgumentParser(description="Thai Segmentation utilities.")
    subparsers = parser.add_subparsers(title="Tasks", dest="task")

    parser_clean = subparsers.add_parser(
        "clean",
        help="Clean input from non-thai and blank lines.",
        parents=[shared_inout_parser],
    )
    parser_sentseg = subparsers.add_parser(
        "sentseg",
        help="Sentence segmentize input lines.",
        parents=[shared_inout_parser],
    )
    parser_tokenize = subparsers.add_parser(
        "tokenize", help="Tokenize input lines.", parents=[shared_inout_parser]
    )
    parser_tokpos = subparsers.add_parser(
        "tokpos",
        help="Tokenize and POS-tag input lines.",
        parents=[shared_inout_parser],
    )

    # ------------------------------------
    # - clean command arguments

    parser_clean.add_argument(
        "--keep-blanks",
        action="store_false",
        dest="filter_blank",
        help="Don't filter blank/empty lines.",
    )
    parser_clean.add_argument(
        "--keep-non-thai",
        action="store_false",
        dest="filter_non_thai",
        help="Keep lines not containing thai characters.",
    )
    parser_clean.add_argument(
        "--no-trim-whitespaces",
        action="store_false",
        dest="trim_whitespaces",
        help="Don't trim whitespaces at start/end of line.",
    )
    parser_clean.add_argument(
        "--no-normalize-whitespaces",
        action="store_false",
        dest="normalize_whitespaces",
        help="Don't convert all whitespaces to a blank char and fold multiple whitespaces together.",
    )

    # ------------------------------------

    parser_sentseg.add_argument("--foo", help="WIP")

    # ------------------------------------

    parser_tokenize.add_argument("--foo", help="WIP")

    # ------------------------------------

    parser_tokpos.add_argument("--foo", help="WIP")

    # ------------------------------------

    return parser


def main(args=None):
    parser = build_parser()
    args = parser.parse_args(args=args)
    print("Run task: {}".format(args.task))

    print(args)

    if args.task == "clean":
        run_clean(args)
    elif args.task == "sentseg":
        run_sentence_segmentation(args)
    elif args.task == "tokenize":
        run_tokenize(args)
    elif args.task == "tokpos":
        run_tokenize_postag(args)
