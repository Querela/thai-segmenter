from collections import namedtuple
from functools import lru_cache
from pprint import pformat

# ----------------------------------------------------------------------------


class SentenceSegmenter(object):
    def __init__(self, app=None, config=None):
        if not (config is None or isinstance(config, dict)):
            raise ValueError("`config` must be an instance of dict or None")
        self.config = config
        self.app = app
        self._ss = None
        if app is not None:
            self.init_app(app, config)

    def init_app(self, app, config=None):
        if not (config is None or isinstance(config, dict)):
            raise ValueError("`config` must be an instance of dict or None")
        base_config = app.config.copy()
        if self.config:
            base_config.update(self.config)
        if config:
            base_config.update(config)

        self.config = base_config
        self.app = app

        self.init_segmenter()

    def init_segmenter(self):
        self.app.logger.debug("Init sentence segmenter")
        import thai_segmenter.sentence_segmenter as _ss

        self._ss = _ss.sentence_segmenter()  # get segmenter class instance
        self._ss.sentence = _ss.sentence  # add module as reference
        self._ss.vtb = _ss.vtb  # add module as reference
        self.app.logger.debug("Sentence segmenter inited.")

    def segment(self, line, *args, **kwargs):
        if not self._ss:
            return line
        else:
            return self._ss.sentence_segment(line, *args, **kwargs)

    @lru_cache(maxsize=200)
    def do_segmentation(self, paragraph, tri_gram=False):
        words = self._ss.wp.word_segment_words(paragraph)
        tmp_paragraph = self._ss.wp.clean_special_characters(words)
        to_be_tagged, new_paragraph, replace_idx = self._ss.clean_unknown_word(
            tmp_paragraph
        )
        initp, trans, emiss = self._ss.corpus.get_statistics_model(tri_gram)
        if tri_gram:
            path = self._ss.vtb.viterbi_trigram(
                to_be_tagged, self._ss.corpus.pos_list_sentence, initp, trans, emiss
            )
        else:
            path = self._ss.vtb.viterbi(
                to_be_tagged, self._ss.corpus.pos_list_sentence, initp, trans, emiss
            )
        pos = self._ss.invert_unknown_word(new_paragraph, path, replace_idx)
        sentences, sen_with_pos = self._ss.cut_sentence(words, pos)
        # sen_with_pos: List[List[Tuple[str, str]]] -> List1: sentences, List2: pos in sentence

        pos = list(
            map(POSInfo._make, zip(words, pos, (None,) * len(pos), (None,) * len(pos)))
        )
        paragraph = self._ss.sentence.sentence(paragraph, pos)

        # update frag_nr in paragraph pos
        cut_sentences = list()
        offset = 0
        for fn, (sentence, sen_pos) in enumerate(zip(sentences, sen_with_pos)):
            # for all sentences
            cut_sentence = self._ss.sentence.sentence(sentence, sen_pos)
            cut_sentences.append(cut_sentence)

            # print('frag pos', sen_pos[0][0], [p[1] for p in sen_pos])
            for r in range(len(pos) - offset):
                # print('all pos ', pos[offset + r][0], [p[1] for p in pos[offset + r:offset + r + len(sen_pos)]])
                # find matching offset in global pos sequence
                check_sequence_ok = True
                for c, csp in enumerate(sen_pos):
                    # check whole fragment sequence if matches at current position
                    check_cur_pos = pos[offset + r + c]
                    if check_cur_pos[1] != csp[1] or check_cur_pos[0] != csp[0]:
                        check_sequence_ok = False
                        break
                if check_sequence_ok:
                    offset = offset + r
                    break

            for i in range(len(sen_pos)):
                # for all pos in fragment - update frag_nr
                pos[offset + i] = pos[offset + i]._replace(frag_nr=fn)
            offset = offset + len(sen_pos)

        merge_sen, merge_sen_with_pos = self._ss.merge_sentence(sentences, sen_with_pos)

        # update sent_nr in paragraph pos
        segmented_sentences = list()
        offset = 0
        for sn in range(len(merge_sen)):
            segmented_sentence = self._ss.sentence.sentence(
                merge_sen[sn], merge_sen_with_pos[sn]
            )
            segmented_sentences.append(segmented_sentence)

            # print('-' * 60)
            # print('sent pos', sn, merge_sen_with_pos[sn][0][0], [p[1] for p in merge_sen_with_pos[sn]])
            for r in range(len(pos) - offset):
                # print('all pos ', sn, pos[offset + r][0], [p[1] for p in pos[offset + r:offset + r + len(merge_sen_with_pos[sn])]])
                check_sequence_ok = True
                for c, csp in enumerate(merge_sen_with_pos[sn]):
                    # check whole sentence sequence if matches at current position
                    check_cur_pos = pos[offset + r + c]
                    if check_cur_pos[1] != csp[1] or check_cur_pos[0] != csp[0]:
                        if check_cur_pos[1] == "SBS" and csp[1] == "NSBS":
                            continue
                        check_sequence_ok = False
                        break
                if check_sequence_ok:
                    offset = offset + r
                    break

            for i in range(len(merge_sen_with_pos[sn])):
                # for all pos in sentences - update sent_nr
                pos[offset + i] = pos[offset + i]._replace(sent_nr=sn)
            offset = offset + len(merge_sen_with_pos[sn])

        return paragraph, cut_sentences, segmented_sentences


POSInfo = namedtuple("POSInfo", "word pos frag_nr sent_nr".split())


# ----------------------------------------------------------------------------


