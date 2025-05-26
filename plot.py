from typing import List

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib.widgets import TextBox

import gather_stats
from spotlight import *
from gather_stats import *

#TODO: maybe split into monolith and chapters
# inheritance?
class SingletonSearchData(object):
    max_len: int
    chapters: List[Chapter]
    markers: List[Line2D]
    cur_aggregates: []
    chapter_lines: List[LineCollection]

    chapter_labels: List[Text]

    monolith_markers: List[Line2D]
    monolith_lines: List[LineCollection]

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
        self.monolith_markers = []
        self.monolith_lines = []
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

    def clear_monolith_markers(self):
        for marker in self.monolith_markers:
            marker.remove()
        self.monolith_markers = []

    def clear_monolith_lines(self):
        for line in self.monolith_lines:
            line.remove()
        self.monolith_lines = []

    def clear_slate(self):
        self.chapters = []
        self.clear_aggregates()
        self.clear_search_results()
        self.clear_chapter_lines()
        self.clear_chapter_labels()
        self.clear_monolith_markers()
        self.clear_monolith_lines()

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

    view_mode: ViewMode

    def __new__(self):
        if not hasattr(self, 'instance'):
            self.instance = super(SingletonContext, self).__new__(self)
            self.search_data = SingletonSearchData()
            self.spotlight_manager = SpotlightWarden()
            self.single_render = SingleRenderDeets()
            self.view_mode = ViewMode.Monolithic
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

def vis_single(occurrence_pos, char_length):
    global context

    line_len = (line_x_end - line_x_start)
    t1 = plt.hlines(0, line_x_start, line_x_start + line_len)
    t2 = plt.vlines(line_x_start, 0 - bounds_height, 0 + bounds_height)
    t3 = plt.vlines(line_x_start + line_len, 0 - bounds_height, 0 + bounds_height)

    context.search_data.monolith_lines.extend([t1,t2,t3])

    for occurrence in occurrence_pos:
        context.single_render.single_pos_norm.append(occurrence / char_length)

    for pos in context.single_render.single_pos_norm:
        plot_loc = line_len * pos + line_x_start

        temp = plt.plot(plot_loc, 0,
                 marker='|', markersize=marker_size,
                 markeredgecolor=marker_default_colour)
        context.search_data.monolith_markers.extend(temp)


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

    view_mode_toggle_butt = ToggleButton()

    plt.sca(context.ax)
    plt.show()

def driver(search_term):
    global context
    if search_term == "":
        driver(default_search_text)
        return

    if context.view_mode == ViewMode.Monolithic:
        data = gather_stats.get_stats(search_term, ViewMode.Monolithic)[0]
        vis_single(data.monolith_stats.occurrence_pos, data.monolith_stats.char_length)

    elif context.view_mode == ViewMode.Chapters:
        data = get_stats(search_term, ViewMode.Chapters)[0]
        chapter_stats = data.chapter_stats

        for chapter_stat in chapter_stats:
            context.search_data.chapters.append(Chapter(chapter_stat))
        context.search_data.max_len = -1

        for chapter in context.search_data.chapters:
            if chapter.chapter_stat.char_length > context.search_data.max_len:
                context.search_data.max_len = chapter.chapter_stat.char_length

        for chapter in context.search_data.chapters:
            for i in range(len(chapter.chapter_stat.occurrence_pos)):
                chapter.render_deets.chapter_pos_norm.append(chapter.chapter_stat.occurrence_pos[i] / chapter.chapter_stat.char_length)

        count = 0
        for chapter in context.search_data.chapters:
            vis_chapter(chapter, top_margin * count)
            count -= 1

    aggregate_all(context, aggregate_base_distance_thresh)

class ToggleButton(object):
    global context
    label = "Toggle View"
    butt: Button
    desc: Text
    ax: plt.Axes

    def __init__(self):
        self.ax = plt.axes(view_toggle_axes)
        self.butt = Button(self.ax, self.label)
        self.butt.on_clicked(self.toggle_view_factory())
        plt.sca(context.ax)

    def toggle_view_factory(self):
        def toggle_view(event):
            if context.view_mode == ViewMode.Monolithic:
                context.view_mode = ViewMode.Chapters
            else:
                context.view_mode = ViewMode.Monolithic

            plt.sca(self.ax)
            if hasattr(self, "desc"):
                self.desc.set_visible(False)
                self.desc.remove()
                del self.desc
            if context.view_mode == ViewMode.Monolithic:
                self.desc = plt.text(view_toggle_left[0], view_toggle_left[1], "Single View")
            else:
                self.desc = plt.text(view_toggle_right[0], view_toggle_right[1], "Chapters View")
            plt.sca(context.ax)
            refresh(context.search_term_input.text)
        return toggle_view



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