
Changelog
=========

0.4.2 (2023-08-23)
------------------

* Fix signature of ``tasks.tokenize_and_postag`` function
* Update ``tox.ini`` to include newer python version, as well as older parameters and flags
* Reformat und Lint

0.4.1 (2019-04-08)
------------------

* Fix tokenization / tokenization + POS tagging: return words instead of subwords
* Add ``--escape-special`` and ``--subwords`` parameter to CLI script for tokenization.
  Allows tokenization to further tokenize unknown words (e. g. names)
  as well as escape special characters with angle bracket entities.


0.4.0 (2019-04-08)
------------------

* Add demo webapp with sentence segmentation.
  (NOTE: Running both the webapp and (batch) sentence segmentation at the same time from the same installation is not recommeded. It can have unexpected side-effects.)
* Some reformat of ``README.rst``


0.3.3 (2019-04-07)
------------------

* Fix duplicate names (class/method for ``sentence_segment``), rename class to ``sentence_segmenter`` (``.py``).


0.3.2 (2019-04-07)
------------------

* Add ``twine`` to extras dependencies.
* Publish module on **PyPI**. (Only ``sdist``, ``bdist_wheel`` can't be built currently.)
* Fix some TravisCI warnings.


0.3.1 (2019-04-07)
------------------

* Add tasks to ``__init__.py`` for easier access.


0.3.0 (2019-04-06)
------------------

* Refactor tasks into ``tasks.py`` to enable better import in case of embedding thai-segmenter into other projects.
* Have it almost release ready. :-)
* Add some more parameters to functions (optional header detection function)
* Flesh out ``README.rst`` with examples and descriptions.
* Add Changelog items.


0.2.1 / 0.2.2 (2019-04-05)
--------------------------

* Many changes, ``bumpversion`` needs to run where ``.bumpversion.cfg`` is located else it silently fails ...
* Strip Typehints and add support for Python3.5 again.
* Add CLI tasks for cleaning, sentseg, tokenize, pos-tagging.
* Add various params, e. g. for selecting columns, skipping headers.
* Fix many bugs for TravisCI (isort, flake8)
* Use iterators / streaming approach for file input/output.


0.2.0 (2019-04-05)
------------------

* Remove support of Python 2.7 and lower equal to Python 3.5 because of Typehints.
* Added CLI skeleton.
* Add really good ``setup.py``. (with ``black``, ``flake8``)


0.1.0 (2019-04-05)
------------------

* First release version as package.
