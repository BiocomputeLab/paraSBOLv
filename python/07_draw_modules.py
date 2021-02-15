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
                   None,
                   None
                  ] )
part_list.append( ['CDS', 
                   None,
                   None
                  ] )
part_list.append( ['CDS', 
                   None,
                   None
                  ] )
part_list.append( ['CDS', 
                   None,
                   None
                  ] )

# Create list of modules
module_list = []
module_list.append([1, 2, -1.5, 0])
module_list.append([0, 5, 0, 10])

fig, ax, baseline_start, baseline_end = psv.render_part_list(part_list, glyph_path='../glyphs/', padding=0.3, module_list=module_list)
ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)
fig.savefig('07_draw_modules.pdf', transparent=True, dpi=300)

plt.show()