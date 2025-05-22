from math import sqrt

from matplotlib.widgets import Button
from consts import *
import matplotlib.pyplot as plt
from types import *
from aggregate_keeper import *

class SpotlightWarden(object):

    def __init__(self, parent_context):
        self.parent_context = parent_context

    spotlight_nav_idx = 0
    spotlight_next_butt: Button
    spotlight_prev_butt: Button
    spotlight_bounds = nav_init_bounds

    spotlight_find_ax: plt.Axes
    spotlight_prev_ax: plt.Axes
    spotlight_next_ax: plt.Axes

    #int is index to specific instance in chapter
    spotlight_marker: (Chapter, int)
    spotlight_search_scope: list[coords]

    def compare_tolerance(self, tolerance: float, lhs: float, rhs: float):
        if rhs == 0.:
            rhs = 0.000001
        ratio = lhs / rhs
        if abs(ratio) > 1:
            ratio = 1 / ratio
        return tolerance < abs(ratio)

    def compare_bounds_tolerance(self, tolerance: float, lhbounds, rhbounds):
        return (self.compare_tolerance(tolerance, lhbounds[0][0], rhbounds[0][0]) and
                self.compare_tolerance(tolerance, lhbounds[0][1], rhbounds[0][1]) and
                self.compare_tolerance(tolerance, lhbounds[1][0], rhbounds[1][0]) and
                self.compare_tolerance(tolerance, lhbounds[1][1], rhbounds[1][1]))

    def del_button(self, del_me: Button):
        del_me.ax.patch.set_visible(False)
        del_me.label.set_visible(False)
        del_me.ax.axis("off")
        del del_me

    def nearest_marker_factory(self):
        def get_nearest_marker(event):
            context = self.parent_context

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
            context.spotlight_nav_idx = 0
            i = 0
            for i in range(len(pos_list)):
                x = get_dis(centre, pos_list[i])
                if x < min_dis:
                    min_dis = x
                    min_pos = pos_list[i]
                    context.spotlight_nav_idx = i
            self.move_camera(min_pos)
            self.create_nav_buttons()

        return get_nearest_marker

    def create_nav_buttons(self):
        context = self.parent_context

        pos_list = context.search_data.spotlight_search_scope

        context.spotlight_next_ax = plt.axes(nav_next_axes)
        context.spotlight_prev_ax = plt.axes(nav_prev_axes)

        butt_next = Button(context.spotlight_next_ax, ">")
        butt_prev = Button(context.spotlight_prev_ax, "<")
        plt.sca(context.ax)

        def move_factory(direction: int):
            def move_func(event):
                context.spotlight_nav_idx = (context.spotlight_nav_idx + direction) % len(pos_list)
                self.move_camera(pos_list[context.spotlight_nav_idx])

            return move_func

        butt_next.on_clicked(move_factory(1))
        butt_prev.on_clicked(move_factory(-1))
        context.spotlight_next_butt = butt_next
        context.spotlight_prev_butt = butt_prev

        return

    def move_camera(self, target_pos: coords):
        context = self.parent_context

        print("moving to " + str(target_pos.x) + " ," + str(target_pos.y))
        (a, b) = context.ax.get_xlim()
        curr_width = b - a
        bot_x = target_pos.x - curr_width / 2
        top_x = target_pos.x + curr_width / 2

        context.spotlight_bounds = ((bot_x, top_x), context.ax.get_ylim())
        context.ax.set_xlim(bot_x, top_x)

        (a, b) = context.ax.get_ylim()
        curr_height = b - a
        bot_y = target_pos.y - curr_height / 2
        top_y = target_pos.y + curr_height / 2

        context.spotlight_bounds = ((bot_x, top_x), (bot_y, top_y))
        context.ax.set_ylim(bot_y, top_y)

    def get_dis(self, coords_a, coords_b):
        return sqrt(
            abs(coords_a.x - coords_b.x) ** 2 +
            abs(coords_a.y - coords_b.y) ** 2
        )
