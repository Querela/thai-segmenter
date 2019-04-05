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
import re
import sys

# ----------------------------------------------------------------------------


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


def line_cleaner(
    lines, skip_headers, filter_blank, filter_non_thai, norm_whitespaces, summary=None
):
    pattern_anywhitespace = re.compile(r"\s+")

    num_lines = num_headers = num_blank = num_nonthai = num_keep = 0

    for line in lines:
        num_lines += 1
        line = line.strip()

        if skip_headers and is_head_line(line):
            num_headers += 1  # TODO: count even if not enabled?
            num_keep += 1
            # if we check for headers, then output if found and continue
            yield line
            continue

        if not line:
            if not filter_blank:
                num_blank += 1
                num_keep += 1
                yield line
            continue

        if filter_non_thai and not contains_thai(line):
            num_nonthai += 1
            # skip if filtering and no thai in line
            continue

        if norm_whitespaces:
            line = pattern_anywhitespace.sub(" ", line)

        num_keep += 1
        yield line

    # set summary at end
    if isinstance(summary, dict):
        summary["lines"] = num_lines
        summary["headers"] = num_headers
        summary["blank"] = num_blank
        summary["nonthai"] = num_nonthai
        summary["keep"] = num_keep


# ----------------------------------------------------------------------------


def run_clean(args):
    infile, outfile = args.input, args.output

    # TODO: output stats if cmd param?
    summary = dict() if args.collect_stats else None

    for line in line_cleaner(
        infile,
        args.has_source_headers,
        args.filter_blank,
        args.filter_non_thai,
        args.normalize_whitespaces,
        summary=summary,
    ):
        outfile.write(line + "\n")

    if args.collect_stats:
        print(summary, file=sys.stderr)


def run_sentence_segmentation(args):
    from thai_segmenter import sentence_segment  # noqa: F401

    segmenter = sentence_segment()

    infile, outfile = args.input, args.output

    num_lines = num_headers = num_sentences = num_segmented = 0

    for line in infile:
        num_lines += 1
        line = line.strip()

        if is_head_line(line):
            num_headers += 1
            outfile.write(line + "\n")
            continue

        # segment
        sentences = segmenter.sentence_segment(line)
        if len(sentences) > 1:
            num_segmented += 1
        num_sentences += len(sentences)

        for sentence in sentences:
            outfile.write(str(sentence) + "\n")

    if args.collect_stats:
        summary = dict(
            lines=num_lines,
            headers=num_headers,
            segmented=num_segmented,
            sentences=num_sentences,
        )
        print(summary, file=sys.stderr)


def run_tokenize(args):
    from thai_segmenter import sentence_segment  # noqa: F401

    segmenter = sentence_segment()

    infile, outfile = args.input, args.output
    column = args.column

    num_lines = num_headers = num_sentences = num_segmented = num_tokens = 0

    for line in infile:
        num_lines += 1
        line = line.strip()

        if is_head_line(line):
            num_headers += 1
            outfile.write(line + "\n")
            continue

        if column is not None:
            # TODO: how often to split
            parts = line.split("\t")
            pre_parts = [p for i, p in enumerate(parts) if i < column]
            main_part = parts[column]
            post_parts = [p for i, p in enumerate(parts) if i > column]

        # segment
        sentences = segmenter.sentence_segment(main_part)
        if len(sentences) > 1:
            num_segmented += 1
        num_sentences += len(sentences)

        for sentence in sentences:
            num_tokens += len(sentence.pos)
            sentence_tok = " ".join(w for w, _ in sentence.pos)

            parts = pre_parts + [sentence_tok] + post_parts
            line_out = "\t".join(parts) + "\n"

            outfile.write(line_out)

    if args.collect_stats:
        summary = dict(
            lines=num_lines,
            headers=num_headers,
            segmented=num_segmented,
            sentences=num_sentences,
            tokens=num_tokens,
        )
        print(summary, file=sys.stderr)


def run_tokenize_postag(args):
    from thai_segmenter import sentence_segment  # noqa: F401

    segmenter = sentence_segment()

    infile, outfile = args.input, args.output
    column = args.column

    num_lines = num_headers = num_sentences = num_segmented = num_tokens = 0

    for line in infile:
        num_lines += 1
        line = line.strip()

        if is_head_line(line):
            num_headers += 1
            outfile.write(line + "\n")
            continue

        if column is not None:
            # TODO: how often to split
            parts = line.split("\t")
            pre_parts = [p for i, p in enumerate(parts) if i < column]
            main_part = parts[column]
            post_parts = [p for i, p in enumerate(parts) if i > column]

        # segment
        sentences = segmenter.sentence_segment(main_part)
        if len(sentences) > 1:
            num_segmented += 1
        num_sentences += len(sentences)

        for sentence in sentences:
            num_tokens += len(sentence.pos)
            sentence_tagged = " ".join("{}|{}".format(w, p) for w, p in sentence.pos)

            parts = pre_parts + [sentence_tagged] + post_parts
            line_out = "\t".join(parts) + "\n"

            outfile.write(line_out)

    if args.collect_stats:
        summary = dict(
            lines=num_lines,
            headers=num_headers,
            segmented=num_segmented,
            sentences=num_sentences,
            tokens=num_tokens,
        )
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

    raise SystemExit("WIP")

    if args.task == "clean":
        run_clean(args)
    elif args.task == "sentseg":
        run_sentence_segmentation(args)
    elif args.task == "tokenize":
        run_tokenize(args)
    elif args.task == "tokpos":
        run_tokenize_postag(args)
