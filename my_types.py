from abc import abstractmethod
from dataclasses import dataclass

@dataclass
class SegmentStat:
    chapter_number: int
    char_length: int
    occurrence_pos: list[int]

class MonolithStats:
    char_length: int
    occurrence_pos: list[int]

    def __init__(self):
        self.char_length = 0
        self.occurrence_pos = []

class coords(object):
    x: float
    y: float

    def __init__(self, x, y):
        self.x = x
        self.y = y

class SegmentRenderDeets(object):
    segment_pos_norm: list[float]
    segment_pos_coords: list[coords]

    def __init__(self):
        self.segment_pos_norm = []
        self.segment_pos_coords = []

class SingleViewRenderDeets(object):
    single_view_pos_norm: list[float]
    single_view_pos_coords: list[coords]

    single_view_pos_segments: list[list[float]]

    def __init__(self):
        self.single_view_pos_norm = []
        self.single_view_pos_coords = []
        self.single_view_pos_segments = [[]]

class Segment(object):
    render_deets: SegmentRenderDeets
    segment_stat: SegmentStat

    def __init__(self, chapter_stat):
        self.render_deets = SegmentRenderDeets()
        self.segment_stat = chapter_stat

class GatherStatInterface(object):
    valid: bool=False

    @abstractmethod
    def ingest_line(self, line: str, pos_list: list[int]):
        pass

    @abstractmethod
    def finish(self):
        pass
