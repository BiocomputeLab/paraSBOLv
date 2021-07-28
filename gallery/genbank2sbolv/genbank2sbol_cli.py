#!/usr/bin/env python
"""
CLI for the .gbk plotting tool that supports specification of which colours to assign to features, how
long the lines of features should be, and the spacings between features and lines.

Specify feature:colour pairs with comma-seperated values. For example:

-c 'membrane:(1.0,1.0,1.0),terminator:(0.5,0.5,0.0)'

where feature:colour pairs are seperated by a colon.
"""

import click
import parasbolv as psv
import matplotlib.pyplot as plt
from Bio import SeqIO
import math
from ast import literal_eval as make_tuple

cmap = {}
cmap['none'] = (230/255.0, 230/255.0, 230/255.0)
cmap['factor'] = (144/255.0, 201/255.0, 135/255.0)
cmap['enzyme'] = (82/255.0, 137/255.0, 199/255.0)
cmap['regulator'] = (220/255.0, 5/255.0, 12/255.0)
cmap['structural'] = (241/255.0, 147/255.0, 45/255.0)
cmap['membrane'] = (177/255.0, 120/255.0, 166/255.0)
cmap['IS'] = (0, 0, 0)

@click.command()
@click.option('--path', prompt='Please enter your .gbk path', help='The path of the .gbk file to be rendered.')
@click.option('-c', '--colours', default='', help='Assigns features (keys) to colours (values) in the cmap dictionary.')
@click.option('-v', '--vgap', default=20, help='Vertical gap size between baselines')
@click.option('-h', '--hgap', default=8, help='Horizontal gap size between parts')
@click.option('-t', '--thickness', default=10, help='Specify CDS thickness')
@click.option('-l', '--linelength', default=30000, help='Specify line length')


def recieve_input(path, colours, vgap, hgap, thickness, linelength):
    if colours:
        map_options = parse_map(colours)
        for option in map_options:
            keyvalue = option.split(':')
            cmap[keyvalue[0]] = make_tuple(keyvalue[1])
    genome_record = SeqIO.read(path, "genbank")
    cds_list = get_features(genome_record)
    part_lists = create_lines(cds_list, thickness, linelength)
    bounds_list, fig, ax = plot_construct(part_lists, vgap, hgap)
    prepare_diagram(bounds_list, fig, ax)
    plt.show()
    
def parse_map(options):
    options_list = options.split(' ')
    return(options_list)

def get_features(genome_record):
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
    return cds_list

def create_lines(cds_list, thickness, linelength):
    part_lists = []
    cur_line = []
    cur_len = 0
    line_len = linelength
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
        cur_line.append(['CDS', orientation, {'width': cds_len/40.0, 'arrowhead_width': arrowhead_width, 'arrowbody_height': thickness, 'height': thickness}, {'cds': {'facecolor': cmap[cds[3]], 'edgecolor': (0,0,0), 'linewidth': 1.5}}])
        cur_len += cds_len
    return part_lists

def plot_construct(part_lists, vgap, hgap):
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
        part_position = (0.0, line_num*vgap)
        for part in l:
            bounds, part_position = renderer.draw_glyph(ax, part[0], part_position,
                                                        orientation = part[1],
                                                        rotation = rotation,
                                                        user_parameters = part[2],
                                                        user_style = part[3])
            bounds_list.append(bounds)
            part_position = (part_position[0]+hgap, part_position[1])
        ax.plot([-1*hgap, part_position[0]], [line_num*vgap, line_num*vgap], color=(0,0,0), linewidth=1.5, zorder=0)
        line_num += 1
    return bounds_list, fig, ax

def prepare_diagram(bounds_list, fig, ax):
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


if __name__ == '__main__':
    renderer = psv.GlyphRenderer()
    recieve_input()
