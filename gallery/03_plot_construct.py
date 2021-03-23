#!/usr/bin/env python
"""
Demonstrate how to plot lists of parts
"""

import parasbolv as psv
import matplotlib.pyplot as plt

# Basic data type to hold the parts
part_list = []
part_list.append( ['CDS', 
                   {'arrowhead_width': 6}, 
                   {'cds': {'facecolor': (0.5,0.5,0.5), 'edgecolor': (1,0,0), 'linewidth': 2}}
                  ] )
part_list.append( ['CDS', 
                   {'arrowbody_height': 15, 'arrowhead_width': 6}, 
                   {'cds': {'facecolor': (1,1,1), 'edgecolor': (0,0,1), 'linewidth': 2}}
                  ] )
part_list.append( ['Promoter', 
                   None, 
                   None
                  ] )
part_list.append( ['CDS', 
                   None, 
                   None
                  ] )

# Draw part list
fig, ax, baseline_start, baseline_end, bounds = psv.render_part_list(part_list, glyph_path='../glyphs/', padding=0.2)
ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)
fig.savefig('03_plot_construct_1.pdf', transparent=True, dpi=300)

# Draw reversed part list
fig, ax, baseline_start, baseline_end, bounds = psv.render_reverse_part_list(part_list, glyph_path='../glyphs/', padding=0.2)
ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)
fig.savefig('03_plot_construct_2.pdf', transparent=True, dpi=300)

plt.show()
