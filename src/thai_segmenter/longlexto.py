#!/usr/bin/env python
# pylint: disable=missing-docstring,line-too-long
# pylint: disable=useless-object-inheritance,len-as-condition
# pylint: disable=too-many-boolean-expressions,too-many-branches

#
# Licensed under the CC-GNU Lesser General Public License, Version 2.1 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://creativecommons.org/licenses/LGPL/2.1/
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#
# Author: Choochart Haruechaiyasak
# Last update: 28 March 2006
#

#
# Re-Write to Python:
# Author: Erik Körner
# Last update: 31 Dec 2018
#
# Used tools:
# - java source + class files
# - decompiler CFR at http://www.javadecompilers.com/
# - java2python conversion tool from https://github.com/natural/java2python/
# - sublime + WSL ...
# -> and manual review/rewrite of the generated python code with comparisons to the original java source + many improvements
#

"""LongLexTo: Tokenizing Thai texts using Longest Matching Approach"""

# import only used for initialization and test/main code
from __future__ import print_function

import codecs
import os.path
import sys
import threading


class Trie(object):
    """Implementing trie data structure.

    Usage:
    >>> dict = Trie()          # Constructor
    >>> dict.add(word, value)  # add word
    >>> dict.contains(string)  # Check if contain string, return: freq if word, 0 if prefix, -1 otherwise
    """

    def __init__(self, char="\u00fb"):
        """Creates a Trie using the specified character.
        Defaults to a root symbol as the character (0xFB / 251).
        """
        self.char = char  # pylint: disable=invalid-name
        self.children = list()
        self.parent = None
        self.is_word = False

    @staticmethod
    def _create_node(char):
        """Used to create the trie nodes when a string is added to a trie. Returns the trie."""
        return Trie(char)

    def add_child(self, trie):
        """Inserts the trie as the last child."""
        self.insert_child(trie, len(self.children))

    def insert_child(self, trie, index):
        """Inserts the trie at the specified index.
        If successful, the parent of the specified trie is updated to be this trie.
        Raises exceptions on invalid inputs."""
        if index < 0 or index > len(self.children):
            raise ValueError("required: index >= 0 && index <= numChildren")
        if trie is None:
            raise ValueError("cannot add null child")
        if trie.parent is not None:
            raise ValueError("specified child still belongs to parent")
        if self.has_char(trie.char):
            raise ValueError("duplicate chars not allowed")
        if self.is_descendent(trie):
            raise ValueError("cannot add cyclic reference")

        trie.parent = self
        self.children.insert(index, trie)

    def is_descendent(self, trie):
        """Returns true if this node is a descendent of the specified node or this node and the specified
        node are the same node, false otherwise."""
        trie2 = self
        while trie2 is not None:
            if trie2 == trie:
                return True
            trie2 = trie2.parent
        return False

    # ------------------ End of tree-level operations.  Start of string operations. ------------------

    def add(self, string):
        """Adds the string to the trie.
        Returns true if the string is added or false if the string is already contained in the trie."""
        return self._add(string, 0)

    def _add(self, string, index=0):
        """[Internal function] Adds the string to the trie.
        Returns true if the string is added or false if the string is already contained in the trie."""
        if index == len(string):
            if self.is_word:
                return False
            self.is_word = True
            return True

        char = string[index]
        for child in self.children:
            if child.char != char:
                continue
            return child._add(string, index + 1)  # pylint: disable=protected-access

        # this code adds from the bottom to the top because the add_child method
        # checks for cyclic references.  This prevents quadratic runtime.
        pos = len(string) - 1
        trie = Trie._create_node(string[pos])
        trie.is_word = True

        pos -= 1
        while pos >= index:
            trie2 = Trie._create_node(string[pos])
            trie2.add_child(trie)
            trie = trie2
            pos -= 1
        self.add_child(trie)

        return True

    def get_node_by_char(self, char):
        """Returns the child that has the specified character or null if no child has the specified character."""
        for child in self.children:
            if child.char != char:
                continue
            return child
        return None

    def get_node(self, string):
        """Returns the last trie in the path that prefix matches the specified prefix string
        rooted at this node, or null if there is no such prefix path."""
        return self._get_node(string, 0)

    def _get_node(self, string, index=0):
        """[Internal function] Returns the last trie in the path
        that prefix matches the specified prefix string rooted at this node,
        or null if there is no such prefix path."""
        if index == len(string):
            return self
        char = string[index]
        for child in self.children:
            if child.char != char:
                continue
            return child._get_node(
                string, index + 1
            )  # pylint: disable=protected-access
        return None

    def size(self):
        """Returns the number of nodes that define isWord as true,
        starting at this node and including all of its descendents.
        This operation requires traversing the tree rooted at this node."""
        num = 0
        if self.is_word:
            num += 1
        for child in self.children:
            num += child.size()
        return num

    def get_words(self, string):
        """Returns all of the words in the trie that begin with the specified prefix rooted at this node.
        An array of length 0 is returned if there are no words that begin with the specified prefix."""
        trie = self._get_node(string)
        if trie is None:
            return list()
        return trie._get_words_list()  # pylint: disable=protected-access

    def _get_words_list(self):
        """[Internal function] Returns all of the words in the trie
        that begin with the specified prefix (rooted at this node?)."""
        arrstring = list()
        if self.is_word:
            arrstring.append(str(self))

        for child in self.children:
            arrstring.extend(
                child._get_words_list()
            )  # pylint: disable=protected-access

        return arrstring

    def has_prefix(self, string):
        """Returns true if the specified string has a prefix path starting at this node.
        Otherwise false is returned."""
        trie = self._get_node(string)
        if trie is None:
            return False
        return True

    def contains(self, string):
        """Check if the specified string is in the trie.
        Return value 1 if contains, 0 if has_prefix, else -1"""
        trie = self._get_node(string)
        if trie is None:
            return -1
        if trie.is_word:
            return 1
        return 0

    def has_char(self, char):
        """Returns true if this node has a child with the specified character."""
        for child in self.children:
            if child.char != char:
                continue
            return True
        return False

    def get_height(self):
        """Returns the number of nodes from this node up to the root node.
        The root node has height 0."""
        height = -1
        trie = self
        while trie is not None:
            height += 1
            trie = trie.parent
        return height

    def __str__(self):
        """Returns a string containing the characters on the path from this node to the root,
        but not including the root character.  The last character in the returned string is the
        character at this node."""
        chars = list()
        trie = self
        while trie.parent is not None:
            chars.append(trie.char)
            trie = trie.parent
        return "".join(reversed(chars))


