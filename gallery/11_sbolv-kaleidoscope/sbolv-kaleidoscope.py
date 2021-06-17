#!/usr/bin/env python
"""
Generative art project using SBOLv glyphs as building blocks.
"""

import parasbolv as psv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import random

# Generate Matplotlib Figure and Axes
fig = plt.figure(figsize=(6,6))
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], frameon=False, aspect=1)

# Generate renderer object
renderer = psv.GlyphRenderer()

def draw_randomised_glyph(ax, renderer, glyph_type, glyph_position, glyph_size, glyph_angle):
    user_parameters = {}
    user_parameters['arrowbody_height'] = 5
    user_parameters['arrowhead_width'] = 5
    cds_style = {}
    cds_style['cds'] = {'facecolor': (0,0,1), 'edgecolor': (1,1,0), 'linewidth': 2}
    bounds, end_point = renderer.draw_glyph(ax, glyph_type, glyph_position, rotation=glyph_angle, user_parameters=user_parameters, user_style=cds_style)




def generate_spiral(part_type, angle_shift=91.0, size_shift=0.2, glyph_angle_shift=1.0):
    part_types = ['CDS', 'Promoter', 'RibosomeEntrySite', 'Terminator']
    cur_position = (0.0, 0.0)
    cur_angle = 0.0
    cur_size = 1.0
    cur_glyph_angle = 0.0
    for idx in range(800):
        # part_types[random.randint(0,3)]
        draw_randomised_glyph(ax, renderer, part_type, cur_position, 20, cur_glyph_angle)
        # update position and heading
        cur_position = (cur_size*math.sin(math.radians(cur_angle)), cur_size*math.cos(math.radians(cur_angle)))
        cur_angle += angle_shift
        cur_size += size_shift
        cur_glyph_angle += math.radians(glyph_angle_shift)

generate_spiral('RibosomeEntrySite', angle_shift=88.0, size_shift=0.3, glyph_angle_shift=0.3)
generate_spiral('Terminator')


# Add black background patch
rect = patches.Rectangle((-1000, -1000), 2000, 2000, facecolor='orange', zorder=-1)
ax.add_patch(rect)

# Set Bounds
ax.set_ylim([-100, 100])
ax.set_xlim([-100, 100])

fig.savefig('sbolv-kaleidoscope.pdf', transparent=True, dpi=300)
fig.savefig('sbolv-kaleidoscope.jpg', dpi=300)
plt.show()
