from . import markup as m


class PMarkup:

    def __init__(self, pansi, idx: int, pidx, standalone: bool, code: str):
        self.pansi = pansi
        self.idx = idx
        self.pidx = pidx
        self.children = list()
        self.parent = pansi.markup[pidx] if pidx else None
        if self.parent:
            self.parent.children.append(self)
        self.standalone = standalone
        self.code = code
        self.start_text = ""
        self.end_text = ""
        self.start_pos = 0
        self.end_pos = 0

    def auto_close(self, pos):
        self.end_pos = pos


class PAnsiString:

    def __init__(self, src: str):
        self.source = src
        self.clean = ""
        self.markup = list()
        self.markup_idx_map = list()
        state, pos, index = 0, 0, None
        mstack = list()
        tag = ""

        for s in src:
            if state == 0:
                if s == m.TAG_START:
                    state = 1
                else:
                    self.clean += s
                    self.markup_idx_map.append(index)
                    pos += 1
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
                    mark = PMarkup(self, len(self.markup), index, False, tag)
                    mark.start_pos = pos
                    self.markup.append(mark)
                    index = len(self.markup)-1
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
                    mark.end_pos = pos
                    index = mark.pidx
                else:
                    mstack[-1].end_text += s
                continue

        for m in reversed(mstack):
            m.auto_close(pos)