class LongParseTree(object):
    def __init__(self, trie, index_list, type_list):
        self.dict_ = trie  # For storing words from dictionary
        self.index_list = index_list  # List of index positions
        self.type_list = type_list  # List of word types
        # Adding front-dependent characters
        self.front_dep_char = [
            "\u0e30",
            "\u0e31",
            "\u0e32",
            "\u0e33",
            "\u0e34",
            "\u0e35",
            "\u0e36",
            "\u0e37",
            "\u0e38",
            "\u0e39",
            "\u0e45",
            "\u0e47",
            "\u0e4c",
            "\u0e4d",
        ]
        # Adding rear-dependent characters
        self.rear_dep_char = [
            "\u0e31",
            "\u0e37",
            "\u0e40",
            "\u0e41",
            "\u0e42",
            "\u0e43",
            "\u0e44",
            "\u0e4d",
        ]
        # Adding tonal characters
        self.tonal_char = ["\u0e48", "\u0e49", "\u0e4a", "\u0e4b"]
        # Adding ending characters
        self.ending_char = ["\u0e46", "\u0e2f"]

    def next_word_valid(self, begin_pos, string):
        if begin_pos == len(string):
            return True
        if string[begin_pos] <= "~":  # English alphabets/digits/special characters
            return True
        for i in range(begin_pos + 1, len(string)):
            status = self.dict_.contains(string[begin_pos:i])
            if status == 1:
                return True
            if status != 0:
                break
        return False

    def parse_word_instance(self, begin_pos, string):
        prev_char = "\u0000"
        longest_pos = -1  # longest_pos
        longest_valid_pos = -1  # Longest valid position
        num_valid_pos = 0  # Number of longest value pos (for determining ambiguity)

        status = 1
        for pos in range(begin_pos + 1, len(string) + 1):
            if status == -1:
                break
            status = self.dict_.contains(string[begin_pos:pos])
            if status != 1:
                continue

            # Record longest so far
            longest_pos = pos
            if not self.next_word_valid(pos, string):
                continue

            longest_valid_pos = pos
            num_valid_pos += 1

        # --------------------------------------------------
        # For checking rear dependent character
        if begin_pos >= 1:
            prev_char = string[begin_pos - 1]

        # Unknown word
        if longest_pos == -1:
            # Combine unknown segments
            return_pos = begin_pos + 1
            if len(self.index_list) > 0 and (
                string[begin_pos] in self.front_dep_char
                or string[begin_pos] in self.tonal_char
                or prev_char in self.rear_dep_char
                or self.type_list[-1] == 0
            ):
                self.index_list[-1] = return_pos
                self.type_list[-1] = 0
            else:
                self.index_list.append(return_pos)
                self.type_list.append(0)
            return return_pos

        # --------------------------------------------------
        # Known or ambiguous word

        # If there is no merging point
        if longest_valid_pos == -1:
            # Check whether front char requires rear segment
            if prev_char in self.rear_dep_char:
                self.index_list[-1] = longest_pos
                self.type_list[-1] = 0
            else:
                self.type_list.append(1)
                self.index_list.append(longest_pos)
            return longest_pos  # known followed by unknown: consider longest_pos

        # Check whether front char requires rear segment
        if prev_char in self.rear_dep_char:
            self.index_list[-1] = longest_valid_pos
            self.type_list[-1] = 0
        elif num_valid_pos == 1:
            self.type_list.append(1)  # known
            self.index_list.append(longest_valid_pos)
        else:
            self.type_list.append(2)  # ambiguous
            self.index_list.append(longest_valid_pos)

        return longest_valid_pos


