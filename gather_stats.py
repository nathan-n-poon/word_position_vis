from dataclasses import dataclass
from re import search, escape
from my_types import *

class MonolithStats:
    char_length: int=0
    occurrence_pos: list[int]=[]

chapter_stats = []
monolith_stats = MonolithStats()

# search_token = "and"

def search_line(needle, line, base_offset, text):
    positions = []
    pos = find_sub(needle, line)
    curr_offset = 0
    while pos >= 0:
        positions.append(base_offset + curr_offset + pos)
        curr_offset = curr_offset + pos  + len(needle)
        pos = find_sub(needle, line[curr_offset:])
        monolith_stats.occurrence_pos.extend([text.tell()])
    return positions

def find_sub(needle, haystack):
    x = search(r"\b" + escape(needle) + r"\b", haystack)
    if x is None:
        return -1
    return x.start()

#TODO: create variant for just monolith_stats
#should be separate variant?  I think so....
def get_stats(search_token):
    global chapter_stats
    chapter_stats = []
    with open("input.txt") as text:
        chapter_count = 1
        bottom_bound = "Chapter " + str(chapter_count)
        upper_bound = "Chapter " + str(chapter_count + 1)

        found_start = False
        chapter_len = 0
        curr_chapter_offset = 0
        chapter_occurrence_pos = []

        while line := text.readline():
            if line.find(bottom_bound) >= 0:
                found_start = True
            if found_start:
                if line.find(upper_bound) >= 0:
                    chapter_stats.append(ChapterStat(chapter_number=chapter_count,
                                                     char_length=chapter_len,
                                                     occurrence_pos=chapter_occurrence_pos))

                    chapter_count += 1
                    bottom_bound = "Chapter " + str(chapter_count)
                    upper_bound = "Chapter " + str(chapter_count + 1)
                    chapter_len = 0
                    curr_chapter_offset = 0
                    chapter_occurrence_pos = []

                chapter_len += len(line)
                chapter_occurrence_pos.extend(search_line(search_token,
                                                          line,
                                                          curr_chapter_offset, text))
                curr_chapter_offset += len(line)
        chapter_stats.append(ChapterStat(chapter_number=chapter_count,
                                         char_length=chapter_len,
                                         occurrence_pos=chapter_occurrence_pos))

        monolith_stats.char_length = text.tell()
        return chapter_stats

