#!/usr/bin/env python
"""
CLI for the gff plotting tool that supports specification of which chromosomes and features to draw.

Specify chromosomes and feature:SBOLv pairs with comma-seperated values. For example:

-c 'chrom1,chrom2,chrom6,chromX'

and

-m 'promoter:Promoter,terminator:Terminator'

where feature:SBOLv pairs are seperated by a colon.
"""

from operator import add
import parasbolv as psv
import matplotlib.pyplot as plt
import click
from ast import literal_eval
import csv
from operator import itemgetter
from collections import namedtuple

gffsvgtype_map = {}
gffsvgtype_map['gene'] = 'CDS'
gffsvgtype_map['promoter'] = 'Promoter'
gffsvgtype_map['terminator'] = 'Terminator'
gffsvgtype_map['rbs'] = 'RibosomeEntrySite'

@click.command()
@click.option('--path', prompt='Please enter your .gff path', help='The path of the .gff file to be rendered.')
@click.option('-c', '--chromosomes', default='chrom1', help='Chromosomes to draw.')
@click.option('-m', '--map', default='', help='.gff features to be mapped to SBOLv parts.')
@click.option('-v', '--vgap', default=50, help='Vertical gap size between chromosomes')
@click.option('-h', '--hgap', default=10, help='Horizontal gap size between parts')


def recieve_input(path, chromosomes, map, vgap, hgap):
    if map is True:
        map_options = parse_map(map)
        for option in map_options:
            keyvalue = option.split(':')
            gffsvgtype_map[keyvalue[0]] = keyvalue[1]
    chroms_list = parse_chromosomes(chromosomes)
    fig, ax = plt.subplots()
    y = 0
    additional_bounds_list = []
    for chrom in chroms_list:
        bounds = draw_chrom(fig, ax, chrom, path, y, additional_bounds_list, hgap)
        additional_bounds_list.append(bounds)
        y =- vgap
    plt.show()


def draw_chrom(fig, ax, chrom, path, y, additional_bounds_list, hgap):
    part_list = load_part_list_from_gff(path, chrom, type_map = gffsvgtype_map)
    construct = psv.Construct(part_list, renderer, fig=fig, ax=ax, start_position=(0,y), additional_bounds_list=additional_bounds_list, gapsize=hgap)
    fig, ax, baseline_start, baseline_end, bounds = construct.draw()
    ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)
    return bounds


def parse_map(options):
    chars_to_split = ''
    if ' ' in options:
        chars_to_split += ' '
    if ',' in options:
        chars_to_split += ','
    if len(chars_to_split) == 2:
        options = options.replace(' ', '')
        options_list = options.split(',')
        return(options_list)
    if chars_to_split == ',':
        options_list = options.split(',')
    else:
        options_list = options.split(' ')
    return(options_list)


def parse_chromosomes(string):
    # Split by spaces and commas
    chars_to_split = ''
    if ' ' in string:
        chars_to_split += ' '
    if ',' in string:
        chars_to_split += ','
    if len(chars_to_split) == 2:
        string = string.replace(' ', '')
        chrom_list = string.split(',')
        return(chrom_list)
    if chars_to_split == ',':
        chrom_list = string.split(',')
    else:
        chrom_list = string.split(' ')
    return(chrom_list)



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


if __name__ == '__main__':
    renderer = psv.GlyphRenderer()
    recieve_input()
