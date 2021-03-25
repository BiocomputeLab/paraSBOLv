#!/usr/bin/env python

import parasbolv as psv
import matplotlib.pyplot as plt

part_list = []
part_list.append( ['CDS', 
                   None,
                   None
                  ] )
part_list.append( ['CDS', 
                   None,
                   None
                  ] )
part_list.append( ['CDS', 
                   {'y_offset': -25},
                   None
                  ] )
part_list.append( ['CDS', 
                   {'y_offset': -25},
                   None
                  ] )
part_list.append( ['CDS', 
                   {'y_offset': -25},
                   None
                  ] )
part_list.append( ['CDS', 
                   {'y_offset': -50},
                   None
                  ] )
part_list.append( ['CDS', 
                   {'y_offset': -50},
                   None
                  ] )
part_list.append( ['CDS', 
                   None,
                   None
                  ] )
 

# Create list of modules
module_list = []
module_list.append([0, 1, 0, -10])
module_list.append([6, 7, 0, -60])

# Create renderer
renderer = psv.GlyphRenderer(glyph_path='../glyphs/')

# Draw construct
construct = psv.construct(part_list, renderer, module_list = module_list)
fig, ax, baseline_start, baseline_end, bounds = construct.draw()

ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)
ax.plot([baseline_start[0], baseline_end[0]], [-25, -25], color=(0,0,0), linewidth=1.5, zorder=0)
ax.plot([baseline_start[0], baseline_end[0]], [-50, -50], color=(0,0,0), linewidth=1.5, zorder=0)

fig.savefig('07_split_plots_and_modules.pdf', transparent=True, dpi=300)

plt.show()
