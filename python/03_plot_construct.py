#!/usr/bin/env python
"""
Demonstrate how to plot lists of parts
"""

import numpy as np
import parasbolv as psv
import matplotlib.pyplot as plt
import csv

__author__  = 'Thomas E. Gorochowski <tom@chofski.co.uk>'
__license__ = 'MIT'
__version__ = '1.0'

def find_bound_of_bounds (bounds_list):
    # Set initial guess
    x_min = bounds_list[0][0][0]
    y_min = bounds_list[0][0][1]
    x_max = bounds_list[0][1][0]
    y_max = bounds_list[0][1][1]
    for b in bounds_list:
        if b[0][0] < x_min:
            x_min = b[0][0]
        if b[0][1] < y_min:
            y_min = b[0][1]
        if b[1][0] > x_max:
            x_max = b[1][0]
        if b[1][1] > y_max:
            y_max = b[1][1]
    return [(x_min, y_min), (x_max, y_max)]

def render_part_list (part_list, padding=0.2):
    renderer = psv.GlyphRenderer(glyph_path='../glyphs/')
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    part_position = (0, 0)
    start_position = part_position
    bounds_list = []
    for part in part_list:
        bounds, part_position = renderer.draw_glyph(ax, part[0], part_position, user_parameters=part[1], user_style=part[2])
        bounds_list.append(bounds)
    # Automatically find bounds for plot and resize axes
    final_bounds = find_bound_of_bounds(bounds_list)
    width = (final_bounds[1][0] - final_bounds[0][0])/30.0
    height = (final_bounds[1][1] - final_bounds[0][1])/30.0
    fig_pad = (final_bounds[1][1] - final_bounds[0][1])*padding
    pad = height*padding
    width = width + (pad*2.0)
    height = height + (pad*2.0)
    ax.set_xlim([final_bounds[0][0]-fig_pad, final_bounds[1][0]+fig_pad])
    ax.set_ylim([final_bounds[0][1]-fig_pad, final_bounds[1][1]+fig_pad])
    fig.set_size_inches( (width, height) )
    return fig, ax, start_position, part_position

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
fig, ax, baseline_start, baseline_end = render_part_list(part_list)
fig.savefig('03_plot_construct.pdf', transparent=True, dpi=300)
plt.close('all')
