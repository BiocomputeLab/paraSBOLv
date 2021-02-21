#!/usr/bin/env python

import parasbolv as psv
import matplotlib.pyplot as plt
import numpy as np

part_list = []
part_list.append( ['CDS', 
                  {'arrowbody_height':5},
                   None
                  ] )
part_list.append( ['CDS', 
                  {'arrowbody_height':5},
                   None
                  ] )
part_list.append( ['CDS', 
                  {'arrowbody_height':5},
                   None
                  ] )
part_list.append( ['CDS', 
                  {'arrowbody_height':5},
                   None
                  ] )
        
fig, ax, baseline_start, baseline_end, bounds = psv.render_rotated_part_list(part_list, start_position = (-10,7), rotation = 3.142/2, glyph_path='../glyphs/', padding=0.2)
ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)

part_list = []
part_list.append( ['CDS', 
                  {'arrowbody_height':5},
                   None
                  ] )
part_list.append( ['CDS', 
                  {'arrowbody_height':5},
                   None
                  ] )
part_list.append( ['CDS', 
                  {'arrowbody_height':5},
                   None
                  ] )
part_list.append( ['CDS', 
                  {'arrowbody_height':5},
                   None
                  ] )

fig, ax, baseline_start, baseline_end, bounds = psv.render_part_list(part_list, start_position = (0,-4), fig=fig, ax=ax, extra_bounds_list=[bounds], glyph_path='../glyphs/', padding=0.2)
ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)

ax.arrow(90,100,-19,-18, width=2, color=(0,0,0))

part_list = []
part_list.append( ['CDS', 
                  {'arrowbody_height':2, 'arrowbody_width':15},
                  {'cds': {'facecolor': (0,0,1)}}
                  ] )
part_list.append( ['CDS', 
                  {'arrowbody_height':2, 'arrowbody_width':15},
                  {'cds': {'facecolor': (0,0,1)}}
                  ] )
part_list.append( ['CDS', 
                  {'arrowbody_height':2, 'arrowbody_width':15},
                  {'cds': {'facecolor': (0,0,1)}}
                  ] )

fig, ax, baseline_start, baseline_end, bounds = psv.render_part_list(part_list, start_position = (92,100), fig=fig, ax=ax, extra_bounds_list=[bounds], glyph_path='../glyphs/', padding=0.2)
ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)

t = np.arange(0, 136, 0.01)
s = 70 + 50 * (np.sin(0.015 * np.pi * t))
ax.plot(t, s, color=(0,0,1))
ax.plot([0,0], [6.5, 143], color=(0,0,0), linewidth=1.5)
ax.plot([0,136], [6.5, 6.5], color=(0,0,0), linewidth=1.5)

fig.savefig('08_annotate_figures.pdf', transparent=True, dpi=300)

plt.show()