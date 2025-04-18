from typing import List

import matplotlib
import matplotlib.pyplot as plt
from fontTools.unicodedata import block
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from matplotlib.widgets import Button, TextBox

import gather_stats
from consts import *

class SingletonSearchData(object):
    max_len: int
    chapters_stats: List[gather_stats.ChapterStat]
    search_results: List[Line2D]
    cur_aggregates: []
    chapter_lines: List[LineCollection]

    chapter_labels: List[Text]

    def __new__(self):
        if not hasattr(self, 'instance'):
          self.instance = super(SingletonSearchData, self).__new__(self)
        self.max_len = 0
        self.chapters_stats = []
        self.search_results = []
        self.cur_aggregates = []
        self.chapter_lines = []
        self.chapter_labels = []
        return self.instance

    def clear_aggregates(self):
        for aggregate in self.cur_aggregates:
            aggregate.remove()
        self.cur_aggregates = []

    def clear_search_results(self):
        for result in self.search_results:
            result.remove()
        self.search_results = []

    def clear_chapter_lines(self):
        for line in self.chapter_lines:
            line.remove()
        self.chapter_lines = []

    def clear_chapter_labels(self):
        for label in self.chapter_labels:
            label.remove()
        self.chapter_labels = []

    def clear_slate(self):
        self.chapters_stats = []
        self.clear_aggregates()
        self.clear_search_results()
        self.clear_chapter_lines()
        self.clear_chapter_labels()

# global context
class SingletonContext(object):
    #all this data is ephemeral -- changes with each search
    search_data: SingletonSearchData

    x_zoom_ratio = 1.

    # all else is plot stuff -- not ephemeral
    ax: plt.Axes
    fig: plt.Figure

    init_x_lim: float
    init_y_bounds: float
    search_term_input: TextBox

    def __new__(self):
        if not hasattr(self, 'instance'):
          self.instance = super(SingletonContext, self).__new__(self)
          self.search_data = SingletonSearchData()
        return self.instance

def vis_chapter(chapter_stats, y_offset):
    global context
    # draw lines
    y = y_offset

    line_len = (line_x_end - line_x_start) * (chapter_stats.char_length / context.search_data.max_len)

    add_chapter_label(y, chapter_stats.chapter_number)

    t1 = plt.hlines(y, line_x_start, line_x_start + line_len)
    t2 = plt.vlines(line_x_start, y - bounds_height, y + bounds_height)
    t3 = plt.vlines(line_x_start + line_len, y - bounds_height, y + bounds_height)
    context.search_data.chapter_lines.extend([t1,t2,t3])

    for pos in chapter_stats.occ_pos_norm:
        plot_loc = line_len * pos + line_x_start
        chapter_stats.occ_pos_plot_loc.append(plot_loc)

        temp = plt.plot(plot_loc, y,
                 marker='|', markersize=marker_size,
                 markeredgecolor=marker_default_colour)
        context.search_data.search_results.extend(temp)

def add_aggregate_label(x, y, width, aggregate_size):
    global context

    # redshift the larger the aggregate
    green_val = max(0, 1 - (aggregate_proportional_redshift * aggregate_size))
    new_patch = Rectangle((x, y - bounds_height), width, 2 * bounds_height,
                          zorder=z_order_aggregate,
                          color=(1, green_val, 0))
    context.search_data.cur_aggregates.append(new_patch)
    context.ax.add_patch(new_patch)
    context.search_data.cur_aggregates.append(plt.text(x + width / 2 - aggregate_label_centre_shift * context.x_zoom_ratio,
                                           y - label_centre_shift,
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
    bounds = top - bot
    context.x_zoom_ratio = bounds / context.init_x_lim
    if bounds / context.init_x_lim != 1:
        context.search_data.clear_aggregates()
        aggregate_all(aggregate_base_distance_thresh * context.x_zoom_ratio)

        context.search_data.clear_chapter_labels()
        count = 0
        for chapter in context.search_data.chapters_stats:
            add_chapter_label(top_margin * count, chapter.chapter_number)
            count -= 1

def add_chapter_label(y, chapter_num):
    x = line_x_start - chapter_label_x_pad * context.x_zoom_ratio
    context.search_data.chapter_labels.append(plt.text(x,
                                                       y - label_centre_shift,
                                                       "Chapter " + str(chapter_num),
                                                       horizontalalignment='right'
                                                       )
                                              )

def callback_y_bounds_changed(axes):
    global context

    (bot, top) = axes.get_ylim()
    bounds = top - bot
    if bounds != context.init_y_bounds:
        # maintain the Y size
        # TODO: maybe dont fix it to bot
        axes.set_ylim(bot, bot + context.init_y_bounds)

def aggregate_all(coalesce_width):
    global context

    count = 0
    for chapter_stats in context.search_data.chapters_stats:
        aggregate_chapter_pos(chapter_stats, top_margin * count, coalesce_width)
        count -= 1

def create_and_populate_graph():
    global context

    context.fig = plt.figure()
    context.ax = context.fig.add_subplot(1, 1, 1)
    context.ax.set_xlim(window_x_start, window_x_end)
    context.ax.set_ylim(window_y_start, window_y_end)

    (a, b) = context.ax.get_xlim()
    context.init_x_lim = b - a

    (a, b) = context.ax.get_ylim()
    context.init_y_bounds = b - a

    cb_registry = context.ax.callbacks
    cidx = cb_registry.connect('xlim_changed', callback_x_bounds_changed)
    cidy = cb_registry.connect('ylim_changed', callback_y_bounds_changed)

    driver(default_search_text)
    plt.axis('off')

    context.search_term_input = TextBox(plt.axes([0.2, 0.85, 0.1, 0.05]), "Search term")
    context.search_term_input.on_submit(refresh)
    plt.sca(context.ax)
    plt.show()

def driver(search_term):
    global context
    if search_term == "":
        driver(default_search_text)
        return
    context.search_data.chapters_stats = gather_stats.get_chapters_stats(search_term)
    context.search_data.max_len = -1

    for chapter_stats in context.search_data.chapters_stats:
        if chapter_stats.char_length > context.search_data.max_len:
            context.search_data.max_len = chapter_stats.char_length

    # separate for loop, maybe less cache hit but idgad
    for chapter_stats in context.search_data.chapters_stats:
        for i in range(len(chapter_stats.occurrence_pos)):
            chapter_stats.occ_pos_norm.append(chapter_stats.occurrence_pos[i] / chapter_stats.char_length)

    count = 0
    for chapter_stats in context.search_data.chapters_stats:
        vis_chapter(chapter_stats, top_margin * count)
        count -= 1

    aggregate_all(aggregate_base_distance_thresh)

def refresh(term):
    global context

    print("refresh")
    context.search_data.clear_slate()
    # context.search_term_input.remove()
    driver(term)

context = SingletonContext()
create_and_populate_graph()