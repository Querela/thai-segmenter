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

from thai_segmenter.tasks import line_cleaner
from thai_segmenter.tasks import line_sentence_segmenter
from thai_segmenter.tasks import line_tokenize_and_tagger
from thai_segmenter.tasks import line_tokenizer

# ----------------------------------------------------------------------------


def run_clean(args):
    infile, outfile = args.input, args.output

    summary = dict() if args.collect_stats else None

    for line in line_cleaner(
        infile,
        skip_headers=args.has_source_headers,
        filter_blank=args.filter_blank,
        filter_non_thai=args.filter_non_thai,
        norm_whitespaces=args.normalize_whitespaces,
        summary=summary,
    ):
        outfile.write(line + "\n")

    if args.collect_stats:
        print(summary, file=sys.stderr)


def run_sentence_segmentation(args):
    infile, outfile = args.input, args.output

    summary = dict() if args.collect_stats else None

    for line in line_sentence_segmenter(infile, summary=summary):
        outfile.write(line + "\n")

    if args.collect_stats:
        print(summary, file=sys.stderr)


def run_tokenize(args):
    infile, outfile = args.input, args.output

    summary = dict() if args.collect_stats else None

    for line in line_tokenizer(
        infile,
        escape_special=args.escape_special,
        tokenize_subwords=args.subwords,
        column=args.column,
        summary=summary,
    ):
        outfile.write(line + "\n")

    if args.collect_stats:
        print(summary, file=sys.stderr)


def run_tokenize_postag(args):
    infile, outfile = args.input, args.output

    summary = dict() if args.collect_stats else None

    for line in line_tokenize_and_tagger(infile, column=args.column, summary=summary):
        outfile.write(line + "\n")

    if args.collect_stats:
        print(summary, file=sys.stderr)


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

    shared_stats_parser = argparse.ArgumentParser(add_help=False)
    group = shared_stats_parser.add_argument_group("In-/Output")
    group.add_argument(
        "--stats",
        action="store_true",
        dest="collect_stats",
        help="Collect statistics (counters) and print to stderr at end.",
    )

    shared_colselect_parser = argparse.ArgumentParser(add_help=False)
    group = shared_colselect_parser.add_argument_group("Selection")
    group.add_argument(
        "-c",
        "-f",
        "--column",
        "--field",
        type=int,
        dest="column",
        default=None,
        help="If supplied, then only do task on nth column of tab separated file. (1 == first column)",
    )

    # ------------------------------------
    # - add sub commands

    parser = argparse.ArgumentParser(description="Thai Segmentation utilities.")
    subparsers = parser.add_subparsers(title="Tasks", dest="task")

    parser_clean = subparsers.add_parser(
        "clean",
        help="Clean input from non-thai and blank lines.",
        parents=[shared_inout_parser, shared_stats_parser],
    )
    parser_sentseg = subparsers.add_parser(
        "sentseg",
        help="Sentence segmentize input lines.",
        parents=[shared_inout_parser, shared_stats_parser],
    )
    parser_tokenize = subparsers.add_parser(
        "tokenize",
        help="Tokenize input lines.",
        parents=[shared_inout_parser, shared_stats_parser, shared_colselect_parser],
    )
    parser_tokpos = subparsers.add_parser(
        "tokpos",
        help="Tokenize and POS-tag input lines.",
        parents=[shared_inout_parser, shared_stats_parser, shared_colselect_parser],
    )

    # ------------------------------------
    # - clean command arguments

    group = parser_clean.add_argument_group("Transformations")
    group.add_argument(
        "--keep-blanks",
        action="store_false",
        dest="filter_blank",
        help="Don't filter blank/empty lines.",
    )
    group.add_argument(
        "--keep-non-thai",
        action="store_false",
        dest="filter_non_thai",
        help="Keep lines not containing any thai characters.",
    )
    group.add_argument(
        "--no-source-headers",
        action="store_false",
        dest="has_source_headers",
        help="File has no source headers (else skip lines starting with '<source>').",
    )
    group.add_argument(
        "--no-normalize-whitespaces",
        action="store_false",
        dest="normalize_whitespaces",
        help="Don't convert all whitespaces to a blank char and fold multiple whitespaces together.",
    )

    # ------------------------------------

    parser_sentseg.add_argument("--foo", help="WIP")

    # ------------------------------------

    group = parser_tokenize.add_argument_group("Transformations")
    group.add_argument(
        "--escape-special",
        action="store_true",
        dest="escape_special",
        help="Escape special tokens with angle brackets.",
    )
    group.add_argument(
        "--subwords",
        action="store_true",
        dest="subwords",
        help="Tokenize entities(?) (names etc.) into subwords.",
    )

    # ------------------------------------

    parser_tokpos.add_argument("--foo", help="WIP")

    # ------------------------------------

    return parser


def main(args=None):
    parser = build_parser()
    args = parser.parse_args(args=args)
    print("Run task: {}".format(args.task))

    print(args)

    if args.task in ("tokenize", "tokpos"):
        if isinstance(args.column, int):
            if args.column < 1:
                raise parser.error(
                    "Column must be at least 1 or larger. (Counting starts at 1): value = {}".format(
                        args.column
                    )
                )
            # TODO: only till 3 ?

            args.column -= 1

    if args.task == "clean":
        run_clean(args)
    elif args.task == "sentseg":
        run_sentence_segmentation(args)
    elif args.task == "tokenize":
        run_tokenize(args)
    elif args.task == "tokpos":
        run_tokenize_postag(args)
