#!/usr/bin/env python
"""
Demonstrate how to plot a GFF files
"""

import csv
from operator import itemgetter
import parasbolv as psv
import matplotlib.pyplot as plt

__author__  = 'Thomas E. Gorochowski <tom@chofski.co.uk>'
__license__ = 'MIT'
__version__ = '1.0'

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
                key_value = attrib.split('=')
                if len(key_value) == 2:
                    if key_value[0] == 'Name':
                        part_name = key_value[1]
                    # TODO: add else to process attributes
            if part_name != None and cur_chrom == chrom and part_type in type_map.keys():
                gff.append([part_name, type_map[part_type], part_dir, start_bp, end_bp, part_attribs])
    # Convert to part list for parasbolv
    part_list = []
    for gff_el in sorted(gff, key=itemgetter(3)):
        part_list.append([gff_el[1], None, None])
    return part_list

part_list = load_part_list_from_gff('./04_plot_gff.gff', 'chrom1', type_map=gffsvgtype_map)
fig, ax, baseline_start, baseline_end = psv.render_part_list(part_list,glyph_path='../glyphs/', padding=0.3)
ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)
fig.savefig('04_plot_gff.pdf', transparent=True, dpi=300)
plt.close('all')
