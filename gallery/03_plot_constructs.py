#!/usr/bin/env python
"""
Demonstrate how to plot lists of parts
"""

import parasbolv as psv
import matplotlib.pyplot as plt

# Basic data type to hold the parts
part_list = []
part_list.append( ['CDS', 
                   None, 
                   {'cds': {'facecolor': (0.5,0.5,0.5), 'edgecolor': (1,0,0), 'linewidth': 2}}
                  ] )
part_list.append( ['CDS', 
                   {'height':25, 'arrowbody_height':25, 'width':40}, 
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
part_list.append( ['CDS', 
                   {'orientation':'reverse'}, 
                   None
                  ] )
part_list.append( ['CDS', 
                   {'orientation':'reverse'},
                   None
                  ] )

# Create renderer
renderer = psv.GlyphRenderer()

# Draw construct
construct = psv.Construct(part_list, renderer)
fig, ax, baseline_start, baseline_end, bounds = construct.draw()
ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)

# Draw rotated construct
construct_2 = psv.Construct(part_list, renderer, fig=fig, ax=ax, start_position=(0,-30), additional_bounds_list=[bounds])
construct_2.rotation = 3.142 / -8
construct_2.update_bounds() # Update bounds to new orientation of construct
fig, ax, baseline_start, baseline_end, bounds = construct_2.draw()
ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)

fig.savefig('03_plot_constructs.pdf', transparent=True, dpi=300)

plt.show()
