# -*- coding: utf-8 -*-
"""App module + factory?

see here: https://github.com/sloria/cookiecutter-flask
    /blob/master/%7B%7Bcookiecutter.app_name%7D%7D/%7B%7Bcookiecutter.app_name%7D%7D/app.py
"""
from flask import Flask
from thai_segmenter_webapp import default_config
from thai_segmenter_webapp.segmenter import SentenceSegmenter

# ---------------------------------------------------------------------------


sentseg = SentenceSegmenter()


# ----------------------------------------------------------------------------

# from thai_segmenter_webapp import views  # noqa: E402,F401  isort:skip

# ----------------------------------------------------------------------------


def create_app(config_object="thai_segmenter_webapp.config"):
    app = Flask(__name__.split(".")[0])

    # configure
    app.config.from_object(default_config)

    try:
        app.config.from_object(
            config_object
        )  # TODO: how to handle if missing (or if installed as package?)
    except ImportError:
        app.logger.warning(
            "No config object ({}). Consider creating one from the default_config.py file.".format(
                config_object
            )
        )

    app.config.from_envvar("THAI_SEGMENTER_WEBAPP_CONFIG", silent=True)

    # register extensions
    sentseg.init_app(app)

    # register routes
    # https://stackoverflow.com/questions/25254022/flask-are-blueprints-necessary-for-app-factories
    from thai_segmenter_webapp.views import view_index

    app.add_url_rule("/", "view_index", view_index, methods=["GET", "POST"])

    return app


# ----------------------------------------------------------------------------
