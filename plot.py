from curses.textpad import Textbox

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import gather_stats

height = 1
marker_height = height / 3.
def vis_chapter(chapter_stats, y_offset):
    # draw lines
    xmin = 1
    xmax = 9
    y = y_offset

    line_len = (xmax - xmin) * chapter_stats.char_length/max_len
    plt.hlines(y, xmin, xmin + line_len)
    plt.vlines(xmin, y - marker_height, y + marker_height)
    plt.vlines(xmin + line_len, y - marker_height, y + marker_height)

    for pos in chapter_stats.occ_pos_norm:
        plot_loc = line_len * pos + xmin
        plt.plot(plot_loc, y,
                 marker='|', markersize=10,
                 markeredgecolor='#e8bd79',)
        chapter_stats.occ_pos_plot_loc.append(plot_loc)

def add_aggregate_label(x, y, width):
    ax.add_patch(Rectangle((x,y-marker_height), width, 2*marker_height))


def aggregate_chapter_pos(chapter_stats, y_offset):
    coalesce_width = 0.3

    # cute alias
    locs = chapter_stats.occ_pos_plot_loc
    if len(locs) < 1:
        return

    aggregate_base = locs[0]
    aggregate_apex = locs[0]
    aggregate_size = 1
    for idx in range(len(locs)):
        if idx == 0:
            continue
        dbg = locs[idx] - locs[idx - 1]
        if locs[idx] - locs[idx - 1] < coalesce_width:
            aggregate_apex = locs[idx]
            aggregate_size += 1
        else:
            if aggregate_size > 1:
                add_aggregate_label(aggregate_base, y_offset, (aggregate_apex - aggregate_base))
                # ax.add_patch(Textbox())
            aggregate_base = locs[idx]
            aggregate_apex = locs[idx]
            aggregate_size = 1
    if aggregate_size > 1:
        add_aggregate_label(aggregate_base, y_offset, (aggregate_apex - aggregate_base))

fig = plt.figure()
ax = fig.add_subplot(111)

chapters_stats = gather_stats.get_chapters_stats("and")
max_len = -1

for chapter_stats in chapters_stats:
    if chapter_stats.char_length > max_len:
        max_len = chapter_stats.char_length

# separate for loop, maybe less cache hit but idgad
for chapter_stats in chapters_stats:
    for i in range(len(chapter_stats.occurrence_pos)):
        chapter_stats.occ_pos_norm.append(chapter_stats.occurrence_pos[i] / chapter_stats.char_length)

side_margin = 1
top_margin = 1

vertical_offset = 0

ax.set_xlim(0,10)
ax.set_ylim(0,10)

count = 1
for chapter_stats in chapters_stats:
    vis_chapter(chapter_stats, top_margin * -count)
    count += 1

count = 1
for chapter_stats in chapters_stats:
    aggregate_chapter_pos(chapter_stats, top_margin * -count)
    count += 1

plt.axis('off')
plt.show()

