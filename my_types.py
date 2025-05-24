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
    chapter_pos_norm: list[float]
    chapter_pos_coords: list[coords]

    def __init__(self):
        self.chapter_pos_norm = []
        self.chapter_pos_coords = []


class SingleRenderDeets(object):
    single_pos_norm: list[float]
    single_pos_coords: list[coords]

    def __init__(self):
        self.single_pos_norm = []
        self.single_pos_coords = []

class Chapter(object):
    render_deets: ChapterRenderDeets
    chapter_stat: ChapterStat

    def __init__(self, chapter_stat):
        self.render_deets = ChapterRenderDeets()
        self.chapter_stat = chapter_stat