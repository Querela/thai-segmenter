# -*- coding: utf-8 -*-
"""App module + factory?

see here: https://github.com/sloria/cookiecutter-flask/blob/master/%7B%7Bcookiecutter.app_name%7D%7D/%7B%7Bcookiecutter.app_name%7D%7D/app.py
"""
from flask import Flask
from thai_segmenter_webapp.segmenter import SentenceSegmenter

# ---------------------------------------------------------------------------


app = Flask(__name__.split(".")[0])
app.config["TESTING"] = True
app.config["DEBUG"] = True


sentseg = SentenceSegmenter(app)


# ----------------------------------------------------------------------------
