from enum import Enum

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

chapter_label_x_pad = 0.1
label_centre_shift = 0.125

zoom_sens = 0.01

top_y = 0.85
butt_height = 0.05

search_x = 0.2
search_axes = [search_x, top_y, 0.1, butt_height]

spotlight_butt_width = 0.1
spotlight_x = 0.8
spotlight_y = top_y
spotlight_axes = [spotlight_x,                          spotlight_y,               spotlight_butt_width,   butt_height]
nav_prev_axes =  [spotlight_x,                          spotlight_y - butt_height, spotlight_butt_width/2, butt_height]
nav_next_axes = [ spotlight_x + spotlight_butt_width/2, spotlight_y - butt_height, spotlight_butt_width/2, butt_height]
nav_init_bounds = ((0., 0.), (0., 0.))
nav_pan_cancel_sens = 0.9

view_toggle_x = (search_x + spotlight_x) / 2
view_toggle_y = top_y
view_toggle_width = 0.15
view_toggle_axes = [ view_toggle_x, view_toggle_y,               view_toggle_width, butt_height]
view_toggle_left = [ view_toggle_x, view_toggle_y - butt_height, view_toggle_width, butt_height]
view_toggle_right = [view_toggle_x, view_toggle_y - butt_height, view_toggle_width, butt_height]



default_search_text = "an improbable text a̶n̶d̴ ̶s̶o̷m̶e̵ ̵u̸n̶i̵c̶o̶d̵e̸ ̶m̸a̶d̸n̸e̵s̵s̶!̴"
chapter_delim = "Chapter "

class ViewMode(Enum):
    All = 1
    Chapters = 2
    Monolithic = 3