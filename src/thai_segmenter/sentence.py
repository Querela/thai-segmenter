import ast


class sentence:
    def __init__(self, *args, **kwargs):
        if len(args) == 2:
            (sentence_content, sentence_pos) = args
            self.content = sentence_content
            self.pos = sentence_pos

        elif "from_str" in kwargs:
            attributes = ast.literal_eval(kwargs["from_str"])
            for key in attributes:
                setattr(self, key, attributes[key])

    def __str__(self):
        return self.content

    def __repr__(self):
        represent = dict()
        represent["content"] = self.content
        represent["pos"] = self.pos

        return repr(represent)
