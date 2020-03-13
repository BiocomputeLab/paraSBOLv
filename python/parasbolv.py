#!/usr/bin/env python
"""
Parametric SBOL Visual (parasbolv)

A simple and lightweight library for rendering parametric SVG versions
of the SBOL Visual glyphs using matplotlib. Is able to load a directory 
of glyphs and provides access to all style and geometry customisations.
"""

import svgpath2mpl
import os
import glob
import xml.etree.ElementTree as ET
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

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
            c_els = val[5:-1].split(',')
            r_val = float(c_els[0])/255.0
            g_val = float(c_els[1])/255.0
            b_val = float(c_els[2])/255.0
            a_val = float(c_els[3])
            converted_val = (r_val, g_val, b_val)
        elif val.startswith('rgb'):
            c_els = val[4:-1].split(',')
            r_val = float(c_els[0])/255.0
            g_val = float(c_els[1])/255.0
            b_val = float(c_els[2])/255.0
            converted_val = (r_val, g_val, b_val)
        elif val.endswith('pt'):
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
            key_val = [x.strip() for x in el.split(':')]
            if key_val[0] in self.svg2mpl_style_map.keys():
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
            org_x = cur_vert[0]
            org_flipped_y = baseline_y-(cur_vert[1]-baseline_y)
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
        glyph = self.glyphs_library[glyph_type]
        merged_parameters = glyph['defaults'].copy()
        if user_parameters is not None:
            # Collate parameters (user parameters take priority) 
            for key in user_parameters.keys():
                merged_parameters[key] = user_parameters[key]
        paths_to_draw = []
        for path in glyph['paths']:
            if path['class'] not in ['baseline', 'bounding-box']:
                merged_style = path['style']
                if path['id'] is not None and user_style is not None and path['id'] in user_style.keys():
                    # Merge the styling dictionaries (user takes preference)
                    merged_style = user_style[path['id']].copy()
                    for k in path['style'].keys():
                        if k not in merged_style.keys():
                            merged_style[k] =  path['style'][k]
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
        return self.__bounds_from_paths_to_draw(all_y_flipped_paths), self.get_baseline_end(glyph_type, position, rotation=rotation, user_parameters=user_parameters)

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

def render_part_list (part_list, glyph_path='glyphs/', padding=0.2):
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
        bounds, part_position = renderer.draw_glyph(ax, part[0], part_position, user_parameters=part[1], user_style=part[2])
        bounds_list.append(bounds)
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

