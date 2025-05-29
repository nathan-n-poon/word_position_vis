from math import sqrt

from matplotlib.widgets import Button
from my_types import *
from aggregate_keeper import *


def del_button(del_me: Button):
    del_me.ax.patch.set_visible(False)
    del_me.label.set_visible(False)
    del_me.ax.axis("off")
    del del_me

def compare_tolerance(tolerance: float, lhs: float, rhs: float):
    if rhs == 0.:
        rhs = 0.000001
    ratio = lhs / rhs
    if abs(ratio) > 1:
        ratio = 1 / ratio
    return tolerance < abs(ratio)

def compare_bounds_tolerance(tolerance: float, lhbounds, rhbounds):
    return (compare_tolerance(tolerance, lhbounds[0][0], rhbounds[0][0]) and
            compare_tolerance(tolerance, lhbounds[0][1], rhbounds[0][1]) and
            compare_tolerance(tolerance, lhbounds[1][0], rhbounds[1][0]) and
            compare_tolerance(tolerance, lhbounds[1][1], rhbounds[1][1]))


def get_dis(coords_a, coords_b):
    return sqrt(
        abs(coords_a.x - coords_b.x) ** 2 +
        abs(coords_a.y - coords_b.y) ** 2
    )


class SpotlightWarden(object):
    spotlight_nav_idx: int
    spotlight_next_butt: Button
    spotlight_prev_butt: Button
    spotlight_bounds = nav_init_bounds

    spotlight_find_ax: plt.Axes
    spotlight_prev_ax: plt.Axes
    spotlight_next_ax: plt.Axes

    #int is index to specific instance in chapter
    spotlight_marker: (Segment, int)
    spotlight_search_scope: list[coords]

    def __init__(self):
        self.spotlight_nav_idx = 0

    def del_buttons(self):
        if hasattr(self, "spotlight_next_butt") and hasattr(self, "spotlight_prev_butt"):
            del_button(self.spotlight_next_butt)
            del_button(self.spotlight_prev_butt)

    def nearest_marker_factory(self, context):
        def get_nearest_marker(event):

            pos_list = self.spotlight_search_scope
            if len(pos_list) == 0:
                return

            (x_bot, x_top) = context.ax.get_xlim()
            (y_bot, y_top) = context.ax.get_ylim()

            centre = coords((x_bot + x_top) / 2,
                            (y_bot + y_bot) / 2)

            print("centre: " + str(centre.x))
            min_dis = get_dis(centre, pos_list[0])
            min_pos = pos_list[0]
            self.spotlight_nav_idx = 0
            for i in range(len(pos_list)):
                x = get_dis(centre, pos_list[i])
                if x < min_dis:
                    min_dis = x
                    min_pos = pos_list[i]
                    self.spotlight_nav_idx = i
            self.move_camera(context, min_pos)
            self.create_nav_buttons(context)

        return get_nearest_marker

    def create_nav_buttons(self, context):
        pos_list = self.spotlight_search_scope

        self.spotlight_next_ax = plt.axes(nav_next_axes)
        self.spotlight_prev_ax = plt.axes(nav_prev_axes)

        butt_next = Button(self.spotlight_next_ax, ">")
        butt_prev = Button(self.spotlight_prev_ax, "<")
        plt.sca(context.ax)

        def move_factory(direction: int):
            def move_func(event):
                self.spotlight_nav_idx = (self.spotlight_nav_idx + direction) % len(pos_list)
                self.move_camera(context, pos_list[self.spotlight_nav_idx])

            return move_func

        butt_next.on_clicked(move_factory(1))
        butt_prev.on_clicked(move_factory(-1))
        self.del_buttons()
        self.spotlight_next_butt = butt_next
        self.spotlight_prev_butt = butt_prev

        return

    def move_camera(self, context, target_pos: coords):
        # print("moving to " + str(target_pos.x) + " ," + str(target_pos.y))
        (a, b) = context.ax.get_xlim()
        curr_width = b - a
        bot_x = target_pos.x - curr_width / 2
        top_x = target_pos.x + curr_width / 2

        self.spotlight_bounds = ((bot_x, top_x), context.ax.get_ylim())
        context.ax.set_xlim(bot_x, top_x)

        (a, b) = context.ax.get_ylim()
        curr_height = b - a
        bot_y = target_pos.y - curr_height / 2
        top_y = target_pos.y + curr_height / 2

        self.spotlight_bounds = ((bot_x, top_x), (bot_y, top_y))
        context.ax.set_ylim(bot_y, top_y)
