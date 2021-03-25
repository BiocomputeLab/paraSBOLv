#!/usr/bin/env python
"""
Basic example of plotting parametric SBOL Visual glyphs using the parasbolv library.
"""

import parasbolv as psv
import matplotlib.pyplot as plt

__author__  = 'Thomas E. Gorochowski <tom@chofski.co.uk>'
__license__ = 'MIT'
__version__ = '1.0'

renderer = psv.GlyphRenderer(glyph_path='../glyphs/')

p = renderer.get_baseline_end('RibosomeEntrySite', (0.5, 40), rotation=1.0)
print(renderer.get_glyph_bounds('RibosomeEntrySite', (0.5, 40), rotation=1.0))

fig = plt.figure(figsize=(6,6))
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], frameon=False, aspect=1)

user_parameters = {}
user_parameters['arrowbody_width'] = 50
insulator_style = {}
insulator_style['insulator-inner-path'] = {'facecolor': (1,0,0)}
insulator_style['insulator-outer-path'] = {'edgecolor': (0,1,0), 'linewidth': 5}
renderer.draw_glyph(ax, 'Insulator', (10, 20), user_parameters=user_parameters, user_style=insulator_style)

user_parameters['arrowbody_width'] = 50
renderer.draw_glyph(ax, 'CDS', (0.5, 40), user_parameters=user_parameters)

user_parameters['arrowbody_width'] = 50
renderer.draw_glyph(ax, 'RibosomeEntrySite', (10, 60), user_parameters=user_parameters)

user_parameters['arrowbody_width'] = 70
user_parameters['arrowhead_height'] = 5
user_parameters['arrowhead_width'] = 20
cds_style = {}
cds_style['cds'] = {'facecolor': (0,0,1), 'edgecolor': (1,1,0), 'linewidth': 10}
bounds, end_point = renderer.draw_glyph(ax, 'CDS', (35, 80), rotation=(2*3.14)-(3.14/4), user_parameters=user_parameters, user_style=cds_style)

ax.set_ylim([0,100])
ax.set_xlim([0,100])
plt.show()
