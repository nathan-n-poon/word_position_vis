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
    segments: List[Segment]
    markers: List[Line2D]
    cur_aggregates: []
    segment_lines: List[LineCollection]

    segment_labels: List[Text]

    single_view_markers: List[Line2D]
    single_view_lines: List[LineCollection]

    single_view_render: SingleViewRenderDeets

    def __new__(self):
        if not hasattr(self, 'instance'):
          self.instance = super(SingletonSearchData, self).__new__(self)
        self.max_len = 0
        self.segments = []
        self.markers = []
        self.cur_aggregates = []
        self.segment_lines = []
        self.segment_labels = []
        self.spotlight_search_scope = []
        self.single_view_markers = []
        self.single_view_lines = []
        self.single_view_render = SingleViewRenderDeets()
        return self.instance

    def erase_and_clear(self, clear_me):
        for i in clear_me:
            i.remove()
        clear_me.clear()

    def clear_list(self, clear_me):
        clear_me.clear()

    def clear_slate(self):
        self.segments = []
        self.erase_and_clear(self.cur_aggregates)
        self.erase_and_clear(self.markers)
        self.erase_and_clear(self.segment_lines)
        self.erase_and_clear(self.segment_labels)
        self.erase_and_clear(self.single_view_markers)
        self.erase_and_clear(self.single_view_lines)
        self.clear_list(self.single_view_render.single_view_pos_norm)
        self.clear_list(self.single_view_render.single_view_pos_segments)
        self.clear_list(self.single_view_render.single_view_pos_coords)


# global context
class SingletonContext(object):
    #all this data is ephemeral -- changes with each search
    search_data: SingletonSearchData
    spotlight_manager: SpotlightWarden

    x_zoom_ratio: float

    # all else is plot stuff -- not ephemeral
    ax: plt.Axes
    fig: plt.Figure

    init_x_lim: float
    init_y_bounds: float
    search_term_input: TextBox

    view_mode: ViewMode

    def __new__(self):
        if not hasattr(self, 'instance'):
            self.x_zoom_ratio = 1.
            self.instance = super(SingletonContext, self).__new__(self)
            self.search_data = SingletonSearchData()
            self.spotlight_manager = SpotlightWarden()
            self.view_mode = ViewMode.Monolithic
        return self.instance

def vis_chapter(chapter, y_offset):
    global context
    # draw lines
    y = y_offset

    line_len = (line_x_end - line_x_start) * (chapter.segment_stat.char_length / context.search_data.max_len)

    add_chapter_label(y, chapter.segment_stat.chapter_number)

    t1 = plt.hlines(y, line_x_start, line_x_start + line_len)
    t2 = plt.vlines(line_x_start, y - bounds_height, y + bounds_height)
    t3 = plt.vlines(line_x_start + line_len, y - bounds_height, y + bounds_height)
    context.search_data.segment_lines.extend([t1, t2, t3])

    for pos in chapter.render_deets.segment_pos_norm:
        plot_loc = line_len * pos + line_x_start
        chapter.render_deets.segment_pos_coords.append(coords(plot_loc, y))

        temp = plt.plot(plot_loc, y,
                 marker='|', markersize=marker_size,
                 markeredgecolor=marker_default_colour)
        context.search_data.markers.extend(temp)

def add_chapter_label(y, chapter_num):
    x = line_x_start - chapter_label_x_pad * context.x_zoom_ratio
    context.search_data.segment_labels.append(plt.text(x,
                                                       y - label_centre_shift,
                                                       "Chapter " + str(chapter_num),
                                                       horizontalalignment='right'
                                                       )
                                              )

def vis_single(occurrence_pos, char_length):
    global context

    line_len = (line_x_end - line_x_start)
    t1 = plt.hlines(0, line_x_start, line_x_start + line_len)
    t2 = plt.vlines(line_x_start, 0 - bounds_height, 0 + bounds_height)
    t3 = plt.vlines(line_x_start + line_len, 0 - bounds_height, 0 + bounds_height)

    context.search_data.single_view_lines.extend([t1, t2, t3])

    for occurrence in occurrence_pos:
        context.search_data.single_view_render.single_view_pos_norm.append(occurrence / char_length)

    for pos in context.search_data.single_view_render.single_view_pos_norm:
        plot_loc = line_len * pos + line_x_start

        temp = plt.plot(plot_loc, 0,
                 marker='|', markersize=marker_size,
                 markeredgecolor=marker_default_colour)
        context.search_data.single_view_markers.extend(temp)

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
        for chapter in context.search_data.segments:
            add_chapter_label(top_margin * count, chapter.segment_stat.chapter_number)
            count -= 1

def cb_y_zoom_set_pos(axes):
    global context
    (bot, top) = axes.get_ylim()
    bounds = top - bot
    if bounds != context.init_y_bounds:
        # maintain the Y size
        # TODO: maybe dont fix it to bot
        axes.set_ylim(bot, bot + context.init_y_bounds)

def cb_xy_moved_remove_nav(axes):
    global context

    current_bounds = (context.ax.get_xlim(), context.ax.get_ylim())
    if context.spotlight_manager.spotlight_bounds != nav_init_bounds:
        if not compare_bounds_tolerance(nav_pan_cancel_sens, current_bounds, context.spotlight_manager.spotlight_bounds):
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
            context.search_data.segments.append(Segment(chapter_stat))
        context.search_data.max_len = -1

        for chapter in context.search_data.segments:
            if chapter.segment_stat.char_length > context.search_data.max_len:
                context.search_data.max_len = chapter.segment_stat.char_length

        for chapter in context.search_data.segments:
            for i in range(len(chapter.segment_stat.occurrence_pos)):
                chapter.render_deets.segment_pos_norm.append(chapter.segment_stat.occurrence_pos[i] / chapter.segment_stat.char_length)

        count = 0
        for chapter in context.search_data.segments:
            vis_chapter(chapter, top_margin * count)
            count -= 1

    aggregate_all(context, aggregate_base_distance_thresh)

class ToggleButton(object):
    global context
    label: str
    butt: Button
    desc: Text
    ax: plt.Axes

    def __init__(self):
        self.label = "Toggle View"
        self.ax = plt.axes(view_toggle_axes)
        self.butt = Button(self.ax, self.label)
        self.butt.on_clicked(self.toggle_view_factory())
        self.desc = plt.text(view_toggle_left[0], view_toggle_left[1], "Single View")
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
                self.desc = plt.text(view_toggle_left[0], view_toggle_left[1], "Monolithic View")
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