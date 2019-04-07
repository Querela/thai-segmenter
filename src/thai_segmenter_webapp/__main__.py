from thai_segmenter_webapp.app import create_app


def main():
    app = create_app()

    app.logger.info("Routes: {}".format(app.url_map))
    app.logger.debug("Config: {}".format(app.config))

    if app.config["TESTING"]:
        # if not with gevent
        app.logger.warning("Run in TESTING mode ...")

        app.run()
        raise SystemExit("TESTING END")

    try:
        # use gevent if it exists, else default run it stupid ...
        from gevent.pywsgi import WSGIServer

        http_server = WSGIServer((app.config["HOST"], app.config["PORT"]), app)
        print(
            "Run WSGIServer listening on < {}:{} > ... (Press Ctrl+C to quit.)".format(
                app.config["HOST"], app.config["PORT"]
            )
        )
        http_server.serve_forever()
    except ImportError:
        app.logger.warning("No gevent found. Run really simple ...")
        # as demo app:
        # - host: 0.0.0.0 - run on localhost, accept requests from every IP
        # - ip: 8999 - our demo webapp port
        # - use_evalex - block interactive debugging
        # see: http://flask.pocoo.org/docs/1.0/api/#flask.Flask.run
        # app.run(host='0.0.0.0', port=8999, debug=False, use_reloader=False, use_evalex=False)
        app.run()


if __name__ == "__main__":
    main()
