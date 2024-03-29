#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import codecs
import distutils.log
import glob
import io
import os
import re
import subprocess
from distutils import dir_util
from distutils.command.clean import clean as _CleanCommand  # noqa: N812

from setuptools import Command
from setuptools import find_packages
from setuptools import setup


class CleanCommand(_CleanCommand):
    # see:
    # - https://github.com/dave-shawley/setupext-janitor/blob/master/setupext/janitor.py  # noqa: E501
    # - https://jichu4n.com/posts/how-to-add-custom-build-steps-and-commands-to-setuppy/  # noqa: E501
    user_options = _CleanCommand.user_options[:]
    user_options.extend(
        [
            # The format is (long option, short option, description).
            (
                "egg-base=",
                "e",
                "directory containing .egg-info directories "
                "(default: top of the source tree)",
            ),
            ("eggs", None, "remove *.egg-info and *.eggs directories"),
            ("pycache", "p", "remove __pycache__ directories"),
            ("pytest", None, "remove pytest + coverage hidden files"),
        ]
    )
    boolean_options = _CleanCommand.boolean_options[:]
    boolean_options.extend(["eggs", "pycache", "pytest"])

    def initialize_options(self):
        super().initialize_options()
        self.egg_base = None
        self.eggs = False
        self.pycache = False
        self.pytest = False

    def finalize_options(self):
        super().finalize_options()

        if self.egg_base is None:
            self.egg_base = os.curdir

        if self.all:
            self.eggs = True
            self.pycache = True
            self.pytest = True

    def run(self):  # pylint: disable=too-many-branches
        super().run()

        dir_names = set()
        file_names = set()

        if self.eggs:
            for name in os.listdir(self.egg_base):
                dname = os.path.join(self.egg_base, name)
                if name.endswith(".egg-info") and os.path.isdir(dname):
                    dir_names.add(dname)
            for name in os.listdir(os.curdir):
                if name.endswith(".egg"):
                    dir_names.add(name)
                if name == ".eggs":
                    dir_names.add(name)

        if self.pycache:
            for root, dirs, _ in os.walk(os.curdir):
                if "__pycache__" in dirs:
                    dir_names.add(os.path.join(root, "__pycache__"))

        if self.pytest:
            file_names.add(".coverage")
            dir_names.add(".pytest_cache")

        for dir_name in dir_names:
            if os.path.exists(dir_name):
                dir_util.remove_tree(dir_name, dry_run=self.dry_run)
            else:
                self.announce("skipping {0} since it does not exist".format(dir_name))

        for file_name in file_names:
            if os.path.exists(file_name):
                self.announce("removing file {0}", level=distutils.log.INFO)
                if not self.dry_run:
                    os.remove(file_name)
            else:
                self.announce("skipping {0} since it does not exist".format(file_name))


