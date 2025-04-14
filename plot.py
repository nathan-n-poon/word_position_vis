from curses.textpad import Textbox

import matplotlib.pyplot as plt
from matplotlib.axis import YAxis, XAxis
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1.axes_size import AxesY

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

def add_aggregate_label(x, y, width, aggregate_size):
    # redshift the larger the aggregate
    green_val = max(0, 1 - (0.05 * aggregate_size))
    new_patch = Rectangle((x, y-marker_height), width, 2 * marker_height,
                           zorder=10,
                           color=(1, green_val, 0))
    cur_aggregates.append(new_patch)
    ax.add_patch(new_patch)
    # 0.1 works on my display :P
    cur_aggregates.append(plt.text(x + width/2 - 0.1, y - 0.1, str(aggregate_size), zorder=11))

cur_aggregates = []
def aggregate_chapter_pos(chapter_stats, y_offset, coalesce_width):
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
                add_aggregate_label(aggregate_base, y_offset, (aggregate_apex - aggregate_base), aggregate_size)
                # ax.add_patch(Textbox())
            aggregate_base = locs[idx]
            aggregate_apex = locs[idx]
            aggregate_size = 1
    if aggregate_size > 1:
        add_aggregate_label(aggregate_base, y_offset, (aggregate_apex - aggregate_base), aggregate_size)

def xLimChanged(axes):
    global cur_aggregates
    global prev_x_lim
    (bot, top) = axes.get_xlim()
    bounds = round(top) - round(bot)
    if bounds != prev_x_lim:
        for aggregate in cur_aggregates:
            aggregate.remove()
        cur_aggregates = []
        print("calling aggregate all with: " + str(0.3 * bounds/init_x_lim))
        aggregate_all(0.3 * bounds/init_x_lim)
        prev_x_lim = bounds
def yLimChanged(axes):
    global init_y_lim
    (bot, top) = axes.get_ylim()
    bounds = round(top) - round(bot)
    if bounds != init_y_lim:
        axes.set_ylim(bot, bot+init_y_lim)
        (bot, top) = axes.get_ylim()
        bounds = round(top) - round(bot)
        print("bounds are "+ str(bounds))

def aggregate_all(coalesce_width):
    count = 1
    for chapter_stats in chapters_stats:
        aggregate_chapter_pos(chapter_stats, top_margin * -count, coalesce_width)
        count += 1

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

aggregate_all(0.3)

(a, b) = ax.get_xlim()
init_x_lim = round(b) - round(a)
prev_x_lim = init_x_lim
(a, b) = ax.get_ylim()
init_y_lim = round(b) - round(a)
cb_registry = ax.callbacks
cidx = cb_registry.connect('xlim_changed', xLimChanged)
cidy = cb_registry.connect('ylim_changed', yLimChanged)

plt.axis('off')
plt.show()