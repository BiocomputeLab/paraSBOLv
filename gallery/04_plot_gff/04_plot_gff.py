#!/usr/bin/env python
"""
Demonstrate how to plot a GFF files
"""

from ast import literal_eval
import csv
from operator import itemgetter
import parasbolv as psv
import matplotlib.pyplot as plt
from collections import namedtuple

# Mapping from GFF annotation type to parasbolv glyph
gffsvgtype_map = {}
gffsvgtype_map['gene'] = 'CDS'
gffsvgtype_map['promoter'] = 'Promoter'
gffsvgtype_map['terminator'] = 'Terminator'
gffsvgtype_map['rbs'] = 'RibosomeEntrySite'

def load_part_list_from_gff (filename, chrom, type_map=gffsvgtype_map, region=None):
    # Load the GFF data
    gff = []
    data_reader = csv.reader(open(filename, 'r'), delimiter='\t')
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
                # Find part attributes
                key_value = attrib.split('=')
                if len(key_value) == 2:
                    if key_value[0] == 'Name':
                        part_name = key_value[1]
                    elif key_value[0] == 'orientation':
                        part_attribs['orientation'] = key_value[1]
                    elif key_value[0] == 'user_parameters':
                        part_attribs['user_parameters'] = literal_eval(key_value[1])
                    elif key_value[0] == 'style_parameters':
                        part_attribs['style_parameters'] = literal_eval(key_value[1])
            if part_name != None and cur_chrom == chrom and part_type in type_map.keys():
                gff.append([part_name, type_map[part_type], part_dir, start_bp, end_bp, part_attribs])
    # Convert to part list for parasbolv
    part_list = []
    Part = namedtuple('part', ['glyph_type', 'orientation',  'user_parameters', 'style_parameters'])
    for gff_el in sorted(gff, key=itemgetter(3)):
        # Check for available elements and append to part list
        if len(gff_el[5]) == 0 or gff_el == None:
            part_list.append(Part(gff_el[1], 'forward', None, None))

        else:
            orientation = 'forward'
            if 'orientation' in gff_el[5]:
                orientation = gff_el[5]['orientation']
            if len(gff_el[5]) == 2:
                part_list.append(Part(gff_el[1], orientation, gff_el[5]['user_parameters'], gff_el[5]['style_parameters']))
            else:
                if 'user_parameters' in gff_el[5]:
                    part_list.append(Part(gff_el[1], orientation, gff_el[5]['user_parameters'], None))
                else:
                    part_list.append(Part(gff_el[1], orientation, None, gff_el[5]['style_parameters']))

    return part_list

part_list = load_part_list_from_gff('./04_plot_gff.gff', 'chrom1', type_map=gffsvgtype_map)

renderer = psv.GlyphRenderer()

construct = psv.Construct(part_list, renderer)
fig, ax, baseline_start, baseline_end, bounds = construct.draw()
ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)

fig.savefig('04_plot_gff.pdf', transparent=True, dpi=300)
fig.savefig('04_plot_gff.jpg', dpi=300)
plt.show()

