#!/usr/bin/env python
"""
genbank2sbolv

Generate a simplified SBOLV diagram of the contents of a GenBank file. Only
CDSs are shown with key types coloured.

factor - green
enzyme - blue
regulator - red
structural - orange
membrane - purple
IS - black
none - light grey
"""

import parasbolv as psv
import matplotlib
import matplotlib.pyplot as plt
from Bio import SeqIO
import math

genome_record = SeqIO.read("U00096.2.gbk", "genbank")
cds_list = []
for feature in genome_record.features:
        if feature.type == 'CDS':
            cds_type = 'none'
            if feature.qualifiers.get('function') is not None:
                cds_type = ((feature.qualifiers.get('function')[0]).split(';'))[0]
                if 'factor' in cds_type:
                    cds_type = 'factor'
                elif 'enzyme' in cds_type:
                    cds_type = 'enzyme'
                elif 'regulator' in cds_type:
                    cds_type = 'regulator'
                elif 'structural' in cds_type:
                    cds_type = 'structural'
                elif 'membrane' in cds_type:
                    cds_type = 'membrane'
                elif 'IS' in cds_type:
                    cds_type = 'IS'
                else:
                    cds_type = 'none'
            cds_list.append([int(feature.location.start), int(feature.location.end), feature.location.strand, cds_type])

cmap = {}
cmap['none'] = (230/255.0, 230/255.0, 230/255.0)
cmap['factor'] = (144/255.0, 201/255.0, 135/255.0)
cmap['enzyme'] = (82/255.0, 137/255.0, 199/255.0)
cmap['regulator'] = (220/255.0, 5/255.0, 12/255.0)
cmap['structural'] = (241/255.0, 147/255.0, 45/255.0)
cmap['membrane'] = (177/255.0, 120/255.0, 166/255.0)
cmap['IS'] = (0, 0, 0)

part_lists = []
cur_line = []
cur_len = 0
line_len = 30000
for cds in cds_list:
    orientation = 'forward'
    if cds[2] == -1:
        orientation = 'reverse'
    cds_len = cds[1] - cds[0]
    
    if cur_len + cds_len > line_len:
        part_lists.append(cur_line)
        cur_line = []
        cur_len = 0
    
    arrowhead_width = 7.0
    if (cds_len / 40.0) < 7.0:
        arrowhead_width = cds_len / 40.0
    cur_line.append(['CDS', orientation, {'width': cds_len/40.0, 'arrowhead_width': arrowhead_width}, {'cds': {'facecolor': cmap[cds[3]], 'edgecolor': (0,0,0), 'linewidth': 1.5}}])
    cur_len += cds_len

# Plot Construct
renderer = psv.GlyphRenderer()
fig, ax = plt.subplots()
ax.set_aspect('equal')
ax.set_xticks([])
ax.set_yticks([])
ax.axis('off')
plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
part_position = (0,0)
rotation = 0
line_num = 0
bounds_list = []
for l in part_lists:
    part_position = (0.0, line_num*20.0)
    for part in l:
        bounds, part_position = renderer.draw_glyph(ax, part[0], part_position,
                                    orientation=part[1],
                                    rotation = rotation,
                                    user_parameters = part[2],
                                    user_style = part[3])
        bounds_list.append(bounds)
        part_position = (part_position[0]+6, part_position[1])
    ax.plot([-6, part_position[0]], [line_num*20.0, line_num*20.0], color=(0,0,0), linewidth=1.5, zorder=0)
    line_num += 1

# Automatically find bounds for plot and resize axes
padding = 0.05
final_bounds = psv.find_bound_of_bounds(bounds_list)
width = (final_bounds[1][0] - final_bounds[0][0])/60.0
height = (final_bounds[1][1] - final_bounds[0][1])/60.0
fig_pad = (final_bounds[1][1] - final_bounds[0][1])*padding
pad = height*padding
width = width + (pad*2.0)
height = height + (pad*2.0)
ax.set_xlim([final_bounds[0][0]-fig_pad, final_bounds[1][0]+fig_pad])
ax.set_ylim([final_bounds[0][1]-fig_pad, final_bounds[1][1]+fig_pad])
fig.set_size_inches( (width, height) )

fig.savefig('U00096.2.pdf', transparent=True, dpi=300)
