import ast
import os


class orchid_corpus:
    filename_orchid = "orchid97.txt"

    def __init__(self, file_name=None):
        if file_name is None:
            cwd = os.path.dirname(os.path.realpath(__file__))
            file_name = os.path.join(cwd, "tools", orchid_corpus.filename_orchid)
        self.orchid = file_name
        self.corpus = list()
        self.corpus_pos = list()
        self.corpus_sentence = list()
        self.read_from_corpus()

        # word and pos list
        self.word_list = set()
        self.pos_list = set()
        self.pos_list_sentence = set()
        self.get_word_pos_list()

        # for statistics model
        self.initp = dict()
        self.trans_bi = dict()
        self.trans_tri = dict()
        self.emiss = dict()
        self.calc_statistics()

    def read_from_corpus(self):
        with open(self.orchid, "r", encoding="utf-8") as corpus_file:
            corpus = corpus_file.readlines()

        state = "init"
        sentences = []
        words = []

        # read to corpus

        for line in corpus:
            line = line.strip()

            if state == "init":
                if line[0:7] == "%TTitle":
                    state = "book"
                elif line[0] == "#" and line[1] == "P":
                    state = "paragraph"
                elif line[0] == "#":
                    state = "sentence"

            elif state == "book":
                if line[0] == "#" and line[1] == "P":
                    state = "paragraph"

            elif state == "paragraph":
                if len(sentences) > 0:
                    self.corpus.append(sentences)
                sentences = []
                state = "sentence"

            elif state == "sentence":
                if "//" in line:
                    if line[0:2] == "%E":
                        state = "init"
                    else:
                        words = []
                        state = "word"
                elif line[0:2] == "%E":
                    state = "eng"

            elif state == "eng":
                if "//" in line:
                    state = "init"

            elif state == "word":
                if "//" in line:
                    state = "init"
                    sentences.append(words)
                else:
                    (word, pos) = line.split("/")
                    words.append((word, pos))

        # corpus_pos

        for paragraph in self.corpus:
            for sentence in paragraph:
                self.corpus_pos.append(sentence)

        # corpus_sentence
        # add tag <SBS> = Sentence Break Space and <NSBS> = Non Sentence Break Space

        for paragraph in self.corpus:
            p = []
            for i in range(len(paragraph)):
                for word in paragraph[i]:  # for each word in sentence
                    if word[0] == "<space>":
                        p.append(("<space>", "NSBS"))
                    else:
                        p.append(word)

                if i != len(paragraph) - 1:
                    p.append(("<space>", "SBS"))

            self.corpus_sentence.append(p)

    def get_word_pos_list(self):

        for paragraph in self.corpus:
            for sentence in paragraph:
                for word in sentence:
                    self.word_list.add(word[0])
                    self.pos_list.add(word[1])

        self.pos_list_sentence = self.pos_list.copy()
        self.pos_list_sentence.add("SBS")
        self.pos_list_sentence.add("NSBS")

    def calc_statistics(self):
        cp = self.corpus_sentence
        word_list = self.word_list
        pos_list = self.pos_list_sentence

        # initial probability
        for pos in pos_list:
            self.initp[pos] = 0

        for paragraph in cp:
            self.initp[paragraph[0][1]] += 1

        n = len(cp)
        for pos in self.initp:
            self.initp[pos] /= n

        # transition probability
        # bigram
        for pos1 in pos_list:
            self.trans_bi[pos1] = dict()
            self.trans_bi[pos1]["count"] = 0
            for pos2 in pos_list:
                self.trans_bi[pos1][pos2] = 0

        for paragraph in cp:
            n = len(paragraph)
            for i in range(n - 1):
                curr_pos = paragraph[i][1]
                next_pos = paragraph[i + 1][1]
                self.trans_bi[curr_pos][next_pos] += 1
                self.trans_bi[curr_pos]["count"] += 1

        for pos1 in self.trans_bi:
            for pos2 in self.trans_bi[pos1]:
                if pos2 != "count":
                    self.trans_bi[pos1][pos2] /= self.trans_bi[pos1]["count"]

        # trigram
        for pos1 in pos_list:
            self.trans_tri[pos1] = dict()
            for pos2 in pos_list:
                self.trans_tri[pos1][pos2] = dict()
                self.trans_tri[pos1][pos2]["count"] = 0
                for pos3 in pos_list:
                    self.trans_tri[pos1][pos2][pos3] = 0  # p(pos3|pos1,pos2)

        for paragraph in cp:
            n = len(paragraph)
            for i in range(n - 2):
                pos1 = paragraph[i][1]
                pos2 = paragraph[i + 1][1]
                pos3 = paragraph[i + 2][1]

                self.trans_tri[pos1][pos2][pos3] += 1
                self.trans_tri[pos1][pos2]["count"] += 1

        for pos1 in self.trans_tri:
            for pos2 in self.trans_tri[pos1]:
                for pos3 in self.trans_tri[pos1][pos2]:
                    if pos3 != "count" and self.trans_tri[pos1][pos2]["count"] != 0:
                        self.trans_tri[pos1][pos2][pos3] /= self.trans_tri[pos1][pos2][
                            "count"
                        ]

        # emission probability
        pos_count = dict()
        for pos in pos_list:
            pos_count[pos] = 0

        for word in word_list:
            self.emiss[word] = dict()
            for pos in pos_list:
                self.emiss[word][pos] = 0

        for paragraph in cp:
            for word in paragraph:
                pos_count[word[1]] += 1
                self.emiss[word[0]][word[1]] += 1

        # modify for custom dictionary
        for pos1 in pos_list:
            kw = "_" + pos1
            self.emiss[kw] = dict()
            for pos2 in pos_list:
                self.emiss[kw][pos2] = 0 if pos2 != pos1 else 1

        for word in word_list:
            for pos in pos_list:
                self.emiss[word][pos] /= pos_count[pos]

    def exists(self, word):
        return word in self.word_list

    def get_corpus_pos(self):
        return self.corpus_pos

    def get_corpus_sentence(self):
        return self.corpus_sentence

    def get_statistics_model(self, tri_gram=True):
        if tri_gram:
            return self.initp, self.trans_tri, self.emiss
        else:
            return self.initp, self.trans_bi, self.emiss

    def test_print(self):
        # TODO: check etc.
        with open("test/sentence_seg", "w", encoding="utf-8") as fout:
            fout.write(str(self.corpus_sentence))


# initial pos map
filename_posmap = os.path.join(os.path.dirname(__file__), "tools", "pos_map")
with open(filename_posmap, "r", encoding="utf-8") as f:
    for line in f:
        text = line.strip()
        pos_map = ast.literal_eval(text)

if __name__ == "__main__":
    orchid = orchid_corpus()
