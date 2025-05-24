from typing import List

from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib.widgets import TextBox

from spotlight import *
from gather_stats import *

class SingletonSearchData(object):
    max_len: int
    chapters: List[Chapter]
    markers: List[Line2D]
    cur_aggregates: []
    chapter_lines: List[LineCollection]

    chapter_labels: List[Text]

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
    spotlight_manager: SpotlightWarden

    x_zoom_ratio = 1.

    # all else is plot stuff -- not ephemeral
    ax: plt.Axes
    fig: plt.Figure

    init_x_lim: float
    init_y_bounds: float
    search_term_input: TextBox

    single_render: SingleRenderDeets

    def __new__(self):
        if not hasattr(self, 'instance'):
            self.instance = super(SingletonContext, self).__new__(self)
            self.search_data = SingletonSearchData()
            self.spotlight_manager = SpotlightWarden()
            self.single_render = SingleRenderDeets()
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

    for pos in chapter.render_deets.chapter_pos_norm:
        plot_loc = line_len * pos + line_x_start
        chapter.render_deets.chapter_pos_coords.append(coords(plot_loc, y))

        temp = plt.plot(plot_loc, y,
                 marker='|', markersize=marker_size,
                 markeredgecolor=marker_default_colour)
        context.search_data.markers.extend(temp)

def vis_single():
    global context

    line_len = (line_x_end - line_x_start)
    t1 = plt.hlines(0, line_x_start, line_x_start + line_len)
    t2 = plt.vlines(line_x_start, 0 - bounds_height, 0 + bounds_height)
    t3 = plt.vlines(line_x_start + line_len, 0 - bounds_height, 0 + bounds_height)

    for occurence in monolith_stats.occurrence_pos:
        context.single_render.single_pos_norm.append(occurence / monolith_stats.char_length)

    for pos in context.single_render.single_pos_norm:
        plot_loc = line_len * pos + line_x_start

        temp = plt.plot(plot_loc, 0,
                 marker='|', markersize=marker_size,
                 markeredgecolor=marker_default_colour)


def add_chapter_label(y, chapter_num):
    x = line_x_start - chapter_label_x_pad * context.x_zoom_ratio
    context.search_data.chapter_labels.append(plt.text(x,
                                                       y - label_centre_shift,
                                                       "Chapter " + str(chapter_num),
                                                       horizontalalignment='right'
                                                       )
                                              )

def cb_x_zoom_reaggregate(axes):

    (bot, top) = axes.get_xlim()
    bounds = top - bot
    temp_ratio = bounds / context.init_x_lim
    temp_cond = abs(temp_ratio / context.x_zoom_ratio - 1) > zoom_sens
    context.x_zoom_ratio = temp_ratio
    if temp_cond:
        context.search_data.clear_aggregates()
        aggregate_all(context, aggregate_base_distance_thresh * temp_ratio)

        context.search_data.clear_chapter_labels()
        count = 0
        for chapter in context.search_data.chapters:
            add_chapter_label(top_margin * count, chapter.chapter_stat.chapter_number)
            count -= 1

def cb_y_zoom_set_pos(axes):
    global context
    (bot, top) = axes.get_ylim()
    bounds = top - bot
    if bounds != context.init_y_bounds:
        # maintain the Y size
        # TODO: maybe dont fix it to bot
        axes.set_ylim(bot, bot + context.init_y_bounds)

count = 1
def cb_xy_moved_remove_nav(axes):
    global context
    global count

    current_bounds = (context.ax.get_xlim(), context.ax.get_ylim())
    if context.spotlight_manager.spotlight_bounds != nav_init_bounds:
        if not compare_bounds_tolerance(nav_pan_cancel_sens, current_bounds, context.spotlight_manager.spotlight_bounds):
            print("oof", count)
            count += 1
            context.spotlight_manager.del_buttons()

def create_and_populate_graph():
    global context

    context.fig = plt.figure()
    context.ax = context.fig.add_subplot(1, 1, 1)
    context.ax.set_xlim(window_x_start, window_x_end)
    context.ax.set_ylim(window_y_start, window_y_end)

    (a, b) = context.ax.get_xlim()
    context.init_x_lim = b - a
    context.x_zoom_ratio = 1

    (a, b) = context.ax.get_ylim()
    context.init_y_bounds = b - a

    cb_registry = context.ax.callbacks
    cb_registry.connect('xlim_changed', cb_x_zoom_reaggregate)
    cb_registry.connect('ylim_changed', cb_y_zoom_set_pos)

    cb_registry.connect('xlim_changed', cb_xy_moved_remove_nav)
    cb_registry.connect('ylim_changed', cb_xy_moved_remove_nav)

    driver(default_search_text)
    plt.axis('off')

    context.search_term_input = TextBox(plt.axes(search_axes), "Search term")
    context.search_term_input.on_submit(refresh)

    context.spotlight_find_ax = plt.axes(spotlight_axes)
    butt = Button(context.spotlight_find_ax, "Find!")
    get_marker = context.spotlight_manager.nearest_marker_factory(context)
    butt.on_clicked(get_marker)

    plt.sca(context.ax)
    plt.show()

def driver(search_term):
    global context
    if search_term == "":
        driver(default_search_text)
        return
    chapter_stats = get_stats(search_term)
    # for chapter_stat in chapter_stats:
    #     context.search_data.chapters.append(Chapter(chapter_stat))
    # context.search_data.max_len = -1
    #
    # for chapter in context.search_data.chapters:
    #     if chapter.chapter_stat.char_length > context.search_data.max_len:
    #         context.search_data.max_len = chapter.chapter_stat.char_length
    #
    # # separate for loop, maybe less cache hit but idgad
    # for chapter in context.search_data.chapters:
    #     for i in range(len(chapter.chapter_stat.occurrence_pos)):
    #         chapter.render_deets.chapter_pos_norm.append(chapter.chapter_stat.occurrence_pos[i] / chapter.chapter_stat.char_length)
    #
    # count = 0
    # for chapter in context.search_data.chapters:
    #     vis_chapter(chapter, top_margin * count)
    #     count -= 1

    vis_single()

    aggregate_all(context, aggregate_base_distance_thresh)

def refresh(term):
    global context

    context.search_data.clear_slate()
    # context.search_term_input.remove()
    driver(term)

    #TODO
    # context.spotlight_manager.spotlight_search_scope =  context.search_data.chapters[3].render_deets.chapter_pos_coords
    #end TODO

context = SingletonContext()
create_and_populate_graph()