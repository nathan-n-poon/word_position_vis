from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

from consts import *

def add_aggregate_label(context, x, y, width, aggregate_size):
    # redshift the larger the aggregate
    green_val = max(0, 1 - (aggregate_proportional_redshift * aggregate_size))
    new_patch = Rectangle((x, y - bounds_height), width, 2 * bounds_height,
                          zorder=z_order_aggregate,
                          color=(1, green_val, 0))
    context.search_data.cur_aggregates.append(new_patch)
    context.ax.add_patch(new_patch)

    context.search_data.cur_aggregates.append(plt.text(
                                           x + width / 2 - aggregate_label_centre_shift * context.x_zoom_ratio,
                                           y - label_centre_shift,
                                           str(aggregate_size), zorder=z_order_aggregate_label))

def aggregate_chapter_pos(context, chapter_stats, y_offset, coalesce_width):
    # cute alias
    locs = chapter_stats.chapter_pos_coords
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
                add_aggregate_label(context, aggregate_base, y_offset, (aggregate_apex - aggregate_base), aggregate_size)
            aggregate_base = locs[idx].x
            aggregate_apex = locs[idx].x
            aggregate_size = 1
    if aggregate_size > 1:
        add_aggregate_label(context, aggregate_base, y_offset, (aggregate_apex - aggregate_base), aggregate_size)

def aggregate_all(context, coalesce_width):
    count = 0
    for chapter in context.search_data.chapters:
        aggregate_chapter_pos(context, chapter.render_deets, top_margin * count, coalesce_width)
        count -= 1