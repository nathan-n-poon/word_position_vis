import matplotlib.pyplot as plt
import gather_stats

def vis_chapter(chapter_stats, y_offset):
    # draw lines
    xmin = 1
    xmax = 9
    y = y_offset
    height = 1

    line_len = (xmax - xmin) * chapter_stats.char_length/max_len
    plt.hlines(y, xmin, xmin + line_len)
    y_span = height / 3.
    plt.vlines(xmin, y - y_span, y + y_span)
    plt.vlines(xmin + line_len, y - y_span, y + y_span)

    for pos in chapter_stats.occ_pos_norm:
        dbg = line_len * pos + xmin
        print(pos, dbg)
        dbg2 = pos
        plt.plot(dbg, y, 'ro', markersize=10, markerfacecolor='r')

chapters_stats = gather_stats.get_chapters_stats("and")
max_len = -1

for chapter_stats in chapters_stats:
    if chapter_stats.char_length > max_len:
        max_len = chapter_stats.char_length

# separate for loop, maybe less cache hit but idgad
for chapter_stats in chapters_stats:
    for i in range(len(chapter_stats.occurrence_pos)):
        chapter_stats.occ_pos_norm.append(chapter_stats.occurrence_pos[i] / chapter_stats.char_length)

side_margin = 1
top_margin = 1

vertical_offset = 0

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlim(0,10)
ax.set_ylim(0,10)

count = 1
for chapter_stats in chapters_stats:
    vis_chapter(chapter_stats, top_margin * -count)
    count += 1

plt.axis('off')
plt.show()


