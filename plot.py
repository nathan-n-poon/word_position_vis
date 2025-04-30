from math import sqrt
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
    chapter_stat: gather_stats.ChapterStat

    def __init__(self, chapter_stat):
        self.render_deets = ChapterRenderDeets()
        self.chapter_stat = chapter_stat

class SingletonSearchData(object):
    max_len: int
    chapters: List[Chapter]
    markers: List[Line2D]
    cur_aggregates: []
    chapter_lines: List[LineCollection]

    chapter_labels: List[Text]

    #int is index to specific instance in chapter
    spotlight_marker: (Chapter, int)
    spotlight_search_scope: list[coords]

    def __new__(self):
        if not hasattr(self, 'instance'):
          self.instance = super(SingletonSearchData, self).__new__(self)
        self.max_len = 0
        self.chapters = []
        self.markers = []
        self.cur_aggregates = []
        self.chapter_lines = []
        self.chapter_labels = []
        self.spotlight_search_scope = []
        return self.instance

    def clear_aggregates(self):
        for aggregate in self.cur_aggregates:
            aggregate.remove()
        self.cur_aggregates = []

    def clear_search_results(self):
        for result in self.markers:
            result.remove()
        self.markers = []

    def clear_chapter_lines(self):
        for line in self.chapter_lines:
            line.remove()
        self.chapter_lines = []

    def clear_chapter_labels(self):
        for label in self.chapter_labels:
            label.remove()
        self.chapter_labels = []

    def clear_slate(self):
        self.chapters = []
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

def vis_chapter(chapter, y_offset):
    global context
    # draw lines
    y = y_offset

    line_len = (line_x_end - line_x_start) * (chapter.chapter_stat.char_length / context.search_data.max_len)

    add_chapter_label(y, chapter.chapter_stat.chapter_number)

    t1 = plt.hlines(y, line_x_start, line_x_start + line_len)
    t2 = plt.vlines(line_x_start, y - bounds_height, y + bounds_height)
    t3 = plt.vlines(line_x_start + line_len, y - bounds_height, y + bounds_height)
    context.search_data.chapter_lines.extend([t1,t2,t3])

    for pos in chapter.render_deets.occ_pos_norm:
        plot_loc = line_len * pos + line_x_start
        chapter.render_deets.occ_pos_plot_loc.append(coords(plot_loc, y))

        temp = plt.plot(plot_loc, y,
                 marker='|', markersize=marker_size,
                 markeredgecolor=marker_default_colour)
        context.search_data.markers.extend(temp)

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

    aggregate_base = locs[0].x
    aggregate_apex = locs[0].x
    aggregate_size = 1
    for idx in range(len(locs)):
        if idx == 0:
            continue
        if locs[idx].x - locs[idx - 1].x < coalesce_width:
            aggregate_apex = locs[idx].x
            aggregate_size += 1
        else:
            if aggregate_size > 1:
                add_aggregate_label(aggregate_base, y_offset, (aggregate_apex - aggregate_base), aggregate_size)
            aggregate_base = locs[idx].x
            aggregate_apex = locs[idx].x
            aggregate_size = 1
    if aggregate_size > 1:
        add_aggregate_label(aggregate_base, y_offset, (aggregate_apex - aggregate_base), aggregate_size)

def callback_x_bounds_changed(axes):
    global context
    (bot, top) = axes.get_xlim()
    bounds = top - bot
    temp_ratio = bounds / context.init_x_lim
    if abs(temp_ratio / context.x_zoom_ratio - 1) > zoom_sens:
        context.search_data.clear_aggregates()
        aggregate_all(aggregate_base_distance_thresh * temp_ratio)

        context.search_data.clear_chapter_labels()
        count = 0
        for chapter in context.search_data.chapters:
            add_chapter_label(top_margin * count, chapter.chapter_stat.chapter_number)
            count -= 1
    context.x_zoom_ratio = temp_ratio

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
    for chapter in context.search_data.chapters:
        aggregate_chapter_pos(chapter.render_deets, top_margin * count, coalesce_width)
        count -= 1

