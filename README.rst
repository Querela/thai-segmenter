========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis|
        | |coveralls|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |travis| image:: https://travis-ci.org/Querela/thai-segmenter.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/Querela/thai-segmenter

.. |coveralls| image:: https://coveralls.io/repos/Querela/thai-segmenter/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/Querela/thai-segmenter

.. |version| image:: https://img.shields.io/pypi/v/thai-segmenter.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/thai-segmenter

.. |commits-since| image:: https://img.shields.io/github/commits-since/Querela/thai-segmenter/v0.1.1.svg
    :alt: Commits since latest release
    :target: https://github.com/Querela/thai-segmenter/compare/v0.1.1...master

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

Thai tokenizer, POS-tagger and sentence segmenter.

* Free software: MIT license

Installation
============

::

    pip install thai-segmenter

Documentation
=============


To use the project:

.. code-block:: python

    import thai_segmenter
    thai_segmenter.longest()


Development
===========

To run the all tests run::

    tox

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
