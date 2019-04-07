import re

import thai_segmenter.sentence_segmenter
from thai_segmenter import viterbi as vtb
from thai_segmenter.sentence import sentence as sentence_cls

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
    if require_source_at_end and not line.rstrip().endswith("></source>"):
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


__segmenter = None


def get_segmenter():
    segmenter = thai_segmenter.sentence_segmenter.sentence_segmenter()
    # TODO: maybe set in sentence_segmenter class
    # segmenter.sentence = thai_segmenter.sentence_segmenter.sentence
    # segmenter.vtb = thai_segmenter.sentence_segmenter.vtb

    return segmenter


def _get_segmenter_default(segmenter=None):
    global __segmenter

    if segmenter is not None:
        return segmenter

    if __segmenter is None:
        __segmenter = get_segmenter()

    return __segmenter


# ------------------------------------


def sentence_segment(sentence, segmenter=None):
    segmenter = _get_segmenter_default(segmenter)

    return segmenter.sentence_segment(sentence)


def tokenize(sentence, segmenter=None):
    segmenter = _get_segmenter_default(segmenter)

    words = segmenter.wp.word_segment_words(sentence)
    words_escd = segmenter.wp.clean_special_characters(words)
    _, tokens, _ = segmenter.clean_unknown_word(words_escd)
    return tokens


def tokenize_and_postag(sentence, segmenter, tri_gram=False):
    segmenter = _get_segmenter_default(segmenter)

    # tokenize
    words = segmenter.wp.word_segment_words(sentence)
    words_escd = segmenter.wp.clean_special_characters(words)
    to_be_tagged, tokens, replace_idx = segmenter.clean_unknown_word(words_escd)

    # pos tag
    # call viterbi function to get most possible pos sequence
    initp, trans, emiss = segmenter.corpus.get_statistics_model(tri_gram)
    if tri_gram:
        path = vtb.viterbi_trigram(
            to_be_tagged, segmenter.corpus.pos_list_sentence, initp, trans, emiss
        )
    else:
        path = vtb.viterbi(
            to_be_tagged, segmenter.corpus.pos_list_sentence, initp, trans, emiss
        )
    pos = segmenter.invert_unknown_word(tokens, path, replace_idx)

    # make sentence object
    tokens_and_pos = list((w, p if p != "SBS" else "NSBS") for w, p in zip(tokens, pos))
    return sentence_cls(sentence, tokens_and_pos)


# ----------------------------------------------------------------------------


def line_cleaner(
    lines,
    skip_headers=True,
    filter_blank=True,
    filter_non_thai=True,
    norm_whitespaces=True,
    summary=None,
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


def line_sentence_segmenter(
    lines, has_headers=False, header_detect_fun=None, summary=None
):
    segmenter = get_segmenter()

    if not callable(header_detect_fun):
        header_detect_fun = is_head_line

    num_lines = num_headers = num_segmented = num_sentences = 0

    for line in lines:
        num_lines += 1
        line = line.strip()

        if not line:
            continue

        if has_headers and header_detect_fun(line):
            num_headers += 1
            yield line
            continue

        # sentence segment
        sentences = sentence_segment(line, segmenter)
        if len(sentences) > 1:
            num_segmented += 1
        num_sentences += len(sentences)

        for sentence in sentences:
            yield str(sentence)

    if isinstance(summary, dict):
        summary["lines"] = num_lines
        summary["headers"] = num_headers
        summary["sentences"] = num_sentences
        summary["segmented"] = num_segmented


def line_sentence_segmenter_column(
    lines, column=None, has_headers=False, header_detect_fun=None, summary=None
):
    segmenter = get_segmenter()

    if not callable(header_detect_fun):
        header_detect_fun = is_head_line

    num_lines = num_headers = num_segmented = num_sentences = 0

    for line in lines:
        num_lines += 1
        line = line.strip()

        if not line:
            continue

        if has_headers and header_detect_fun(line):
            num_headers += 1
            yield line
            continue

        if column is not None:
            # TODO: how often to split
            parts = line.split("\t")
            pre_parts = [p for i, p in enumerate(parts) if i < column]
            main_part = parts[column]
            post_parts = [p for i, p in enumerate(parts) if i > column]
        else:
            pre_parts, post_parts = list(), list()
            main_part = line

        # sentence segment
        sentences = sentence_segment(main_part, segmenter)
        if len(sentences) > 1:
            num_segmented += 1
        num_sentences += len(sentences)

        for sentence in sentences:
            parts = pre_parts + [str(sentence)] + post_parts
            line_out = "\t".join(parts)

            yield line_out

    if isinstance(summary, dict):
        summary["lines"] = num_lines
        summary["headers"] = num_headers
        summary["sentences"] = num_sentences
        summary["segmented"] = num_segmented


def line_tokenizer(
    lines, column=None, has_headers=False, header_detect_fun=None, summary=None
):
    segmenter = get_segmenter()

    if not callable(header_detect_fun):
        header_detect_fun = is_head_line

    num_lines = num_headers = num_sentences = num_tokens = 0

    for line in lines:
        num_lines += 1
        line = line.strip()

        if not line:
            continue

        if has_headers and header_detect_fun(line):
            num_headers += 1
            yield line
            continue

        if column is not None:
            # TODO: how often to split
            parts = line.split("\t")
            pre_parts = [p for i, p in enumerate(parts) if i < column]
            main_part = parts[column]
            post_parts = [p for i, p in enumerate(parts) if i > column]
        else:
            pre_parts, post_parts = list(), list()
            main_part = line

        # tokenize
        tokens = tokenize(main_part, segmenter)

        num_sentences += 1
        num_tokens += len(tokens)

        sentence_tok = " ".join(tokens)
        parts = pre_parts + [sentence_tok] + post_parts
        line_out = "\t".join(parts)

        yield line_out

    if isinstance(summary, dict):
        summary["lines"] = num_lines
        summary["headers"] = num_headers
        summary["sentences"] = num_sentences
        summary["tokens"] = num_tokens


def line_tokenize_and_tagger(
    lines, column=None, has_headers=False, header_detect_fun=None, summary=None
):
    segmenter = get_segmenter()

    if not callable(header_detect_fun):
        header_detect_fun = is_head_line

    num_lines = num_headers = num_sentences = num_tokens = 0

    for line in lines:
        num_lines += 1
        line = line.strip()

        if not line:
            continue

        if has_headers and header_detect_fun(line):
            num_headers += 1
            yield line
            continue

        if column is not None:
            # TODO: how often to split
            parts = line.split("\t")
            pre_parts = [p for i, p in enumerate(parts) if i < column]
            main_part = parts[column]
            post_parts = [p for i, p in enumerate(parts) if i > column]
        else:
            pre_parts, post_parts = list(), list()
            main_part = line

        # tokenize and pos-tag
        sentence = tokenize_and_postag(main_part, segmenter)

        num_sentences += 1
        num_tokens += len(sentence.pos)

        sentence_tagged = " ".join("{}|{}".format(w, p) for w, p in sentence.pos)
        parts = pre_parts + [sentence_tagged] + post_parts
        line_out = "\t".join(parts)

        yield line_out

    if isinstance(summary, dict):
        summary["lines"] = num_lines
        summary["headers"] = num_headers
        summary["sentences"] = num_sentences
        summary["tokens"] = num_tokens


# ----------------------------------------------------------------------------
