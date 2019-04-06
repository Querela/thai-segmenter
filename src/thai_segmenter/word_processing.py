from __future__ import print_function

import codecs
import os
import os.path
import shutil
import subprocess
import sys  # noqa: F401
import threading
import time

from thai_segmenter import longlexto


class word_processing:
    filename_lexitron = "lexitron.txt"
    filename_lexitron_orig = "lexitron_original.txt"

    def __init__(self, dict_file_paragraph, dict_file_words):
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        self.dict_dir = os.path.join(self.cwd, "tools")

        dict_file = os.path.join(self.dict_dir, word_processing.filename_lexitron)

        shutil.copyfile(os.path.join(self.dict_dir, dict_file_paragraph), dict_file)
        self.tokenizer_words = longlexto.LongLexTo.create(dict_file=dict_file)

        shutil.copyfile(os.path.join(self.dict_dir, dict_file_words), dict_file)
        self.tokenizer_subwords = longlexto.LongLexTo.create(dict_file=dict_file)

        self.special = {
            " ": "<space>",
            "-": "<minus>",
            "_": "<underscore>",
            "(": "<left_parenthesis>",
            ")": "<right_parenthesis>",
            "[": "<left_bracket>",
            "]": "<right_bracket>",
            "*": "<asterisk>",
            ".": "<full_stop>",
            '"': "<quotation>",
            "/": "<slash>",
            ":": "<colon>",
            "=": "<equal>",
            ",": "<comma>",
            ";": "<semi_colon>",
            "<": "<less_than>",
            ">": "<greater_than>",
            "&": "<ampersand>",
            "{": "<left_curly_bracket>",
            "|": "<pipe>",
            "}": "<right_curly_bracket>",
            "'": "<apostrophe>",
            "+": "<plus>",
            "?": "<question_mark>",
            "!": "<exclamation>",
            "$": "<dollar>",
            "%": "<percent>",
        }

    def word_segment(self, sentence, dict_filename=None):
        if dict_filename is None:
            dict_filename = word_processing.filename_lexitron_orig
        # dict file
        dict_file = os.path.join(self.dict_dir, word_processing.filename_lexitron)
        # if os.path.exists(dict_file):
        #     try:
        #         os.remove(dict_file)
        #     except Exception as ex:
        #         print('Ex: {}'.format(ex), file=sys.stderr)
        shutil.copyfile(os.path.join(self.dict_dir, dict_filename), dict_file)

        sent_name = (
            "tmp_sentence_"
            + str(int(time.time()))
            + "_"
            + str(threading.current_thread().ident)
        )
        sent_file = os.path.join(self.dict_dir, sent_name)
        try:
            with codecs.open(sent_file, "w", encoding="utf-8") as f:
                f.write(sentence)

            cmd = list()
            # cmd.extend(['DRIP_SHUTDOWN=30', 'drip'])
            # cmd.append('drip')
            cmd.append("java")
            cmd.extend(["-Xms128M", "-Xmx256M"])
            cmd.append("-Xss10M")
            cmd.append("LongLexTo")
            cmd.append(sent_name)
            # print(cmd)
            proc = subprocess.Popen(cmd, cwd=self.dict_dir, stdout=subprocess.PIPE)

            results = proc.stdout.read()
            uni_results = results.decode("utf-8").strip()
            words = uni_results.split("\n")
        finally:
            os.remove(sent_file)

        # for word in words:
        #   print(word, end=" / ")
        # print("\n=====================")

        # tokenizer = longlexto.LongLexTo.create(dict_file=dict_file)
        # words = list(tokenizer.get_words(sentence))
        # print(sentence, words)

        return words

    def word_segment_words(self, sentence):
        return list(self.tokenizer_words.get_words(sentence))

    def word_segment_subwords(self, word):
        return list(self.tokenizer_subwords.get_words(word))

    def clean_special_characters(self, st):
        sentence = [word for word in st]

        for i, word in enumerate(sentence):
            if word in self.special:
                sentence[i] = self.special[word]

        return sentence
