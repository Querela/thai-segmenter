import logging
from functools import lru_cache

from flask import current_app as app
from flask import render_template
from flask import request
from thai_segmenter_webapp.app import sentseg
from thai_segmenter_webapp.segmenter import dump_tree_pos_info
from thai_segmenter_webapp.segmenter import make_tree_for_output
from thai_segmenter_webapp.segmenter import make_tree_pos_info

# ----------------------------------------------------------------------------


# @app.route("/", methods=["GET", "POST"])
def view_index():
    if request.method == "POST":
        form = request.form
        app.logger.info(form)
        text = form.get("thaiText")
        add_pos = form.get("POSOutput")
        add_seg_tree = form.get("SegOutput")

        all_sentences = process_text(text)

        return render_template(
            "index.html",
            all_sentences=all_sentences,
            add_pos=add_pos,
            add_seg_tree=add_seg_tree,
        )
    else:
        return render_template("index.html")


@lru_cache(maxsize=100)
def process_text(text):
    lines = text.split("\n")
    lines = [l.strip() for l in lines]
    lines = [l for l in lines if l]

    all_sentences = list()
    for nr, line in enumerate(lines, 1):
        app.logger.debug("Segment (%s): %s", nr, line)
        paragraph, fragments, sentences = sentseg.do_segmentation(line)

        if app.logger.isEnabledFor(logging.DEBUG):
            ret, tree = make_tree_pos_info(paragraph.pos)
            dump_tree_pos_info(app.logger, ret, tree)

        tree = make_tree_for_output(make_tree_pos_info(paragraph.pos)[1])
        # pos = [(p[0:2]) for p in paragraph.pos]  # [p[0:4] for p in paragraph.pos]

        if app.logger.isEnabledFor(logging.DEBUG):
            app.logger.debug("POS (%s): %s", nr, paragraph.pos)
            app.logger.debug("Fragments (%s): %s", nr, fragments)
            app.logger.debug("Segmented Sentences (%s): %s", nr, sentences)
            pass

        all_sentences.append((nr, paragraph, tree, sentences))

    return all_sentences
