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


# from thai-word-segmentation repo
THAI_CHARS = [  # noqa: F841
    chr(x)
    for x in list(range(0x0E01, 0x0E3A))
    + list(range(0x0E3F, 0x0E4D))
    + list(range(0x0E50, 0x0E5A))
]
# https://www.compart.com/de/unicode/scripts/Thai
THAI_CHARS2 = [  # noqa: F841
    chr(x) for x in list(range(0x0E01, 0x0E3B)) + list(range(0x0E40, 0x0E5C))
]
ASCII_CHARS = [
    chr(x) for x in [0] + [0x000A] + list(range(0x0020, 0x007F))
]  # noqa: F841


def contains_thai(line):  # type: (str) -> bool
    """Checks whether a line contains at least one thai character."""
    return any(c in THAI_CHARS2 for c in line)


def is_head_line(
    line, require_source_at_end=False, require_all_meta=False
):  # type: (str) -> bool
    """Check whether a line is a source document separator."""
    if require_source_at_end and not line.strip().endswith("></source>"):
        return False

    if require_all_meta:
        return (
            line.startswith("<source><")
            and "</source>" in line
            and ("<date>" in line or "<datum>" in line)
            and ("<location>" in line or "<name_lang>" in line)
        )

    return line.startswith("<source><")


# ----------------------------------------------------------------------------


def run_clean(args):
    skip_headers = args.has_source_headers
    filter_blank = args.filter_blank
    filter_non_thai = args.filter_non_thai
    trim_whitespaces = args.trim_whitespaces
    norm_whitespaces = args.normalize_whitespaces
    infile, outfile = args.input, args.output

    # TODO: output stats if cmd param?

    import re

    pattern_anywhitespace = re.compile(r"\s+")

    for line in infile:
        if skip_headers and is_head_line(line):
            # if we check for headers, then output if found and continue
            outfile.write(line)
            continue

        line_strip = line.strip()

        if not line_strip:
            if not filter_blank:
                outfile.write(line_strip + "\n")
            continue

        if filter_non_thai and not contains_thai(line_strip):
            # skip if filtering and no thai in line
            continue

        if trim_whitespaces:
            line = line_strip

        if norm_whitespaces:
            line = pattern_anywhitespace.sub(" ", line_strip)

        outfile.write(line + "\n")


def run_sentence_segmentation(args):
    from thai_segmenter import sentence_segment  # noqa: F401


def run_tokenize(args):
    from thai_segmenter import sentence_segment  # noqa: F401


def run_tokenize_postag(args):
    from thai_segmenter import sentence_segment  # noqa: F401


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
        "--no-trim-whitespaces",
        action="store_false",
        dest="trim_whitespaces",
        help="Don't trim whitespaces at start/end of line.",
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
