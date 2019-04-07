========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
      - | |travis|
        | |coveralls|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |license| |commits-since|

.. |travis| image:: https://travis-ci.org/Querela/thai-segmenter.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/Querela/thai-segmenter

.. |coveralls| image:: https://coveralls.io/repos/Querela/thai-segmenter/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/Querela/thai-segmenter

.. |version| image:: https://img.shields.io/pypi/v/thai-segmenter.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/thai-segmenter

.. |license| image:: https://img.shields.io/pypi/l/thai-segmenter.svg
    :alt: PyPI - License
    :target: https://github.com/Querela/thai-segmenter/blob/master/LICENSE

.. |commits-since| image:: https://img.shields.io/github/commits-since/Querela/thai-segmenter/v0.3.3.svg
    :alt: Commits since latest release
    :target: https://github.com/Querela/thai-segmenter/compare/v0.3.3...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/thai-segmenter.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/thai-segmenter

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/thai-segmenter.svg
    :alt: Supported versions
    :target: https://pypi.org/project/thai-segmenter

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/thai-segmenter.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/thai-segmenter


.. end-badges

This package provides utilities for Thai sentence segmentation, word tokenization and POS tagging.
Because of how sentence segmentation is performed, prior tokenization and POS tagging is required and therefore also provided with this package.

Besides functions for doing sentence segmentation, tokenization, tokenization with POS tagging for single sentence strings,
there are also functions for working with large amounts of data in a streaming fashion.
They are also accessible with a commandline script ``thai-segmenter`` that accepts file or standard in/output.
Options allow working with meta-headers or tabulator separated data files.

The main functionality for sentence segmentation was extracted, reformatted and slightly rewritten from another project, 
`Question Generation Thai <https://github.com/myscloud/Question-Generation-Thai>`_.

**LongLexTo** is used as state-of-the-art word/lexeme tokenizer. An implementation was packaged in the above project but there are also (*original?*) versions `github <https://github.com/telember/lexto>`_ and `homepage <http://www.sansarn.com/lexto/>`_. To better use it for bulk processing in Python, it has been rewritten from Java to pure Python.

For POS tagging a Viterbi-Model with the annotated Orchid-Corpus is used, `paper <https://www.researchgate.net/profile/Virach_Sornlertlamvanich/publication/2630580_Building_a_Thai_part-of-speech_tagged_corpus_ORCHID/links/02e7e514db19a98619000000/Building-a-Thai-part-of-speech-tagged-corpus-ORCHID.pdf>`_.

* Free software: MIT license

Installation
============

::

    pip install thai-segmenter

Documentation
=============


To use the project:

.. code-block:: python

    sentence = """foo bar 1234"""

    # [A] Sentence Segmentation
    from thai_segmenter.tasks import sentence_segment
    # or even easier:
    from thai_segmenter import sentence_segment
    sentences = sentence_segment(sentence)

    for sentence in sentences:
        print(str(sentence))

    # [B] Lexeme Tokenization
    from thai_segmenter import tokenize
    tokens = tokenize(sentence)
    for token in tokens:
        print(token, end=" ", flush=True)

    # [C] POS Tagging
    from thai_segmenter import tokenize_and_postag
    sentence_info = tokenize_and_postag(sentence)
    for token, pos in sentence_info.pos:
        print("{}|{}".format(token, pos), end=" ", flush=True)


See more possibilities in ``tasks.py`` or ``cli.py``.

Streaming larger sequences can be achieved like this:

.. code-block:: python

    # Streaming
    sentences = ["sent1\n", "sent2\n", "sent3\n"]  # or any iterable (like File)
    from thai_segmenter import line_sentence_segmenter
    sentences_segmented = line_sentence_segmenter(sentences)


This project also provides a nifty commandline tool ``thai-segmenter`` that does most of the work for you:

.. code-block:: bash

    usage: thai-segmenter [-h] {clean,sentseg,tokenize,tokpos} ...

    Thai Segmentation utilities.

    optional arguments:
      -h, --help            show this help message and exit

    Tasks:
      {clean,sentseg,tokenize,tokpos}
        clean               Clean input from non-thai and blank lines.
        sentseg             Sentence segmentize input lines.
        tokenize            Tokenize input lines.
        tokpos              Tokenize and POS-tag input lines.


You can run sentence segmentation like this::

    thai-segmenter sentseg -i input.txt -o output.txt

or even pipe data::

    cat input.txt | thai-segmenter sentseg > output.txt

Use ``-h``/``--help`` to get more information about possible control flow options.


You can run it somewhat interactively with::

    thai-segmenter tokpos --stats

and standard input and output are used. Lines terminated with ``Enter`` are immediatly processed and printed. Stop work with key combination ``Ctrl`` + ``D`` and the ``--stats`` parameter will helpfully output some statistics.


Development
===========

To install the package for development::

    git clone https://github.com/Querela/thai-segmenter.git
    cd thai-segmenter/
    pip install -e .[dev]


After changing the source, run auto code formatting with::

    black <file>.py

And check it afterwards with::

    flake8 <file>.py

The ``setup.py`` also contains the ``flake8`` subcommand as well as an extended ``clean`` command.


Tests
-----

To run the all tests run::

    tox

You can also optionally run ``pytest`` alone::

    pytest

Or with::

    python setup.py test


Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
