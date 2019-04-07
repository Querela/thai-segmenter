from __future__ import print_function

import codecs
import os
import sys  # noqa: F401
import time  # noqa: F401

from thai_segmenter import orchid_corpus as orch
from thai_segmenter import sentence as sentence
from thai_segmenter import viterbi as vtb
from thai_segmenter import word_processing as wp


class sentence_segmenter:
    data_dir = "tools"
    filename_lexitron = "lexitron_original.txt"
    filename_dictionary = "custom_dict_word.txt"
    filename_orchid = "orchid_words.txt"

    def __init__(self, corpus=None, custom_dict=dict()):
        if corpus is None:
            corpus = orch.orchid_corpus()
        self.corpus = corpus

        self.custom_dict = custom_dict
        if custom_dict is not None:
            self.set_custom_dict(custom_dict)
        else:
            self.dict_name = sentence_segmenter.filename_lexitron

        self.wp = wp.word_processing(self.dict_name, sentence_segmenter.filename_orchid)

    def set_custom_dict(self, custom_dict):
        word_list = set()
        filename = os.path.join(
            os.path.dirname(__file__),
            sentence_segmenter.data_dir,
            sentence_segmenter.filename_lexitron,
        )
        with codecs.open(filename, "r", encoding="utf-8") as f:
            for line in f:
                word_list.add(line.strip())
        for word in custom_dict:
            word_list.add(word)

        filename = os.path.join(
            os.path.dirname(__file__),
            sentence_segmenter.data_dir,
            sentence_segmenter.filename_dictionary,
        )
        with codecs.open(filename, "w", encoding="utf-8") as f:
            for word in word_list:
                f.write(word + "\n")
        self.dict_name = sentence_segmenter.filename_dictionary

    def clean_unknown_word(self, sentence):
        new_word_list = list()
        to_be_tagged = list()
        replace_idx = list()
        last_idx = -1

        for word in sentence:
            if word in self.custom_dict and self.custom_dict[word]["pos"] is not None:
                new_word_list.append(word)
                to_be_tagged.append("_" + self.custom_dict[word]["pos"])
            elif not self.corpus.exists(word):
                subwords = self.wp.word_segment_subwords(word)
                valid_first = True
                valid_all = True

                for i in range(len(subwords)):
                    if not self.corpus.exists(subwords[i]):
                        if i == 0:
                            valid_first = False
                        valid_all = False
                        break

                if valid_all:  # don't split this word if it exists in custom dict
                    new_word_list.extend(subwords)
                    to_be_tagged.extend(subwords)
                elif valid_first:
                    new_word_list.append(word)
                    to_be_tagged.append(subwords[0])
                else:
                    new_word_list.append(word)
                    to_be_tagged.append("_NCMN")

            else:
                new_word_list.append(word)
                to_be_tagged.append(word)

            replace_idx.append((last_idx + 1, len(to_be_tagged) - 1))
            last_idx = len(to_be_tagged) - 1

        return to_be_tagged, new_word_list, replace_idx

    def invert_unknown_word(self, broken_words, pos, reverse_idx):
        new_pos = []
        noun_tag = ["NPRP", "NCNM", "NONM", "NLBL", "NCMN", "NTTL"]
        count = 0

        for idx in reverse_idx:
            start, end = idx[0], idx[1]
            original_word = "".join(broken_words[start:(end + 1)])
            if (
                original_word in self.custom_dict
                and self.custom_dict[original_word]["pos"] is not None
            ):
                new_pos.append(self.custom_dict[original_word]["pos"])
            elif start != end:
                # print(original_word)
                noun_count = 0
                for j in range(start, end + 1):
                    if pos[j] in noun_tag:
                        noun_count += 1
                if noun_count > 0:
                    new_pos.append("NPRP")  # proper noun
                else:
                    new_pos.append(pos[start])  # use same pos with the first word
            else:
                new_pos.append(pos[start])
            count += 1

        return new_pos

    def cut_sentence(self, paragraph, pos):
        sentences = []
        sen_with_pos = []

        tmp_sentence = ""
        tmp_list = []

        for i in range(len(paragraph)):
            if pos[i] == "SBS":
                sentences.append(tmp_sentence)
                sen_with_pos.append(tmp_list)
                tmp_sentence = ""
                tmp_list = []
            else:
                tmp_sentence += paragraph[i]
                tmp_list.append((paragraph[i], pos[i]))

        if len(tmp_list) > 0:
            sentences.append(tmp_sentence)
            sen_with_pos.append(tmp_list)

        return sentences, sen_with_pos

    def merge_sentence(self, sentences, sen_with_pos):
        new_sentences = [sentences[0]]
        new_sen_with_pos = [sen_with_pos[0]]

        for i in range(1, len(sentences)):
            first_pos = sen_with_pos[i][0][1]
            last_word_len = len(new_sen_with_pos[-1])

            merge = False
            start_sentence, cut_idx = sentences[i], 0
            if first_pos == "JCRG" or first_pos == "JCMP":
                merge = True
            elif first_pos == "JSBR":
                if (
                    len(sen_with_pos[i]) + last_word_len < 50
                    or len(sen_with_pos[i]) < 10
                ):
                    merge = True
                elif len(sen_with_pos[i]) > 2:
                    # remove conjunction (with space, if any)
                    cut_idx = 1 if sen_with_pos[i][1][1] != "NSBS" else 2
            if merge:
                new_sentences[-1] += " " + sentences[i]
                new_sen_with_pos[-1].extend([(" ", "NSBS")])
                new_sen_with_pos[-1].extend(sen_with_pos[i])
            else:
                if cut_idx > 0:
                    start_sentence = "".join(
                        [word for (word, pos) in sen_with_pos[i][cut_idx:]]
                    )
                new_sentences.append(start_sentence)
                new_sen_with_pos.append(sen_with_pos[i][cut_idx:])

        return new_sentences, new_sen_with_pos

    def sentence_segment(self, paragraph, tri_gram=False):
        # time_start = time.time()
        # preprocess
        words = self.wp.word_segment_words(paragraph)
        # time_seg = time.time() - time_start
        tmp_paragraph = self.wp.clean_special_characters(words)
        to_be_tagged, new_paragraph, replace_idx = self.clean_unknown_word(
            tmp_paragraph
        )

        # call viterbi function to get most possible pos sequence
        initp, trans, emiss = self.corpus.get_statistics_model(tri_gram)

        if tri_gram:
            path = vtb.viterbi_trigram(
                to_be_tagged, self.corpus.pos_list_sentence, initp, trans, emiss
            )
        else:
            path = vtb.viterbi(
                to_be_tagged, self.corpus.pos_list_sentence, initp, trans, emiss
            )
            # for i in range(len(path)):
            #   print(to_be_tagged[i] + "\t\t" + path[i])

        # postprocess
        pos = self.invert_unknown_word(new_paragraph, path, replace_idx)
        sentences, sen_with_pos = self.cut_sentence(words, pos)
        merge_sen, merge_sen_with_pos = self.merge_sentence(sentences, sen_with_pos)

        # time_rest = time.time() - time_start - time_seg
        # print('java: {:.4f}, rest: {:.4f}'.format(time_seg, time_rest), file=sys.stderr)

        # return sentences, sen_with_pos
        # return merge_sen, merge_sen_with_pos
        # return [sentence.sentence(sentences[i], sen_with_pos[i]) for i in range(len(sentences))]
        return [
            sentence.sentence(merge_sen[i], merge_sen_with_pos[i])
            for i in range(len(merge_sen))
        ]

    def get_stats(self):
        return self.initp, self.trans_bi, self.trans_tri, self.emiss
