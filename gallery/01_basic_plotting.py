#!/usr/bin/env python
"""
Basic example of plotting parametric SBOL Visual glyphs using the parasbolv library.
"""

import parasbolv as psv
import matplotlib.pyplot as plt

renderer = psv.GlyphRenderer()

p = renderer.get_baseline_end('RibosomeEntrySite', (0.5, 40), rotation=1.0)
print(renderer.get_glyph_bounds('RibosomeEntrySite', (0.5, 40), rotation=1.0))

fig = plt.figure(figsize=(6,6))
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], frameon=False, aspect=1)

# Draw Insulator
insulator_style = {}
insulator_style['insulator-inner-path'] = {'facecolor': (1,0,0)}
insulator_style['insulator-outer-path'] = {'edgecolor': (0,1,0), 'linewidth': 5}

renderer.draw_glyph(ax, 'Insulator', (10, 20), user_style=insulator_style)

# Draw Ribosome Entry Site
renderer.draw_glyph(ax, 'RibosomeEntrySite', (20, 50))

# Draw CDS 1
user_parameters = {}
user_parameters['arrowbody_height'] = 15

renderer.draw_glyph(ax, 'CDS', (60, 40), user_parameters=user_parameters)

# Draw CDS 2
user_parameters['arrowbody_height'] = 5
user_parameters['arrowhead_width'] = 15

cds_style = {}
cds_style['cds'] = {'facecolor': (0,0,1), 'edgecolor': (1,1,0), 'linewidth': 10}

bounds, end_point = renderer.draw_glyph(ax, 'CDS', (35, 80), rotation=(2*3.14)-(3.14/4), user_parameters=user_parameters, user_style=cds_style)

ax.set_ylim([0,100])
ax.set_xlim([0,100])

plt.show()
