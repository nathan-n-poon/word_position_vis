import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import gather_stats

# constants
top_margin = 1
chapter_disp_height = 1
bounds_height = chapter_disp_height / 3.
marker_size = 10

z_order_inc = 5
z_order_line_graph = 0
z_order_marker = z_order_line_graph + z_order_inc
z_order_aggregate = z_order_marker + z_order_inc
z_order_aggregate_label = z_order_aggregate + z_order_inc

marker_default_colour = (0.75, 0.75, 0.5)
aggregate_proportional_redshift = 0.05

# 0.1 works on my display :P
aggregate_label_centre_shift = 0.1
aggregate_base_distance_thresh = 0.3

window_x_start = 0
window_x_end = 10
line_x_pad = 1
line_x_start = window_x_start + line_x_pad
line_x_end = window_x_end - line_x_pad
window_y_start = 0
window_y_end = 10

# global context
class SingletonContext(object):
    cur_aggregates: []
    max_len: int

    # plot stuff
    ax: plt.Axes

    init_x_lim: float
    prex_x_bounds: float
    init_y_bounds: float
    chapters_stats: [gather_stats.ChapterStat]
    def __new__(self):
        if not hasattr(self, 'instance'):
          self.instance = super(SingletonContext, self).__new__(self)
        self.cur_aggregates = []
        return self.instance

    def clear_aggregates(self):
        for aggregate in self.cur_aggregates:
            aggregate.remove()
        self.cur_aggregates = []

def vis_chapter(chapter_stats, y_offset):
    global context
    # draw lines
    y = y_offset

    line_len = (line_x_end - line_x_start) * (chapter_stats.char_length / context.max_len)

    plt.hlines(y, line_x_start, line_x_start + line_len)
    plt.vlines(line_x_start, y - bounds_height, y + bounds_height)
    plt.vlines(line_x_start + line_len, y - bounds_height, y + bounds_height)

    for pos in chapter_stats.occ_pos_norm:
        plot_loc = line_len * pos + line_x_start
        plt.plot(plot_loc, y,
                 marker='|', markersize=marker_size,
                 markeredgecolor=marker_default_colour)
        chapter_stats.occ_pos_plot_loc.append(plot_loc)

def add_aggregate_label(x, y, width, aggregate_size):
    global context

    # redshift the larger the aggregate
    green_val = max(0, 1 - (aggregate_proportional_redshift * aggregate_size))
    new_patch = Rectangle((x, y - bounds_height), width, 2 * bounds_height,
                          zorder=z_order_aggregate,
                          color=(1, green_val, 0))
    context.cur_aggregates.append(new_patch)
    context.ax.add_patch(new_patch)
    context.cur_aggregates.append(plt.text(x + width / 2 - aggregate_label_centre_shift,
                                           y - aggregate_label_centre_shift,
                                           str(aggregate_size), zorder=z_order_aggregate_label))

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
        if locs[idx] - locs[idx - 1] < coalesce_width:
            aggregate_apex = locs[idx]
            aggregate_size += 1
        else:
            if aggregate_size > 1:
                add_aggregate_label(aggregate_base, y_offset, (aggregate_apex - aggregate_base), aggregate_size)
            aggregate_base = locs[idx]
            aggregate_apex = locs[idx]
            aggregate_size = 1
    if aggregate_size > 1:
        add_aggregate_label(aggregate_base, y_offset, (aggregate_apex - aggregate_base), aggregate_size)

def callback_x_bounds_changed(axes):
    global context

    (bot, top) = axes.get_xlim()
    bounds = round(top) - round(bot)
    if bounds != context.prex_x_bounds:
        context.clear_aggregates()
        aggregate_all(aggregate_base_distance_thresh * bounds / context.init_x_lim)
        context.prex_x_bounds = bounds

def callback_y_bounds_changed(axes):
    global context

    (bot, top) = axes.get_ylim()
    bounds = round(top) - round(bot)
    if bounds != context.init_y_bounds:
        # maintain the Y size
        # TODO: maybe dont fix it to bot
        axes.set_ylim(bot, bot + context.init_y_bounds)

def aggregate_all(coalesce_width):
    global context

    count = 0
    for chapter_stats in context.chapters_stats:
        aggregate_chapter_pos(chapter_stats, top_margin * count, coalesce_width)
        count -= 1

def create_and_populate_graph():
    global context

    context.fig = plt.figure()
    context.ax = context.fig.add_subplot(111)

    context.chapters_stats = gather_stats.get_chapters_stats("and")
    context.max_len = -1

    for chapter_stats in context.chapters_stats:
        if chapter_stats.char_length > context.max_len:
            context.max_len = chapter_stats.char_length

    # separate for loop, maybe less cache hit but idgad
    for chapter_stats in context.chapters_stats:
        for i in range(len(chapter_stats.occurrence_pos)):
            chapter_stats.occ_pos_norm.append(chapter_stats.occurrence_pos[i] / chapter_stats.char_length)

    context.ax.set_xlim(window_x_start, window_x_end)
    context.ax.set_ylim(window_y_start, window_y_end)

    count = 0
    for chapter_stats in context.chapters_stats:
        vis_chapter(chapter_stats, top_margin * count)
        count -= 1

    aggregate_all(aggregate_base_distance_thresh)

    (a, b) = context.ax.get_xlim()
    context.init_x_lim = round(b) - round(a)
    context.prex_x_bounds = context.init_x_lim

    (a, b) = context.ax.get_ylim()
    context.init_y_bounds = round(b) - round(a)

    cb_registry = context.ax.callbacks
    cidx = cb_registry.connect('xlim_changed', callback_x_bounds_changed)
    cidy = cb_registry.connect('ylim_changed', callback_y_bounds_changed)

    plt.axis('off')
    plt.show()

context = SingletonContext()
create_and_populate_graph()