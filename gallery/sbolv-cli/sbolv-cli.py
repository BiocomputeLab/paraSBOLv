"""
A tool to quickly visualse genetic
constructs using shorthand notation.

Example command:
python sbolv-cli.py --string "p black,r white,c l_blue,t black,s white,p black,p blue,r white,c l_orange,t black,s white,p blue,<x l_orange,<c green,<r white,x l_orange,t black" --interaction "2,6,in,blue//8,12,co,orange//8,15,co,orange" --output sbolv-cli-example.pdf
"""

import parasbolv as psv
import matplotlib.pyplot as plt
import click
import math
from collections import namedtuple


@click.command()
@click.option('--string', prompt='Enter your construct design', help='The shorthand string defining the construct you wish to draw.')
@click.option('-r', '--rotation', default='', help='Rotation of the construct in degrees.')
@click.option('-g', '--gapsize', default=3.0, help='Size of the distance between the parts.')
@click.option('-o', '--output', default=None, help='Filename to save output to')
@click.option('-i', '--interaction', default='', help='interaction defined as starting "starting index,ending index,type,color". \
                                                       Can also receive a list of such interactions seperated by a double forward slash //.')

def render_input(string, rotation, gapsize, interaction, output=None):
    """Renders a construct from an input string.
    
    Parameters
    ----------
    string: str
        Input string containing construct details.
    rotation: str
        String containing expression of rotation
        to be evaluated
    gapsize: float
        Size of the gap between construct parts.
    interaction: str
        String to be processed defining either
        a single or multiple interactions.
    """
    parts = parse_string(string)
    part_list = format_parts(parts, renderer)
    if rotation != '':
        rotation = safe_eval(rotation)
        rotation = math.radians(rotation)
    else:
        rotation = 0.0
    if interaction != '':
        interaction = process_interactions(interaction, part_list)
    else:
        interaction = None
    construct = psv.Construct(part_list, renderer, rotation=rotation, gapsize = gapsize, interaction_list = interaction)
    fig, ax, baseline_start, baseline_end, bounds = construct.draw()
    ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)
    if output is not None:
        fig.savefig(output, dpi=300)
    else:
        plt.show()


def parse_string(string):
    """Parses an input string to details
       of a construct.

    Parameters
    ----------
    string: str
        Input string containing construct details.
    """
    partitions = [p.strip() for p in string.split(',')]
    parts = []
    for partition in partitions:
        values = [v.strip() for v in partition.split(' ') if v.strip()]

        if len(values) == 0:
            continue
        elif len(values) == 1:
            glyph, orientation = find_glyph(values[0], renderer)
            color = find_color('14')
            label = None
        elif len(values) == 2:
            glyph, orientation = find_glyph(values[0], renderer)
            color = find_color(values[1])
            label = None
        elif len(values) == 3:
            glyph, orientation = find_glyph(values[0], renderer)
            color = find_color(values[1])
            label = values[2]

        parts.append([glyph, orientation, color, label])
    return parts


def find_glyph(value, renderer):
    """Finds glyph name from index.

    Parameters
    ----------
    value: int
        Index of the glyph to be drawn in
        renderer.glyphs_library
    renderer: obj
        ParaSBOLv glyph renderer object
        containing glyphs library attribute.
    """
    orientation = 'forward'
    if len(value) != 1:
        if value[0] == '<' and (value[1] == ' ' or value[1] == ',' or value[1].isalpha()):
            orientation = 'reverse'
            value = value.replace('<', '')
    library = renderer.glyphs_library

    abbreviations = {
        'p': 'Promoter',
        'r': 'RibosomeEntrySite',
        'c': 'CDS',
        'g': 'CDS',
        't': 'Terminator',
        's': 'InertDNASpacer',
        'o': 'Operator',
        'x': 'Recombination Site',
    }

    if len(value) == 1 and value == '<':
        orientation = 'reverse'
    elif value[0] == '<' and (value[1] == ' ' or value[1] == ','):
        orientation = 'reverse'

    if value in abbreviations:
        glyph = abbreviations[value]
    else:
        glyphs = list(library.keys())
        index = int(value)
        glyph = glyphs[index]

    return glyph, orientation


def find_color(value):
    """Finds glyph name from index.

    Parameters
    ----------
    value: variable
        Either value specifiying a preset colour
        or tuple defining specific (r,g,b) colour.
    """
    if value is tuple:
        return value
    else:
        colordict = {'blue': ( 25/255.0, 101/255.0, 176/255.0),
                     'l_blue': ( 82/255.0, 137/255.0, 199/255.0),
                     'green': ( 78/255.0, 178/255.0, 101/255.0),
                     'l_green': (144/255.0, 201/255.0, 135/255.0),
                     'red': (220/255.0,   5/255.0,  12/255.0),
                     'orange': (232/255.0,  96/255.0,  28/255.0),
                     'l_orange': (241/255.0, 147/255.0,  45/255.0),
                     'vl_orange': (246/255.0, 193/255.0,  65/255.0),
                     'yellow': (247/255.0, 238/255.0,  85/255.0),
                     'purple': (136/255.0,  46/255.0, 114/255.0),
                     'l_purple': (177/255.0, 120/255.0, 166/255.0),
                     'vl_purple': (214/255.0, 193/255.0, 222/255.0),
                     'grey': (119/255.0, 119/255.0, 119/255.0),
                     'vl_grey': (230/255.0, 230/255.0, 230/255.0),
                     'black': (0, 0, 0),
                     'white': (1, 1, 1)}
        return colordict[value]