class LongLexTo(object):
    """LongLexTo: Tokenizing Thai texts using Longest Matching Approach

    Note:
    Types:
        0 = unknown
        1 = known
        2 = ambiguous
        3 = English/digits
        4 = special characters"""

    def __init__(self, dict_file="lexitron.txt", raise_errors=False):
        """Constructor with an (optional default) dictionary file.
        Set raise_errors to True if you want Python to raise Exceptions instead of stderr messages."""
        self._lock = threading.RLock()  # to block concurrent access

        self.dict_file = dict_file
        self.dict_ = Trie()  # For storing words from dictionary

        if not os.path.exists(dict_file):
            if raise_errors:
                raise ValueError("Dictionary file not found: {}".format(dict_file))
            else:
                print(
                    " !!! Error: Dictionary file was not found: {}".format(dict_file),
                    file=sys.stderr,
                )
        else:
            self.add_dict(dict_file)

        self.iter_ = None  # Iterator for index_list OR line_list (depends on the call)

        self.index_list = list()  # List of word index positions
        self.line_list = list()  # List of line index positions
        self.type_list = list()  # List of word types (for word only)

        # Parsing tree (for Thai words)
        self.ptree = LongParseTree(self.dict_, self.index_list, self.type_list)

    def add_dict(self, dict_file):
        """Add dictionary (e.g., unknown-word file).
        Reads words per line from given file."""
        with codecs.open(
            dict_file, "r", encoding="utf-8"
        ) as fr:  # pylint: disable=invalid-name
            for line in fr:
                line = line.strip()
                if line:
                    self.dict_.add(line)

    def word_instance(self, text):
        """Word tokenization."""
        with self._lock:
            # important: this method of clearing because self.ptree has references to those lists
            self.index_list[:] = []
            self.type_list[:] = []

            pos, len_text = 0, len(text)
            while pos < len_text:  # for the whole text length
                # Check for special characters and English words/numbers
                char = text[pos]

                # English
                if ("A" <= char <= "Z") or ("a" <= char <= "z"):
                    while pos < len_text and (
                        ("A" <= char <= "Z") or ("a" <= char <= "z")
                    ):
                        char = text[pos]
                        pos += 1
                    if pos < len_text:
                        pos -= 1
                    self.index_list.append(pos)
                    self.type_list.append(3)
                    continue

                # Digits
                if ("0" <= char <= "9") or ("\u00f0" <= char <= "\u00f9"):
                    while pos < len_text and (
                        ("0" <= char <= "9")
                        or ("\u00f0" <= char <= "\u00f9")
                        or char == ","
                        or char == "."
                    ):
                        char = text[pos]
                        pos += 1
                    if pos < len_text:
                        pos -= 1
                    self.index_list.append(pos)
                    self.type_list.append(3)
                    continue

                # Special characters
                if char <= "~" or char in ("\u00e6", "\u00cf", "\u201c", "\u201d", ","):
                    pos += 1
                    self.index_list.append(pos)
                    self.type_list.append(4)
                    continue

                # Thai word (known/unknown/ambiguous)
                pos = self.ptree.parse_word_instance(pos, text)

            self.iter_ = iter(self.index_list)

    def line_instance(self, text):
        """Line-break tokenization."""
        with self._lock:
            window_size = 10  # for detecting parentheses, quotes
            self.line_list = list()
            self.word_instance(text)

            i = 0
            while i < len(self.type_list):
                cur_type = self.type_list[i]
                cur_index = self.index_list[i]

                if cur_type in (3, 4):
                    # Parentheses
                    if cur_type == 4 and text[cur_index - 1] == "(":
                        pos = i + 1
                        while pos < len(self.type_list) and pos < i + window_size:
                            temp_type = self.type_list[pos]
                            temp_index = self.index_list[pos]
                            pos += 1
                            if temp_type == 4 and text[temp_index - 1] == ")":
                                self.line_list.append(temp_index)
                                i = pos - 1
                                break

                    # Single quote
                    elif cur_type == 4 and text[cur_index - 1] == "'":
                        pos = i + 1
                        while pos < len(self.type_list) and pos < i + window_size:
                            temp_type = self.type_list[pos]
                            temp_index = self.index_list[pos]
                            pos += 1
                            if temp_type == 4 and text[temp_index - 1] == "'":
                                self.line_list.append(temp_index)
                                i = pos - 1
                                break

                    # Double quote
                    elif cur_type == 4 and text[cur_index - 1] == '"':
                        pos = i + 1
                        while pos < len(self.type_list) and pos < i + window_size:
                            temp_type = self.type_list[pos]
                            temp_index = self.index_list[pos]
                            pos += 1
                            if temp_type == 4 or text[temp_index - 1] == '"':
                                self.line_list.append(temp_index)
                                i = pos - 1
                                break

                    else:
                        self.line_list.append(cur_index)

                else:
                    next_type = self.type_list[i + 1]
                    next_index = self.index_list[i + 1]
                    # TODO: check condition?
                    if next_type == 3 or (
                        next_type == 4
                        and (
                            text[next_index - 1] == " "
                            or text[next_index - 1] == '"'
                            or text[next_index - 1] == "("
                            or text[next_index - 1] == "'"
                        )
                    ):
                        self.line_list.append(self.index_list[i])
                    elif cur_type == 1 and next_type not in (0, 4):
                        self.line_list.append(self.index_list[i])

                i += 1

            if i < len(self.type_list):
                self.line_list.append(self.index_list[-1])

            self.iter_ = iter(self.line_list)

    def get_words(self, line):
        """(Word-)Tokenizes the given string and yield the tokens."""
        with self._lock:
            self.word_instance(line)
            begin = 0
            for end in self.index_list:
                yield line[begin:end]
                begin = end

    @classmethod
    def create(cls, dict_file="lexitron.txt", unknown_dict_file="unknown.txt"):
        """Static method to build the tokenizer with default dict files."""
        tokenizer = cls(dict_file)
        if os.path.exists(unknown_dict_file):
            tokenizer.add_dict(unknown_dict_file)
        return tokenizer


def main(args):
    """Dummy method as example use case."""
    tokenizer = LongLexTo.create()

    in_file_name = args[1].strip()  # sys.stdin
    # System.getProperty("user.dir") + "//" + in_file_name
    lines = list()
    with codecs.open(
        in_file_name, "r", encoding="utf-8"
    ) as fr:  # pylint: disable=invalid-name
        for line in fr:
            line = line.strip()
            if line:
                lines.append(line)

    for line in lines:
        for word in tokenizer.get_words(line):
            print(word)
        print()


if __name__ == "__main__":
    main(sys.argv)
