#!/usr/bin/env python
"""
Parametric SBOL Visual (parasbolv)

A simple and lightweight library for rendering parametric SVG versions
of the SBOL Visual glyphs using matplotlib. Is able to load a directory 
of glyphs and provides access to all style and geometry customisations.
"""
import warnings
import svgpath2mpl
import os
import glob
import xml.etree.ElementTree as ET
import re
from math import cos, sin, pi
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.font_manager as font_manager

__author__  = 'Thomas E. Gorochowski <tom@chofski.co.uk>'
__license__ = 'MIT'
__version__ = '1.0'

class GlyphRenderer:
    """ Class to load and render using matplotlib parametric SVG glyphs.
    """

    def __init__(self, glyph_path='glyphs/', global_defaults=None):
        self.svg2mpl_style_map = {}
        self.svg2mpl_style_map['fill'] = 'facecolor'
        self.svg2mpl_style_map['stroke'] = 'edgecolor'
        self.svg2mpl_style_map['stroke-width'] = 'linewidth'
        self.glyphs_library, self.glyph_soterm_map = self.load_glyphs_from_path(glyph_path)

    def __process_unknown_val (self, val):
        # Convert an unknown value into the correct type
        converted_val = None
        if val.startswith('rgba'):
            # Convert RGBA value from 8-bit to arithmetic
            c_els = val[5:-1].split(',')
            r_val = float(c_els[0])/255.0
            g_val = float(c_els[1])/255.0
            b_val = float(c_els[2])/255.0
            a_val = float(c_els[3])
            converted_val = (r_val, g_val, b_val)
        elif val.startswith('rgb'):
            # Convert RGB value from 8-bit to arithmetic
            c_els = val[4:-1].split(',')
            r_val = float(c_els[0])/255.0
            g_val = float(c_els[1])/255.0
            b_val = float(c_els[2])/255.0
            converted_val = (r_val, g_val, b_val)
        elif val.endswith('pt'):
            # Convert to float, omitting 'pt' unit
            try:
                converted_val = float(val[:-2])
            except ValueError:
                converted_val = val
        else:
            try:
                converted_val = float(val)
            except ValueError:
                converted_val = val
        return converted_val

    def __process_style (self, style_text):
        # Convert the style text into a dictionary
        style_data = {}
        style_els = style_text.split(';')
        for el in style_els:
            key_val = [x.strip() for x in el.split(':')] # Convert style element into list
            if key_val[0] in self.svg2mpl_style_map.keys():
                # Create new key-value pair with processed value
                style_data[self.svg2mpl_style_map[key_val[0]]] = self.__process_unknown_val(key_val[1])
        return style_data

    def __extract_tag_details(self, tag_attributes):
        # Extract all the relevant details from an XML tag in the SVG
        tag_details = {}
        tag_details['glyphtype'] = None
        tag_details['soterms'] = []
        tag_details['class'] = None
        tag_details['id'] = None
        tag_details['defaults'] = None
        tag_details['style'] = {}
        tag_details['d'] = None
        # Pull out the relevant details
        for key in tag_attributes.keys():
            if key == 'glyphtype':
                tag_details['glyphtype'] = tag_attributes[key]
            if key == 'soterms':
                tag_details['soterms'] = tag_attributes[key].split(';')
            if key == 'class':
                tag_details['class'] = tag_attributes[key]
            if key == 'id':
                tag_details['id'] = tag_attributes[key]
            if key == 'style':
                tag_details['style'] = self.__process_style(tag_attributes[key])
            if 'parametric' in key and key.endswith('}d'):
                tag_details['d'] = tag_attributes[key]
            if 'parametric' in key and key.endswith('}defaults'):
                split_defaults_text = tag_attributes[key].split(';')
                defaults = {}
                for element in split_defaults_text:
                    key_value = element.split('=')
                    defaults[key_value[0].strip()] = float(key_value[1].strip())
                defaults['baseline_y'] = 0.0
                defaults['baseline_x'] = 0.0
                tag_details['defaults'] = defaults
        return tag_details

    def __eval_svg_data(self, svg_text, parameters):
        # Use regular expression to extract and then replace with evaluated version
        # https://stackoverflow.com/questions/38734335/python-regex-replace-bracketed-text-with-contents-of-brackets
        return re.sub(r"{([^{}]+)}", lambda m: str(eval(m.group()[1:-1], parameters)), svg_text)

    def __flip_position_rotate_glyph(self, path, baseline_y, position, rotation):
        # Flip paths into matplotlib default orientation and position and rotate paths 
        new_verts = []
        new_codes = []
        for v_idx in range(np.size(path.vertices, 0)):
            cur_vert = path.vertices[v_idx]
            new_codes.append(path.codes[v_idx])
            # Assign x and flipped y of origin in accordance with matplotlib default orientation
            org_x = cur_vert[0]
            org_flipped_y = baseline_y-(cur_vert[1]-baseline_y)
            # Rotate using trig functions
            rot_x = org_x * np.cos(rotation) - org_flipped_y * np.sin(rotation)
            rot_y = org_x * np.sin(rotation) + org_flipped_y * np.cos(rotation)
            final_x = rot_x+position[0]
            final_y = rot_y+position[1]
            new_verts.append([final_x, final_y])
        return Path(new_verts, new_codes)

    def __bounds_from_paths_to_draw(self, paths):
        # Calculate the bounding box from a set of paths
        x_min = None
        x_max = None
        y_min = None
        y_max = None
        for p in paths:
            # Find min and max x/y values of all vertices
            xs = p[0].vertices[:, 0]
            ys = p[0].vertices[:, 1]
            cur_x_min = np.min(xs)
            cur_x_max = np.max(xs)
            cur_y_min = np.min(ys)
            cur_y_max = np.max(ys)
            if x_min is None:
                x_min = cur_x_min
                x_max = cur_x_max
                y_min = cur_y_min
                y_max = cur_y_max
            else:
                if cur_x_min < x_min:
                     x_min = cur_x_min
                if cur_x_max < x_max:
                     x_max = cur_x_max
                if cur_y_min < y_min:
                     y_min = cur_y_min
                if cur_y_max < y_max:
                     y_max = cur_y_max
        return (x_min, y_min), (x_max, y_max)

    def load_glyph(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        root_attributes = self.__extract_tag_details(root.attrib)
        glyph_type = root_attributes['glyphtype']
        glyph_soterms = root_attributes['soterms']
        glyph_data = {}
        glyph_data['paths'] = []
        glyph_data['defaults'] = root_attributes['defaults']
        for child in root:
            # Cycle through and find all paths
            if child.tag.endswith('path'):
                glyph_data['paths'].append(self.__extract_tag_details(child.attrib))
        return glyph_type, glyph_soterms, glyph_data

    def load_glyphs_from_path(self, path):
        glyphs_library = {}
        glyph_soterm_map = {}
        for infile in glob.glob( os.path.join(path, '*.svg') ):
            glyph_type, glyph_soterms, glyph_data = self.load_glyph(infile)
            glyphs_library[glyph_type] = glyph_data
            for soterm in glyph_soterms:
                glyph_soterm_map[soterm] = glyph_type
        return glyphs_library, glyph_soterm_map

    def draw_glyph(self, ax, glyph_type, position, rotation=0.0, user_parameters=None, user_style=None):
	    # Check glyph type exists	
        try:	
            glyph = self.glyphs_library[glyph_type]	
        except:	
            class Invalid_glyph_type(Exception):	
                pass	
            raise Invalid_glyph_type(f"""'{glyph_type}' is not a valid glyph.""")
        merged_parameters = glyph['defaults'].copy()
        if user_parameters is not None:
            # Find label
            label = None
            if 'label' in user_parameters:
                label = user_parameters['label']
            # Find rotation in user_parameters (keyword arg takes priority)
            if rotation == 0.0 and 'rotation' in user_parameters:
                rotation = user_parameters['rotation']
            # Collate parameters (user parameters take priority)
            for key in user_parameters.keys():
                if key not in glyph['defaults'] and key != 'label' and key != 'rotation':
                    warnings.warn(f"""Parameter '{key}' is not valid for '{glyph_type}'.""")
                merged_parameters[key] = user_parameters[key]
	    # Find invalid path ids	
        if user_style is not None:	
            path_ids = []	
            for path in glyph['paths']:	
                path_ids.append(path['id'])	
            for key in user_style.keys():	
                if key not in path_ids:	
                    warnings.warn(f"""'{key}' is not a valid path ID for the '{glyph_type}' glyph.""")
        paths_to_draw = []
        for path in glyph['paths']:
            if path['class'] not in ['baseline', 'bounding-box']:
                merged_style = path['style']
                if path['id'] is not None and user_style is not None and path['id'] in user_style.keys():
                    # Merge the styling dictionaries (user takes preference)
                    merged_style = user_style[path['id']].copy()
                    for style_el in path['style'].keys():
                        if style_el not in merged_style.keys():
                            merged_style[style_el] =  path['style'][style_el]
                    for style_el in merged_style.copy():
                        # Find and remove invalid style elements
                        if style_el not in path['style'].keys():
                            merged_style.pop(style_el)
                            warnings.warn(f"""Style parameter '{style_el}' is not valid for '{path["id"]}'.""")
                svg_text = self.__eval_svg_data(path['d'], merged_parameters)
                paths_to_draw.append([svgpath2mpl.parse_path(svg_text), merged_style])
        # Draw glyph to the axis with correct styling parameters
        baseline_y = glyph['defaults']['baseline_y']
        all_y_flipped_paths = []
        for path in paths_to_draw:
            y_flipped_path = self.__flip_position_rotate_glyph(path[0], baseline_y, position, rotation)
            all_y_flipped_paths.append([y_flipped_path])
            patch = patches.PathPatch(y_flipped_path, **path[1])
            if ax is not None:
                ax.add_patch(patch)
        if user_parameters is not None:
            if label is not None:
                # Draw label
                ax.text(**self.process_label_params(label, all_y_flipped_paths), ha='center', va='center')
        return self.__bounds_from_paths_to_draw(all_y_flipped_paths), self.get_baseline_end(glyph_type, position, rotation=rotation, user_parameters=user_parameters)

    def process_label_params(self, label, all_y_flipped_paths):
        color = (0,0,0)
        xy_skew = (0,0)
        rotation = 0.0
        finalfont = font_manager.FontProperties()
        # Collate parameters (user parameters take priority)
        if 'color' in label:
            color = label['color']
        if 'xy_skew' in label:
            xy_skew = label['xy_skew']
        if 'rotation' in label:
            # Convert to degrees
            rotation = (180/pi) * label['rotation']
        if 'userfont' in label:
            finalfont = font_manager.FontProperties(**label['userfont'])        
        all_path_vertices = []
        for path in all_y_flipped_paths:
            # Find vertices of each path
            path_vertices = path[0].vertices.copy()
            all_path_vertices.append(path_vertices)
        textpos_x, textpos_y = self.calculate_centroid_of_paths(all_path_vertices, xy_skew)
        return {'x':textpos_x, 'y':textpos_y, 's':label['text'], 'color':color, 'fontproperties':finalfont, 'rotation':rotation}

    def calculate_centroid_of_paths(self, all_path_vertices, xy_skew):
        vertices = []
        if len(all_path_vertices) == 1:
            vertices = all_path_vertices[0]
        else:
            vertices_to_array = []
            for path_vertices in all_path_vertices:
                # Find centroid of each path
                length = path_vertices.shape[0]
                sum_x = np.sum(path_vertices[:, 0])
                sum_y = np.sum(path_vertices[:, 1])
                vertices_to_array.append([sum_x/length, sum_y/length])
            vertices = np.array(vertices_to_array)            
        # Find centroid of single path/centroid of multiple centroids
        length = vertices.shape[0]
        sum_x = np.sum(vertices[:, 0])
        sum_y = np.sum(vertices[:, 1])
        # Collate original and relative values
        textpos_x = xy_skew[0] + sum_x/length
        textpos_y = xy_skew[1] + sum_y/length
        return textpos_x, textpos_y

    def get_glyph_bounds(self, glyph_type, position, rotation=0.0, user_parameters=None):
        return self.draw_glyph(None, glyph_type, position, rotation=rotation, user_parameters=user_parameters)

    def get_baseline_end(self, glyph_type, position, rotation=0.0, user_parameters=None):
        glyph = self.glyphs_library[glyph_type]
        merged_parameters = glyph['defaults'].copy()
        if user_parameters is not None:
            # Collate parameters (user parameters take priority) 
            for key in user_parameters.keys():
                merged_parameters[key] = user_parameters[key]
        baseline_path = None
        for path in glyph['paths']:
            if path['class'] == 'baseline':
                svg_text = self.__eval_svg_data(path['d'], merged_parameters)
                baseline_path = svgpath2mpl.parse_path(svg_text)
                break
        if baseline_path is not None:
            # Draw glyph to the axis with correct styling parameters
            baseline_y = glyph['defaults']['baseline_y']
            y_flipped_path = self.__flip_position_rotate_glyph(baseline_path, baseline_y, position, rotation)
            return (y_flipped_path.vertices[1,0], y_flipped_path.vertices[1,1])
        else:
            return None

def __find_bound_of_bounds (bounds_list):
    # Set initial guess
    x_min = bounds_list[0][0][0]
    y_min = bounds_list[0][0][1]
    x_max = bounds_list[0][1][0]
    y_max = bounds_list[0][1][1]
    # Find min and max x/y values
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

def render_reverse_part_list (part_list, glyph_path='glyphs/', padding=0.2, interaction_list=None, module_list=None):
    # Rotate glyphs 180° and reverse order
    for glyph in part_list:
        user_parameters = glyph[1]
        if user_parameters is None:
            user_parameters = {}
            glyph[1] = user_parameters
        if 'rotation' in user_parameters:
            user_parameters['rotation'] += pi
        elif 'rotation' not in user_parameters:
            user_parameters['rotation'] = pi
    if interaction_list is not None:
        for interaction in interaction_list:
            if interaction[3] is None:
                interaction[3] = {}
            if 'direction' in interaction[3]:
                if interaction[3]['direction'] == 'forward':
                    interaction[3]['direction'] = 'reverse'
                if interaction[3]['direction'] == 'reverse':
                    interaction[3]['direction'] == 'forward'
            if 'direction' not in interaction[3]:
                interaction[3]['direction'] = 'reverse'
    fig, ax, baseline_start, baseline_end = render_part_list(part_list, glyph_path=glyph_path, padding=padding, interaction_list=interaction_list, module_list=module_list)
    return fig, ax, baseline_start, baseline_end

def render_part_list (part_list, glyph_path='glyphs/', padding=0.2, interaction_list=None, module_list=None):
    # Render multiple glyphs
    renderer = GlyphRenderer(glyph_path=glyph_path)
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
        # Draw and find bounds of each glyph
        bounds, part_position = renderer.draw_glyph(ax, part[0], part_position, user_parameters=part[1], user_style=part[2])
        bounds_list.append(bounds)
    interaction_bounds_list = []
    if interaction_list is not None:
        interaction_types = ['control','degradation','inhibition','process','stimulation']
        for interaction in interaction_list:
            if interaction[2] in interaction_types:
                # Draw interactions
                sending_bounds = bounds_list[interaction[0]]
                receiving_bounds = bounds_list[interaction[1]]
                bounds = draw_interaction(ax, sending_bounds, receiving_bounds, interaction[2], interaction[3])
                interaction_bounds_list.append(bounds)
            else:
                warnings.warn(f"""'{interaction[2]}' is not a valid interaction type.""")
    module_bounds_list = []
    if module_list is not None:
        for module in module_list:
            start_glyph = module[0]
            end_glyph = module[1]
            if module[0] > module[1]:
            # Ensure start_glyph comes before end_glyph in the plot
                start_glyph = module[1]
                end_glyph = module[0]
            elif part_list[start_glyph][1] is not None and part_list[end_glyph][1] is not None:
            # Check if plot is flipped, then correct
                if 'rotation' in part_list[start_glyph][1] and 'rotation' in part_list[end_glyph][1]:
                    if part_list[start_glyph][1]['rotation'] == pi and part_list[end_glyph][1]['rotation'] == pi:
                        start_glyph = module[1]
                        end_glyph = module[0]
            start_bounds = bounds_list[start_glyph]
            end_bounds = bounds_list[end_glyph]
            # Draw modules
            bounds = draw_module(ax, start_bounds, end_bounds, module[2], module[3])
            module_bounds_list.append(bounds)
    # Unify interaction and module bounds with glyph bounds
    for interaction_bounds in interaction_bounds_list:
        bounds_list.append(interaction_bounds)
    for module_bounds in module_bounds_list:
        bounds_list.append(module_bounds)
    # Automatically find bounds for plot and resize axes
    final_bounds = __find_bound_of_bounds(bounds_list)
    width = (final_bounds[1][0] - final_bounds[0][0])/60.0
    height = (final_bounds[1][1] - final_bounds[0][1])/60.0
    fig_pad = (final_bounds[1][1] - final_bounds[0][1])*padding
    pad = height*padding
    width = width + (pad*2.0)
    height = height + (pad*2.0)
    ax.set_xlim([final_bounds[0][0]-fig_pad, final_bounds[1][0]+fig_pad])
    ax.set_ylim([final_bounds[0][1]-fig_pad, final_bounds[1][1]+fig_pad])
    fig.set_size_inches( (width, height) )
    return fig, ax, start_position, part_position

def draw_module (ax, start_bounds, end_bounds, x_strech, y_strech):
    x_pad = (end_bounds[0][0] - start_bounds[0][0]) / 10
    y_pad = (end_bounds[1][1] - start_bounds[0][1])
    # Bottom left coords
    x1 = ((start_bounds[0][0]) - x_pad) - x_strech
    y1 = ((start_bounds[0][1]) - y_pad) - y_strech
    # Top right coords
    x2 = ((end_bounds[1][0]) + x_pad) + x_strech
    y2 = ((end_bounds[1][1]) + y_pad) + y_strech
    # Draw module
    plt.plot([x1,x2,x2,x1,x1],
             [y1,y1,y2,y2,y1],
             '--',
             color='black')
    return ((x1,y1), (x2,y2))


def draw_interaction (ax, sending_bounds, receiving_bounds, interaction_type, parameters):
        parameters = process_interaction_params(parameters)
        # Assign pad height
        y_pad = (sending_bounds[1][1] / 2) + parameters['heightskew']
        if receiving_bounds[1][1] > sending_bounds[1][1]:
            y_pad = (receiving_bounds[1][1] / 2) + parameters['heightskew']
        if parameters['direction'] == 'reverse':
            y_pad *= -1
        # Find interaction origin and endpoint
        int_origin_x = sending_bounds[0][0] + abs((sending_bounds[1][0] - sending_bounds[0][0]) / 2) + parameters['sending_xy_skew'][0]
        int_end_x = receiving_bounds[0][0] + abs((receiving_bounds[1][0] - receiving_bounds[0][0]) / 2) + parameters['receiving_xy_skew'][0]
        int_origin_y = sending_bounds[1][1] + (y_pad / 3) + parameters['sending_xy_skew'][1]
        int_end_y = receiving_bounds[1][1] + y_pad + parameters['receiving_xy_skew'][1]
        if parameters['direction'] == 'reverse':
            int_origin_y -= (sending_bounds[1][1] - sending_bounds[0][1]) 
            int_end_y -= (receiving_bounds[1][1] - receiving_bounds[0][1])
        # Determine max/min height
        max_height = int_origin_y + y_pad
        if int_end_y > int_origin_y:
            max_height = int_end_y + y_pad
        if parameters['direction'] == 'reverse':
            max_height = int_origin_y + y_pad
            if int_end_y < int_origin_y:
                max_height = int_end_y + y_pad
        # Draw headless interaction
        plt.plot([int_origin_x,
                  int_origin_x,
                  int_end_x,
                  int_end_x],
                 [int_origin_y,
                  max_height,
                  max_height,
                  int_end_y],
                color = parameters['color'],
                lw = parameters['linewidth'],
                zorder = parameters['zorder'] - 5) # Slightly lower zorder than head to prevent overlap
        # Control
        if interaction_type == 'control':
            draw_control(ax, int_end_x, int_end_y, parameters)
        # Degradation
        elif interaction_type == 'degradation':
            draw_degradation(ax, int_end_x, int_end_y, parameters)
        # Inhibition
        elif interaction_type == 'inhibition':
            draw_inhibition(ax, int_end_x, int_end_y, parameters)
        # Process
        elif interaction_type == 'process':
            draw_process(ax, int_end_x, int_end_y, parameters)
        # Stimulation
        elif interaction_type == 'stimulation':
            draw_stimulation(ax, int_end_x, int_end_y, parameters)
        # Find bounds of interaction
        minimum_y = int_origin_y - parameters['headheight'] 
        if int_origin_y > int_end_y:
            minimum_y = int_end_y - parameters['headheight']
        if interaction_type == 'degradation':
            # Degradation has smaller y-min
            minimum_y -= (parameters['headheight'] + parameters['headwidth'] / 2)
        # Assign the bounds
        top_right_bound = (int_origin_x, max_height)
        bottom_left_bound = (int_end_x - parameters['headwidth'], minimum_y)
        if int_end_x > int_origin_x:
            # Reassign bound corners if interaction end comes after its start
            top_right_bound = (int_end_x + parameters['headwidth'], max_height)
            bottom_left_bound = (int_origin_x - parameters['headwidth'], minimum_y)
        return (bottom_left_bound, top_right_bound)

def draw_control(ax, int_end_x, int_end_y, parameters):
    if parameters['direction'] == 'forward':
                plt.plot([int_end_x,
                          int_end_x + parameters['headwidth']/2,
                          int_end_x,
                          int_end_x - parameters['headwidth']/2,
                          int_end_x],
                         [int_end_y,
                          int_end_y - parameters['headheight']/2,
                          int_end_y - parameters['headheight'],
                          int_end_y - parameters['headheight']/2,
                          int_end_y],
                         color = parameters['color'],
                         lw = parameters['linewidth'],
                         zorder = parameters['zorder'])
    elif parameters['direction'] == 'reverse':
                plt.plot([int_end_x,
                          int_end_x + parameters['headwidth']/2,
                          int_end_x,
                          int_end_x - parameters['headwidth']/2,
                          int_end_x],
                         [int_end_y,
                          int_end_y + parameters['headheight']/2,
                          int_end_y + parameters['headheight'],
                          int_end_y + parameters['headheight']/2,
                          int_end_y],
                         color = parameters['color'],
                         lw = parameters['linewidth'],
                         zorder = parameters['zorder'])

def draw_degradation(ax, int_end_x, int_end_y, parameters):
    if parameters['direction'] == 'forward':
                # Plot arrow
                path = Path([[int_end_x, int_end_y],
                            [int_end_x + parameters['headwidth']/2, int_end_y],
                            [int_end_x, int_end_y - parameters['headheight']],
                            [int_end_x - parameters['headwidth']/2, int_end_y],
                            [int_end_x, int_end_y]],
                            [1,2,2,2,2])
                patch = patches.PathPatch(path,
                                          facecolor=parameters['color'],
                                          edgecolor = parameters['color'],
                                          lw = parameters['linewidth'],
                                          zorder = parameters['zorder'])
                ax.add_patch(patch)
                # Plot circle
                circle_origin_y = int_end_y - parameters['headheight'] * 2
                r = parameters['headwidth'] / 2
                patch = patches.Circle((int_end_x, circle_origin_y),
                                       radius = r,
                                       facecolor='white',
                                       edgecolor = parameters['color'],
                                       lw = parameters['linewidth'],
                                       zorder = parameters['zorder'])
                ax.add_patch(patch)
                # Plot line within circle
                deg315 = 315 * pi / 180
                deg225 = 225 * pi / 180
                x1 = int_end_x + (r * cos(deg315))
                y1 = circle_origin_y + (r * cos(deg315))
                x2 = int_end_x + (r * cos(deg225))
                y2 = circle_origin_y + (r * cos(deg225))
                plt.plot([x1, x2],
                         [y1, y2],
                         color = parameters['color'],
                         lw = parameters['linewidth'],
                         zorder = parameters['zorder'] + 500)
    elif parameters['direction'] == 'reverse':
                # Plot arrow
                path = Path([[int_end_x, int_end_y],
                            [int_end_x + parameters['headwidth']/2, int_end_y],
                            [int_end_x, int_end_y + parameters['headheight']],
                            [int_end_x - parameters['headwidth']/2, int_end_y],
                            [int_end_x, int_end_y]],
                            [1,2,2,2,2])
                patch = patches.PathPatch(path,
                                          facecolor=parameters['color'],
                                          edgecolor = parameters['color'],
                                          lw = parameters['linewidth'],
                                          zorder = parameters['zorder'])
                ax.add_patch(patch)
                # Plot circle
                circle_origin_y = int_end_y + parameters['headheight'] * 2
                r = parameters['headwidth'] / 2
                patch = patches.Circle((int_end_x, circle_origin_y),
                                       radius = r,
                                       facecolor='white',
                                       edgecolor = parameters['color'],
                                       lw = parameters['linewidth'],
                                       zorder = parameters['zorder'])
                ax.add_patch(patch)
                # Plot line within circle
                deg315 = 315 * pi / 180
                deg225 = 225 * pi / 180
                x1 = int_end_x + (r * cos(deg315))
                y1 = circle_origin_y + (r * cos(deg315))
                x2 = int_end_x + (r * cos(deg225))
                y2 = circle_origin_y + (r * cos(deg225))
                plt.plot([x1, x2],
                         [y1, y2],
                         color = parameters['color'],
                         lw = parameters['linewidth'],
                         zorder = parameters['zorder'] + 500)

def draw_inhibition(ax, int_end_x, int_end_y, parameters):
    plt.plot([int_end_x - parameters['headwidth'] / 2,
              int_end_x + parameters['headwidth'] / 2],
             [int_end_y,
              int_end_y],
             color = parameters['color'],
             lw = parameters['linewidth'],
             zorder = parameters['zorder'])

def draw_process(ax, int_end_x, int_end_y, parameters):
    if parameters['direction'] == 'forward':
                path = Path([[int_end_x, int_end_y],
                            [int_end_x + parameters['headwidth']/2, int_end_y],
                            [int_end_x, int_end_y - parameters['headheight']],
                            [int_end_x - parameters['headwidth']/2, int_end_y],
                            [int_end_x, int_end_y]],
                            [1,2,2,2,2])
                patch = patches.PathPatch(path,
                                          facecolor=parameters['color'],
                                          edgecolor = parameters['color'],
                                          lw = parameters['linewidth'],
                                          zorder = parameters['zorder'])
                ax.add_patch(patch)
    elif parameters['direction'] == 'reverse':
                path = Path([[int_end_x, int_end_y],
                            [int_end_x + parameters['headwidth']/2, int_end_y],
                            [int_end_x, int_end_y + parameters['headheight']],
                            [int_end_x - parameters['headwidth']/2, int_end_y],
                            [int_end_x, int_end_y]],
                            [1,2,2,2,2])
                patch = patches.PathPatch(path,
                                          facecolor=parameters['color'],
                                          edgecolor = parameters['color'],
                                          lw = parameters['linewidth'],
                                          zorder = parameters['zorder'])
                ax.add_patch(patch)

def draw_stimulation(ax, int_end_x, int_end_y, parameters):
    if parameters['direction'] == 'forward':
                path = Path([[int_end_x, int_end_y],
                            [int_end_x + parameters['headwidth']/2, int_end_y],
                            [int_end_x, int_end_y - parameters['headheight']],
                            [int_end_x - parameters['headwidth']/2, int_end_y],
                            [int_end_x, int_end_y]],
                            [1,2,2,2,2])
                patch = patches.PathPatch(path,
                                          facecolor='white',
                                          edgecolor = parameters['color'],
                                          lw = parameters['linewidth'],
                                          zorder = parameters['zorder'])
                ax.add_patch(patch)
    elif parameters['direction'] == 'reverse':
                path = Path([[int_end_x, int_end_y],
                            [int_end_x + parameters['headwidth']/2, int_end_y],
                            [int_end_x, int_end_y + parameters['headheight']],
                            [int_end_x - parameters['headwidth']/2, int_end_y],
                            [int_end_x, int_end_y]],
                            [1,2,2,2,2])
                patch = patches.PathPatch(path,
                                          facecolor='white',
                                          edgecolor = parameters['color'],
                                          lw = parameters['linewidth'],
                                          zorder = parameters['zorder'])
                ax.add_patch(patch)

def process_interaction_params(parameters):
    final_parameters = {'color': (0,0,0),
                        'heightskew': 0,
                        'headheight': 2,
                        'headwidth': 2,
                        'zorder': 0,
                        'direction': 'forward',
                        'linewidth': 1,
                        'sending_xy_skew': (0,0),
                        'receiving_xy_skew': (0,0)}
    if parameters is None:
        return final_parameters
    # Collate interaction parameters
    for key in parameters:
        if key in final_parameters:
            final_parameters[key] = parameters[key]
        else:
            warnings.warn(f"""'{key}' is not a valid interaction parameter.""")
    # Amplify zorder to ensure all drawings composing the interaction can be grouped on Z axis
    final_parameters['zorder'] *= 100
    return final_parameters
