#!/usr/bin/env python
"""
Description
"""

import parasbolv as psv
import matplotlib.pyplot as plt
import numpy as np
import random

fig, ax = plt.subplots()

### Scatter plot
np.random.seed(18012001)
rng = np.random.default_rng(12345)
x = rng.integers(low=0, high=600, size=30)
y = rng.integers(low=0, high=600, size=30)
plt.scatter(x, y, s=15, color = (0,0,0))

### Constructs
renderer = psv.GlyphRenderer()
start_positions_colors = [
                          [(430,470), (0.7,0.7,0)],
                          [(500,220), (0,0.7,0.7)],
                          [(152,300), (0.7,0,0.7)],
                          [(440,350), (0.7,0.7,0.7)]
                        ]
for start_position_color in start_positions_colors:
    part_list = []
    start_position = start_position_color[0]
    color = start_position_color[1]
    part_list.append(['CDS', 'forward', None, {'cds': {'facecolor':color}}])
    part_list.append(['CDS', 'forward', None, {'cds': {'facecolor':color}}])
    part_list.append(['Promoter', 'forward', None, None])
    part_list.append(['Promoter', 'forward', None, None])
    part_list.append(['RibosomeEntrySite', 'forward', None, {'rbs': {'facecolor':color}}])
    part_list.append(['RibosomeEntrySite', 'forward', None, {'rbs': {'facecolor':color}}])
    random.shuffle(part_list)
    construct = psv.Construct(part_list, renderer, fig=fig, ax=ax, start_position = start_position, modify_axis=0)
    fig, ax, baseline_start, baseline_end, bounds = construct.draw()
    ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)
    # Find nearest scatter point and draw a line to it
    xdiffs = abs(x - start_position[0])
    ydiffs = abs(y - start_position[1])
    hyps = np.sqrt(xdiffs**2 + ydiffs**2)
    smallest = min(hyps)
    index = np.where(hyps == smallest)
    nearestpoint = (x[index], y[index])
    ax.plot([baseline_start[0]-5, nearestpoint[0]+5], [baseline_start[1]-5, nearestpoint[1]+5], color=color, linewidth=1.5, zorder=0)
        

ax.set_aspect('equal')
ax.set_xlabel('x parameter', fontsize = 13)
ax.set_ylabel('y parameter', fontsize = 13)

plt.xticks([])
plt.yticks([])
plt.tight_layout()
plt.show()

fig.savefig('10_integrated-plotting.pdf', transparent=True, dpi=300)
fig.savefig('10_integrated-plotting.jpg', dpi=300)