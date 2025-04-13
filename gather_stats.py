from dataclasses import dataclass
from re import search, escape

@dataclass
class ChapterStat:
    chapter_number: int
    char_length: int
    occurrence_pos: list[int]
    occ_pos_norm: list[float]
    occ_pos_plot_loc: list[float]

chapter_stats = []

search_token = "and"


def search_line(needle, line, base_offset):
    positions = []
    pos = find_sub(needle, line)
    curr_offset = 0
    while pos >= 0:
        positions.append(base_offset + curr_offset + pos)
        curr_offset = curr_offset + pos  + len(needle)
        pos = find_sub(needle, line[curr_offset:])
    return positions

def find_sub(needle, haystack):
    x = search(r"\b" + escape(needle) + r"\b", haystack)
    if x is None:
        return -1
    return x.start()

def get_chapters_stats(search_token):
    with open("input.txt") as text:
        chapter_count = 1
        bottom_bound = "Chapter " + str(chapter_count)
        upper_bound = "Chapter " + str(chapter_count + 1)

        found_start = False
        chapter_len = 0
        curr_chapter_offset = 0
        chapter_occurrence_pos = []

        for line in text:
            if line.find(bottom_bound) >= 0:
                found_start = True
            if found_start:
                if line.find(upper_bound) >= 0:
                    chapter_stats.append(ChapterStat(chapter_number=chapter_count,
                                                     char_length=chapter_len,
                                                     occurrence_pos=chapter_occurrence_pos,
                                                     occ_pos_norm=[],
                                                     occ_pos_plot_loc=[]))

                    chapter_count += 1
                    bottom_bound = "Chapter " + str(chapter_count)
                    upper_bound = "Chapter " + str(chapter_count + 1)
                    chapter_len = 0
                    curr_chapter_offset = 0
                    chapter_occurrence_pos = []

                chapter_len += len(line)
                chapter_occurrence_pos.extend(search_line(search_token,
                                                          line,
                                                          curr_chapter_offset))
                curr_chapter_offset += len(line)
        chapter_stats.append(ChapterStat(chapter_number=chapter_count,
                                         char_length=chapter_len,
                                         occurrence_pos=chapter_occurrence_pos,
                                         occ_pos_norm=[],
                                         occ_pos_plot_loc=[]))
        return chapter_stats

