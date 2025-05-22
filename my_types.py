from dataclasses import dataclass

@dataclass
class ChapterStat:
    chapter_number: int
    char_length: int
    occurrence_pos: list[int]

class coords(object):
    x: float
    y: float

    def __init__(self, x, y):
        self.x = x
        self.y = y

class ChapterRenderDeets(object):
    occ_pos_norm: list[float]
    occ_pos_plot_loc: list[coords]

    def __init__(self):
        self.occ_pos_norm = []
        self.occ_pos_plot_loc = []

class Chapter(object):
    render_deets: ChapterRenderDeets
    chapter_stat: ChapterStat

    def __init__(self, chapter_stat):
        self.render_deets = ChapterRenderDeets()
        self.chapter_stat = chapter_stat