"""
A tool to quickly visualse genetic
constructs using shorthand notation.

Example strings:

p 1, p 2,c 3, c 5, t 6

p 3,p 10,c 3,p 10,r 3,c 10,c 3,t 10,<t 3,<c 10,<r 3,<p 10

Example interactions:

-i 0,1,in,5

-i 1,3,pr,10//6,7,in,4
"""

import parasbolv as psv
import matplotlib.pyplot as plt
import click


@click.command()
@click.option('--string', prompt='Enter your construct design', help='The shorthand string defining the construct you wish to draw.')
@click.option('-r', '--rotation', default='', help='Rotation of the construct.')
@click.option('-g', '--gapsize', default=3.0, help='Size of the distance between the parts.')
@click.option('-s', '--save', default=0, help='Enable or disable diagram saving.')
@click.option('-st', '--savetype', default='jpg', help='File extension of saved diagram (enable saving with -s 1).')
@click.option('-sp', '--savepath', default='', help='Absolute path to save diagram to (enable saving with -s 1).')
@click.option('-f', '--fill', default=0.8, help='Value from 0-1 that determines the brightness of fills compared to the defined edge colour. \
                                                  A value of 0 results in a white, rather than black, fill.')
@click.option('-i', '--interaction', default='', help='interaction defined as starting "starting index,ending index,type,color". \
                                                        Can also receive a list of such interactions seperated by a double forward slash //.')

def render_input(string, rotation, gapsize, interaction, save, savetype, savepath, fill):
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
    part_list = format_parts(parts, renderer, fill)
    if rotation != '':
        rotation = safe_eval(rotation)
    else:
        rotation = 0.0
    if interaction != '':
        interaction = process_interactions(interaction, part_list)
    else:
        interaction = None
    construct = psv.Construct(part_list, renderer, rotation=rotation, gapsize = gapsize, interaction_list = interaction)
    fig, ax, baseline_start, baseline_end, bounds = construct.draw()
    ax.plot([baseline_start[0], baseline_end[0]], [baseline_start[1], baseline_end[1]], color=(0,0,0), linewidth=1.5, zorder=0)
    if save == 1:
        filename = f'pSBOLv-cli-output.{savetype}'
        if savepath != '':
            filename = f'{savepath}/{filename}'
        fig.savefig(filename, dpi=300)
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
        '?': 'Unspecified',
        """3'""": "3' Overhang Site",
        """5'""": "5' Overhang Site",
        '3′': "3' Overhang Site",
        '5′': "5' Overhang Site",
        'p': 'Promoter',
        'r': 'RibosomeEntrySite',
        'c': 'CDS',
        'g': 'CDS', # TODO: for pigeon compatability, this should be the variant arrow (rather than pentagon) glyph
        # f is recognised by pigeon, but not this tool
        't': 'Terminator',
        's': 'Spacer',
        'o': 'Operator',
        '>': 'Recombination Site',
        '<': 'Recombination Site'

        # I don't know what |/x/x/d are meant to represent in Pigeon
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
        colordict = {'1':(51, 204, 255),
                     '2':(0, 0, 153),
                     '3':(0, 204, 102),
                     '4':(0, 102, 0),
                     '5':(255, 102, 102),
                     '6':(255, 0, 0),
                     '7':(255, 153, 102),
                     '8':(255, 153, 102),
                     '9':(255, 153, 255),
                     '10':(204, 0, 204),
                     '11':(255, 255, 102),
                     '12':(255, 204, 0),
                     '13':(140, 140, 140),
                     '14':(0, 0, 0),
                     'blue1':(51, 204, 255),
                     'blue2':(0, 0, 153),
                     'green1':(0, 204, 102),
                     'green2':(0, 102, 0),
                     'red1':(255, 102, 102),
                     'red2':(255, 0, 0),
                     'orange1':(255, 153, 102),
                     'orange2':(255, 153, 102),
                     'pink1':(255, 153, 255),
                     'pink2':(204, 0, 204),
                     'yellow1':(255, 255, 102),
                     'yellow2':(255, 204, 0),
                     'grey':(140, 140, 140),
                     'gray':(140, 140, 140),
                     'black':(0, 0, 0)}
        value = colordict[value]
        value = (value[0]/255, value[1]/255, value[2]/255)
        return value


def set_style_color(glyph, color, renderer, fill):
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
                    color_style[key] = color
                if 'facecolor' in key and 'un' not in path['class']:
                    facecolor = (color[0]*fill, color[1]*fill, color[2]*fill)
                    if fill == 0:
                        facecolor = (1,1,1)
                    color_style[key] = facecolor
            style_dict[path['id']] = color_style
    return style_dict


def format_parts(part_list, renderer, fill):
    """Formats parts from parsed input string
       into values usable by paraSBOLv.

    Parameters
    ----------
    part_list: list
        List of parts to be formatted
    renderer: obj
        ParaSBOLv glyph renderer object
        containing glyphs librarya attribute.
    """
    formatted_part_list = []
    for part in part_list:
        glyph, orientation, color, label = part[0], part[1], part[2], part[3]
        style_dict = set_style_color(glyph, color, renderer, fill)
        if label is None:
            formatted_part = [glyph, {'orientation':orientation}, style_dict]
            formatted_part_list.append(formatted_part)
        else:
            formatted_part = [glyph, {'orientation':orientation, 'label_parameters':{'text':label}}, style_dict]
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
    if '//' in interaction:
        interaction_list = interaction.split('//')
        formatted_int_list = []
        for interaction in interaction_list:
            interaction_els = interaction.split(',')
            starting_index = int(interaction_els[0])
            ending_index = int(interaction_els[1])
            interaction_type = find_interaction_type(interaction_els[2])
            color = find_color(interaction_els[3])
            formatted_int_list.append([part_list[starting_index], part_list[ending_index], interaction_type, {'color':color}])
    else:
        interaction_els = interaction.split(',')
        starting_index = int(interaction_els[0])
        ending_index = int(interaction_els[1])
        interaction_type = find_interaction_type(interaction_els[2])
        color = find_color(interaction_els[3])
        formatted_int_list = [[part_list[starting_index], part_list[ending_index], interaction_type, {'color':color}]]
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
