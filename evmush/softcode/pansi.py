import evmush.softcode.markup as m


class PMarkup:

    def __init__(self, pansi, parent, standalone: bool, code: str):
        self.pansi = pansi
        self.children = list()
        self.parent = parent
        if self.parent:
            self.parent.children.append(self)
        self.standalone = standalone
        self.code = code
        self.start_text = ""
        self.end_text = ""


class PAnsiString:

    def __init__(self, src: str):
        self.source = src if src else ""
        self.clean = ""
        self.markup = list()
        self.markup_idx_map = list()
        if src:
            self.from_raw(src)

    def from_raw(self, src: str):
        self.source = src
        self.clean = ""
        self.markup.clear()
        self.markup_idx_map.clear()

        state, index = 0, None
        mstack = list()
        tag = ""

        for s in src:
            if state == 0:
                if s == m.TAG_START:
                    state = 1
                else:
                    self.clean += s
                    self.markup_idx_map.append(index)
                continue
            if state == 1:
                # Encountered a TAG START...
                tag = s
                state = 2
                continue
            if state == 2:
                # we are just inside a tag. if it begins with / this is a closing. else, opening.
                if s == "/":
                    state = 4
                else:
                    state = 3
                    mark = PMarkup(self, index, False, tag)
                    index = mark
                    mstack.append(mark)
                continue
            if state == 3:
                # we are inside an opening tag, gathering text. continue until TAG_END.
                if s == m.TAG_END:
                    state = 0
                else:
                    mstack[-1].start_text += s
                continue
            if state == 4:
                # we are inside a closing tag, gathering text. continue until TAG_END.
                if s == m.TAG_END:
                    state = 0
                    mark = mstack.pop()
                    index = mark.parent
                else:
                    mstack[-1].end_text += s
                continue
