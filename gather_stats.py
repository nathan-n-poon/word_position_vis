from re import search, escape
from my_types import *
from consts import *

def search_line(needle, line):
    positions = []
    pos = find_sub(needle, line)
    curr_offset = 0
    while pos >= 0:
        positions.append(curr_offset + pos)
        curr_offset = curr_offset + pos  + len(needle)
        pos = find_sub(needle, line[curr_offset:])
    return positions

def find_sub(needle, haystack):
    x = search(r"\b" + escape(needle) + r"\b", haystack)
    if x is None:
        return -1
    return x.start()

class GatherMonolithStats(GatherStatInterface):
    valid: bool
    curr_offset: int
    monolith_stats: MonolithStats

    def __init__(self):
        self.valid = True
        self.curr_offset = 0
        self.monolith_stats = MonolithStats()

    def ingest_line(self, line: str, pos_list: list[int]):
        for pos in pos_list:
            self.monolith_stats.occurrence_pos.append(pos + self.curr_offset)
        self.curr_offset += len(line)
        
    def finish(self):
        self.monolith_stats.char_length = self.curr_offset

class GatherChaptersStats(GatherStatInterface):
    chapter_stats: [SegmentStat]
    chapter_count: int
    found_start: False
    chapter_len: int
    curr_chapter_offset: int
    chapter_occurrence_pos: [int]

    def __init__(self):
        self.chapter_stats = []
        self.chapter_count = 1
        self.found_start = False
        self.chapter_len = 0
        self.curr_chapter_offset = 0
        self.chapter_occurrence_pos = []
        self.bottom_bound, self.upper_bound = self.get_chapter_names(self.chapter_count)

    def get_chapter_names(self, bottom_bound: int):
        return chapter_delim + str(bottom_bound), chapter_delim + str(bottom_bound + 1)

    def ingest_line(self, line: str, pos_list: list[int]):
        if line.find(self.bottom_bound) >= 0:
            self.found_start = True
        if self.found_start:
            if line.find(self.upper_bound) >= 0:
                self.chapter_stats.append(SegmentStat(chapter_number=self.chapter_count,
                                                      char_length=self.chapter_len,
                                                      occurrence_pos=self.chapter_occurrence_pos))

                self.chapter_count += 1
                self.bottom_bound, self.upper_bound = self.get_chapter_names(self.chapter_count)

                self.chapter_len = 0
                self.curr_chapter_offset = 0
                self.chapter_occurrence_pos = []

            self.chapter_len += len(line)
            self.curr_chapter_offset += len(line)

            chapter_pos_list = []
            for pos in pos_list:
                chapter_pos_list.append(pos + self.curr_chapter_offset)
            self.chapter_occurrence_pos.extend(chapter_pos_list)
            
    def finish(self):
        if self.found_start:
            self.chapter_stats.append(SegmentStat(chapter_number=self.chapter_count,
                                                  char_length=self.chapter_len,
                                                  occurrence_pos=self.chapter_occurrence_pos))
            self.valid = True

def get_stats(search_token, mode: ViewMode):
    ops: list[GatherStatInterface] = []

    if mode == ViewMode.All:
        ops.extend([GatherChaptersStats(), MonolithStats()])
    elif mode == ViewMode.Chapters:
        ops.append(GatherChaptersStats())
    elif mode == ViewMode.Monolithic:
        ops.append(GatherMonolithStats())
    
    with open("input.txt") as text:
        while line := text.readline():
            pos_list = search_line(search_token, line)
            
            for op in ops:
                op.ingest_line(line, pos_list)

        for op in ops:
            op.finish()

    return ops