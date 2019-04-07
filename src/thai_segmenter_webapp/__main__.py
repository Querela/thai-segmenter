from thai_segmenter_webapp.app import app


def main():
    # app.run(); import sys; sys.exit()  # if not with gevent

    try:
        # use gevent if it exists, else default run it stupid ...
        from gevent.pywsgi import WSGIServer

        app.config["TESTING"] = False
        app.config["DEBUG"] = False
        http_server = WSGIServer(("", 8999), app)
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
