#!/usr/bin/env python
"""
Plot interactions to and from glyphs.
"""

import parasbolv as psv
import matplotlib.pyplot as plt

part_list = []
part_list.append( ['CDS', 
                   None,
                   {'cds': {'facecolor': (1,1,1), 'edgecolor': (0.75,0,0), 'linewidth': 2}}
                  ] )
part_list.append( ['Promoter',
                   None,
                   None
                  ] )
part_list.append( ['CDS', 
                   None,
                   {'cds': {'facecolor': (1,1,1), 'edgecolor': (0,0.75,0), 'linewidth': 2}}
                  ] )
part_list.append( ['Promoter', 
                   None,
                   None
                  ] )
part_list.append( ['CDS', 
                   None,
                   {'cds': {'facecolor': (1,1,1), 'edgecolor': (0,0,0.75), 'linewidth': 2}}
                  ] )

# Create list of interactions to pass to render_part_list
interaction_list = []
interaction_list.append([part_list[0], part_list[1], 'inhibition', {'color': (0.75,0,0)}])
interaction_list.append([part_list[2], part_list[3], 'control', {'color': (0, 0.75, 0),
                                                                 'direction':'reverse'}])

# Create renderer
renderer = psv.GlyphRenderer()

# Plot Construct
construct = psv.Construct(part_list, renderer, interaction_list=interaction_list)
fig, ax, baseline_start, baseline_end, bounds = construct.draw()
ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)

fig.savefig('06_draw_interactions.pdf', transparent=True, dpi=300)

# You can also manually plot interactions:
# interaction_bounds = psv.draw_interaction(ax, ((50, 15), (50, 15)), ((60, 15), (60, 15)), 'process', None)

plt.show()
