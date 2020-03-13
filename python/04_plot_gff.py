#!/usr/bin/env python
"""
Demonstrate how to plot lists of parts (even from GFF files)
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
fig.savefig('test.pdf', transparent=True, dpi=300)
plt.close('all')


"""
gffsvgtype_map = {}

def load_design_from_gff (filename, chrom, type_map=dpl_default_type_map, region=None):
    # Load the GFF data
    gff = []
    data_reader = csv.reader(open(filename, 'rU'), delimiter='\t')
    for row in data_reader:
        if len(row) == 9:
            cur_chrom = row[0]
            part_type = row[2]
            start_bp = int(row[3])
            end_bp = int(row[4])
            part_dir = row[6]
            part_attribs = {}
            split_attribs = row[8].split(';')
            part_name = None
            for attrib in split_attribs:
                key_value = attrib.split('=')
                if len(key_value) == 2:
                    if key_value[0] == 'Name':
                        part_name = key_value[1]
                    else:
                        part_attribs[key_value[0]] = convert_attrib(key_value[1])
            if part_name != None and cur_chrom == chrom and part_type in list(type_map.keys()):
                # Check feature start falls in region
                if region != None and (start_bp > region[0] and start_bp < region[1]):
                    gff.append([part_name, type_map[part_type], part_dir, start_bp, end_bp, part_attribs])
    # Convert to DNAplotlib design (sort on start position first)
    design = []
    for gff_el in sorted(gff, key=itemgetter(3)):
        new_part = {}
        new_part['name'] = gff_el[0]
        new_part['type'] = gff_el[1]
        if gff_el[2] == '+':
            new_part['fwd'] = True
        else:
            new_part['fwd'] = False
        new_part['start'] = gff_el[3]
        new_part['end'] = gff_el[4]
        new_part['opts'] = gff_el[5]
        design.append(new_part)
    # Return the sorted design
    return design
"""