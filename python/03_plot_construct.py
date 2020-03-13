#!/usr/bin/env python
"""
Demonstrate how to plot lists of parts
"""

import parasbolv as psv
import matplotlib.pyplot as plt

__author__  = 'Thomas E. Gorochowski <tom@chofski.co.uk>'
__license__ = 'MIT'
__version__ = '1.0'

# Basic data type to hold the parts
part_list = []
part_list.append( ['CDS', 
                   {'arrowbody_width': 20, 'arrowbody_height': 5, 'arrowhead_height': 0, 'arrowhead_width': 5}, 
                   {'cds': {'facecolor': (0.5,0.5,0.5), 'edgecolor': (1,0,0), 'linewidth': 2}}
                  ] )
part_list.append( ['CDS', 
                   {'arrowbody_width': 40, 'arrowbody_height': 5, 'arrowhead_height': 2, 'arrowhead_width': 10}, 
                   {'cds': {'facecolor': (1,1,1), 'edgecolor': (0,0,1), 'linewidth': 2}}
                  ] )
part_list.append( ['CDS', 
                   None, 
                   None
                  ] )
fig, ax, baseline_start, baseline_end = psv.render_part_list(part_list,glyph_path='../glyphs/', padding=0.2)
ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)
fig.savefig('03_plot_construct.pdf', transparent=True, dpi=300)
plt.close('all')