def set_style_color(glyph, color, renderer):
    """Sets glyph path styles to specific colour.

    Parameters
    ----------
    glyph: str
        String specifying name of glyph.
    color: tuple
        Tuple specifying colour, format (r,g,b).
    renderer: obj
        ParaSBOLv glyph renderer object
        containing glyphs library attribute.
    """
    library = renderer.glyphs_library
    glyphinfo = library[glyph]
    paths = glyphinfo['paths']
    style_dict = {}
    for path in paths:
        if path['class'] not in ['baseline', 'bounding-box'] and 'background' not in path['id']:
            style = path['style']
            color_style = {}
            for key in style.keys():
                if 'edge' in key:
                    if glyph in ['Promoter', 'Terminator', 'Operator']:
                        color_style[key] = color
                if 'facecolor' in key and 'un' not in path['class']:
                    facecolor = (color[0], color[1], color[2])
                    color_style[key] = facecolor
            style_dict[path['id']] = color_style
    return style_dict


def format_parts(part_list, renderer):
    """Formats parts from parsed input string
       into values usable by paraSBOLv.

    Parameters
    ----------
    part_list: list
        List of parts to be formatted
    renderer: obj
        ParaSBOLv glyph renderer object
        containing glyphs library a attribute.
    """
    formatted_part_list = []
    Part = namedtuple('part', ['glyph_type', 'orientation',  'user_parameters', 'style_parameters'])
    for part in part_list:
        glyph, orientation, color, label = part[0], part[1], part[2], part[3]
        style_dict = set_style_color(glyph, color, renderer)
        if label is None:
            formatted_part = Part(glyph, orientation, None, style_dict)
            formatted_part_list.append(formatted_part)
        else:
            formatted_part = Part(glyph, orientation, {'label_parameters':{'text':label}}, style_dict)
            formatted_part_list.append(formatted_part)
    return formatted_part_list


def safe_eval(expression):
    """Safely evaluates a mathematical expression.
    
       (Exists because I couldn't find a way to allow
       CL parameters to be expressions - ideally needs
       a better solution.)
    
    Parameters
    ----------
    expression: str
        Mathematical expression in string to be evaluated.
    """
    allowed_chars = "0123456789+-*(). /"
    for char in expression:
        if char not in allowed_chars:
            raise Exception(f'Unsafe eval - allowed characters: {allowed_chars}')
    return eval(expression)
    

def process_interactions(interaction, part_list):
    """Processes interaction parameters so that they are
       usable by paraSBOLv.

    Parameters
    ----------
    interaction: str
        Input string to be formatted into
        interaction list.
    part_list: list
        Formatted list of parts between which
        interactions will be drawn.
    """
    Interaction = namedtuple('interaction', ['starting_glyph', 'ending_glyph', 'interaction_type', 'interaction_parameters'])
    if '//' in interaction:
        interaction_list = interaction.split('//')
        formatted_int_list = []
        for interaction in interaction_list:
            interaction_els = interaction.split(',')
            starting_index = int(interaction_els[0])
            ending_index = int(interaction_els[1])
            interaction_type = find_interaction_type(interaction_els[2])
            color = find_color(interaction_els[3])
            formatted_int_list.append(Interaction(part_list[starting_index], part_list[ending_index], interaction_type, {'color':color}))
    else:
        interaction_els = interaction.split(',')
        starting_index = int(interaction_els[0])
        ending_index = int(interaction_els[1])
        interaction_type = find_interaction_type(interaction_els[2])
        color = find_color(interaction_els[3])
        formatted_int_list = [Interaction(part_list[starting_index], part_list[ending_index], interaction_type, {'color':color})]
    return formatted_int_list


def find_interaction_type(value):
    """Finds name of interaction from shorthand
       interaction value.

    Parameters
    ----------
    value: str
        Two character string referring to
        an interaction type.
    """
    if value == 'in':
        value = 'inhibition'
    elif value == 'co':
        value = 'control'
    elif value == 'de':
        value = 'degradation'
    elif value == 'pr':
        value = 'process'
    elif value == 'st':
        value = 'stimulation'
    else:
        raise Exception('Invalid interaction type. Valid values: "in", "co", "de", "pr", "st".')
    return value


if __name__ == '__main__':
    renderer = psv.GlyphRenderer()
    render_input()