def create_and_populate_graph():
    global context

    context.fig = plt.figure()
    context.ax = context.fig.add_subplot(1, 1, 1)
    context.ax.set_xlim(window_x_start, window_x_end)
    context.ax.set_ylim(window_y_start, window_y_end)

    (a, b) = context.ax.get_xlim()
    context.init_x_lim = b - a
    context.x_zoom_ratio = context.init_x_lim

    (a, b) = context.ax.get_ylim()
    context.init_y_bounds = b - a

    cb_registry = context.ax.callbacks
    cidx = cb_registry.connect('xlim_changed', callback_x_bounds_changed)
    cidy = cb_registry.connect('ylim_changed', callback_y_bounds_changed)

    driver(default_search_text)
    plt.axis('off')

    context.search_term_input = TextBox(plt.axes(search_axes), "Search term")
    context.search_term_input.on_submit(refresh)

    #TODO
    butt = Button(plt.axes(spotlight_axes), "Nearest Marker Button!!!!")
    butt.on_clicked(get_nearest_marker)
    #end TODO

    plt.sca(context.ax)
    plt.show()

def driver(search_term):
    global context
    if search_term == "":
        driver(default_search_text)
        return
    chapter_stats = gather_stats.get_stats(search_term)
    for chapter_stat in chapter_stats:
        context.search_data.chapters.append(Chapter(chapter_stat))
    context.search_data.max_len = -1

    for chapter in context.search_data.chapters:
        if chapter.chapter_stat.char_length > context.search_data.max_len:
            context.search_data.max_len = chapter.chapter_stat.char_length

    # separate for loop, maybe less cache hit but idgad
    for chapter in context.search_data.chapters:
        for i in range(len(chapter.chapter_stat.occurrence_pos)):
            chapter.render_deets.occ_pos_norm.append(chapter.chapter_stat.occurrence_pos[i] / chapter.chapter_stat.char_length)

    count = 0
    for chapter in context.search_data.chapters:
        vis_chapter(chapter, top_margin * count)
        count -= 1

    aggregate_all(aggregate_base_distance_thresh)

def refresh(term):
    global context

    context.search_data.clear_slate()
    # context.search_term_input.remove()
    driver(term)

    #TODO
    context.search_data.spotlight_search_scope =  context.search_data.chapters[3].render_deets.occ_pos_plot_loc
    #end TODO


def get_nearest_marker(event):
    global context

    pos_list = context.search_data.spotlight_search_scope
    if len(pos_list) == 0:
        return

    (x_bot, x_top) = context.ax.get_xlim()
    (y_bot, y_top) = context.ax.get_ylim()

    centre = coords((x_bot + x_top) / 2,
              (y_bot + y_bot) / 2)

    print("centre: " + str(centre.x))
    min_dis = get_dis(centre, pos_list[0])
    min_pos = pos_list[0]
    for pos in pos_list:
        x = get_dis(centre, pos)
        if x < min_dis:
            min_dis = x
            min_pos = pos
    move_camera(min_pos)

def move_camera(target_pos: coords):
    global context
    print("moving to " + str(target_pos.x) + " ," + str(target_pos.y))
    (a, b) = context.ax.get_xlim()
    curr_width = b - a
    context.ax.set_xlim(target_pos.x - curr_width/2,
                        target_pos.x + curr_width/2)

    (a, b) = context.ax.get_ylim()
    curr_height = b - a
    context.ax.set_ylim(target_pos.y - curr_height / 2,
                        target_pos.y + curr_height / 2)


def get_dis(coords_a, coords_b):
    return sqrt(
                abs(coords_a.x - coords_b.x) ** 2 +
                abs(coords_a.y - coords_b.y) ** 2
    )

context = SingletonContext()
create_and_populate_graph()