def make_tree_pos_info(pos):
    if not pos:
        return [], []

    # def p2p(ppos):
    #     return [(p[1], p[2], p[3]) for p in ppos]

    def consume_frag(i, pos):
        cur_list = list()
        first_sent_nr = pos[i].sent_nr if i < len(pos) else None
        while i < len(pos):
            p = pos[i]
            if p.sent_nr is None or p.frag_nr is None:
                break
            if p.sent_nr != first_sent_nr:
                break
            cur_list.append(p)
            i += 1
        return i, cur_list, first_sent_nr

    def consume_sent_sep(i, pos):
        cur_list = list()
        while i < len(pos):
            p = pos[i]
            if p.sent_nr is not None or p.frag_nr is not None:
                break
            cur_list.append(p)
            i += 1
        return i, cur_list

    def consume_frag_sep(i, pos):
        cur_list = list()
        while i < len(pos):
            p = pos[i]
            if p.frag_nr is not None:
                break
            cur_list.append(p)
            i += 1
        return i, cur_list

    def consume_frag_konj(i, pos):
        cur_list = list()
        while i < len(pos):
            p = pos[i]
            if p.sent_nr is not None:
                break
            if p.sent_nr is None and p.frag_nr is None:
                break
            cur_list.append(p)
            i += 1
        return i, cur_list

    ret = list()
    tree, tree_line, tree_line_type, last_sent_nr = list(), list(), None, None
    i = 0
    while i < len(pos):
        p = pos[i]
        if p.sent_nr is not None and p.frag_nr is not None:
            new_i, cur_list, cur_sent_nr = consume_frag(i, pos)
            # app.logger.debug('frag @%s--%s sn:%s : %s', i, new_i, cur_sent_nr, p2p(cur_list))
            if new_i != i:
                i = new_i
                ret.append(("frag", cur_list))
                if tree_line_type != "sentence" and tree_line_type is not None:
                    tree.append((tree_line_type, tree_line))
                    tree_line = list()
                if tree_line_type == "sentence" and last_sent_nr != cur_sent_nr:
                    tree.append((tree_line_type, tree_line))
                    last_sent_nr = cur_sent_nr
                    tree_line = list()
                tree_line_type = "sentence"
                # tree_line.append(cur_list)
                tree_line.append(ret[-1])
                continue
        if p.sent_nr is not None and p.frag_nr is None:
            new_i, cur_list = consume_frag_konj(i, pos)
            # app.logger.debug('frag_sep @%s--%s : %s', i, new_i, p2p(cur_list))
            if new_i != i:
                i = new_i
                ret.append(("frag_sep", cur_list))
                if tree_line_type != "sentence":
                    tree.append((tree_line_type, tree_line))
                    tree_line = list()
                    tree_line_type = "sentence"
                # tree_line.append(cur_list)
                tree_line.append(ret[-1])
                last_sent_nr = pos[i].sent_nr if i < len(pos) else None
                continue
        if p.sent_nr is not None and p.frag_nr is None:
            new_i, cur_list = consume_frag_sep(i, pos)
            # app.logger.debug('sent_sep(2) @%s--%s : %s', i, new_i, p2p(cur_list))
            if new_i != i:
                i = new_i
                ret.append(("frag_sep", cur_list))
                if tree_line_type != "sentence":
                    tree.append((tree_line_type, tree_line))
                    tree_line = list()
                    tree_line_type = "sentence"
                # tree_line.append(cur_list)
                tree_line.append(ret[-1])
                last_sent_nr = pos[i].sent_nr if i < len(pos) else None
                continue
        if p.sent_nr is None and p.frag_nr is None:
            new_i, cur_list = consume_sent_sep(i, pos)
            # app.logger.debug('sent_sep @%s--%s : %s', i, new_i, p2p(cur_list))
            if new_i != i:
                i = new_i
                ret.append(("sent_sep", cur_list))
                if tree_line_type == "sentence":
                    tree.append((tree_line_type, tree_line))
                    tree_line = list()
                    tree_line_type = "separator"
                # tree_line.append(cur_list)
                tree_line.append(ret[-1])
                last_sent_nr = pos[i].sent_nr if i < len(pos) else None
                continue
        if p.sent_nr is None and p.frag_nr is not None:
            new_i, cur_list = consume_frag_konj(i, pos)
            # app.logger.debug('frag_konj @%s--%s : %s', i, new_i, p2p(cur_list))
            if new_i != i:
                i = new_i
                ret.append(("frag_konj?", cur_list))
                if tree_line_type != "separator":
                    tree.append((tree_line_type, tree_line))
                    tree_line = list()
                    tree_line_type = "separator"
                # tree_line.append(cur_list)
                tree_line.append(ret[-1])
                last_sent_nr = pos[i].sent_nr if i < len(pos) else None
                continue

        break

    if tree_line:
        tree.append((tree_line_type, tree_line))

    return ret, tree


def dump_tree_pos_info(logger, ret, tree):
    ret = [
        (r[0], {(x[2], x[3]) for x in r[1]}) for r in ret
    ]  # , '.'.join([x[1] for x in r[1]])
    for i in range(len(tree)):
        tree[i] = (
            tree[i][0],
            [(t[0], {(x[2], x[3]) for x in t[1]}) for t in tree[i][1]],
        )

    logger.debug("Parts: %s", pformat(ret))
    logger.debug("Structured tree: %s", pformat(tree))


def make_tree_for_output(tree):
    out = list()

    for i in range(len(tree)):
        if tree[i][0] == "sentence":
            sent = [(t[0], [(x[0], x[1]) for x in t[1]]) for t in tree[i][1]]
            out.append(("sent", sent))
        else:
            sep = [(t[0], [(x[0], x[1]) for x in t[1]]) for t in tree[i][1]]
            out.append(("sep", sep))

    return out