class PylintCommand(Command):
    """A custom command to run Pylint on all Python source files.
    see: https://jichu4n.com/posts/how-to-add-custom-build-steps-and-commands-to-setuppy/
    """  # noqa: E501

    description = "run Pylint on Python source files"
    user_options = [
        ("no-color", None, "suppress auto coloring"),
        ("pylint-rcfile=", None, "path to Pylint config file"),
        ("dir=", None, "path to run Pylint on"),
    ]

    boolean_options = ["no-color"]

    def initialize_options(self):
        """Set default values for options."""
        self.pylint_rcfile = ""
        self.no_color = False
        self.dir = ""

    def finalize_options(self):
        """Post-process options."""
        if self.pylint_rcfile:
            assert os.path.exists(self.pylint_rcfile), (
                "Pylint config file %s does not exist." % self.pylint_rcfile
            )
        if self.dir:
            assert os.path.exists(self.dir), (
                "Folder %s to check does not exist." % self.dir
            )

    def package_files(self, no_recurse_list=False):
        """Collect the files/dirs included in the registered modules."""
        seen_package_directories = ()
        directories = self.distribution.package_dir or {}
        empty_directory_exists = "" in directories
        packages = self.distribution.packages or []
        for package in packages:
            package_directory = package
            if package in directories:
                package_directory = directories[package]
            elif empty_directory_exists:
                package_directory = os.path.join(directories[""], package_directory)

            if not no_recurse_list and package_directory.startswith(
                seen_package_directories
            ):
                continue

            seen_package_directories += (package_directory + ".",)
            yield package_directory

    def module_files(self):
        """Collect the files listed as py_modules."""
        modules = self.distribution.py_modules or []
        filename_from = "{0}.py".format
        for module in modules:
            yield filename_from(module)

    def distribution_files(self):
        """Collect package and module files.
        From: https://gitlab.com/pycqa/flake8/blob/master/src/flake8/main/setuptools_command.py
        """  # noqa: E501
        for package in self.package_files():
            yield package

        for module in self.module_files():
            yield module

        yield "setup.py"

    def run(self):
        """Run command."""
        command = ["pylint"]
        # command.append('-d F0010')  # TODO: hmmm?
        if not self.no_color:
            command.append("--output-format=colorized")
        if self.pylint_rcfile:
            command.append("--rcfile=%s" % self.pylint_rcfile)
        if self.dir:
            command.append(self.dir)
        else:
            # command.append(os.getcwd())
            for name in self.distribution_files():
                command.append(name)
            # command.append('*.py')
            # command.append('**/*.py')

        self.announce("Running command: %s" % str(command), level=distutils.log.INFO)
        # TODO: self.spawn(command, dry_run=self.dry_run)
        try:
            subprocess.check_call(" ".join(command), shell=True)
        except subprocess.CalledProcessError as cpe:
            self.announce(cpe, level=distutils.log.ERROR)
            # see: flake8 handling
            raise SystemExit from cpe
        # self.spawn(command)


def find_version(path):
    """Find version string in given file."""
    with codecs.open(path, "r") as file:
        content = file.read()

    version_match = re.search("""__version__ = ['"]([^'"]+)['"]""", content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8"),
    ) as fh:
        return fh.read()


setup(
    name="thai-segmenter",
    version="0.4.2",
    license="MIT license",
    description="Thai tokenizer, POS-tagger and sentence segmenter.",
    long_description="{readme}\n{changelog}".format(
        readme=re.compile("^.. start-badges.*^.. end-badges", re.M | re.S).sub(
            "", read("README.rst")
        ),
        changelog=re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", read("CHANGELOG.rst")),
    ),
    author="Erik Körner",  # \xf6
    author_email="koerner@informatik.uni-leipzig.de",
    url="https://github.com/Querela/thai-segmenter",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[
        os.path.splitext(os.path.basename(path))[0] for path in glob.glob("src/*.py")
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        "Topic :: Utilities",
    ],
    project_urls={
        "Changelog": "https://github.com/Querela/thai-segmenter/blob/master/CHANGELOG.rst",
        "Issue Tracker": "https://github.com/Querela/thai-segmenter/issues",
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
        "thai",
        "nlp",
        "sentence segmentation",
        "tokenize",
        "pos-tag",
        "longlexto",
        "orchid",
    ],
    python_requires=">=3.4",
    # $ pip install -e .
    install_requires=[
        # eg: 'aspectlib==1.1.1', 'six>=1.7',
    ],
    tests_require=["pytest", "pytest-cov", "pytest-mock", "pytest-pylint"],
    # $ pip install -e .[dev]
    # $ flake8 *.py
    # $ pylint *.py
    # $ isort --verbose --check-only --diff *.py
    # $ pyment -q "'''" *.py
    # $ coverage report --skip-covered
    # $ coverage html
    # $ coverage erase
    # $ prospector
    # mypy / pytype ?
    # $ python setup.py check -r -s
    # $ python setup.py sdist
    # $ twine upload --verbose --skip-existing dist/*.gz
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
        "dev": [
            "bumpversion",
            "black",
            "flake8",
            "pylint",
            "pyment",
            "tox",
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "readme_renderer",
            "twine",
            # 'coverage',
        ],
        "webapp": ["Flask", "gevent"],
    },
    entry_points={
        "console_scripts": [
            "thai-segmenter = thai_segmenter.cli:main",
            "thai-segmenter-webapp = thai_segmenter_webapp.__main__:main [webapp]",
        ]
    },
    cmdclass={"clean": CleanCommand, "pylint": PylintCommand},
)
