#!/usr/bin/env python

"""
paraSBOLv

A simple and lightweight library for rendering parametric SVG versions
of the SBOL Visual symbols using matplotlib. It is able to load a directory 
of glyphs and provides access to all style and geometry customisations,
and provides a number of helper functions to handle part lists, modules 
and interactions.
"""

import warnings 
import os
import sys
import glob
import xml.etree.ElementTree as ET
import re
from math import cos, sin, pi

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as font_manager
from matplotlib.path import Path

from parasbolv.svgpath2mpl import parse_path

__author__  = 'Thomas E. Gorochowski <tom@chofski.co.uk>, \
               Charlie Clark <charlieclark1.e.e.2019@bristol.ac.uk>'
__license__ = 'MIT'
__version__ = '0.1'

class GlyphRenderer:
    """ Class to load and render using matplotlib parametric SVG glyphs.
    """

    def __init__(self, glyph_path=None, global_defaults=None):
        """
        Parameters
        ----------
        glyph_path: str
            File path at which the glyph SVG files are stored,
            relative to the directory in which parasbolv.py is
            contained.
        global_defaults: 
        """
        self.svg2mpl_style_map = {}
        self.svg2mpl_style_map['fill'] = 'facecolor'
        self.svg2mpl_style_map['stroke'] = 'edgecolor'
        self.svg2mpl_style_map['stroke-width'] = 'linewidth'
        if glyph_path is None:
            self.glyphs_library, self.glyph_soterm_map = self.load_package_glyphs()
        else:
            self.glyphs_library, self.glyph_soterm_map = self.load_glyphs_from_path(glyph_path)

    def __process_unknown_val (self, val):
        """Converts an unknown value into the correct type.

        Parameters
        ----------
        val: string
            Represents an unknown value
            such as colour or line width.
        """
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
        """Converts style text into a dictionary.

        Parameters
        ----------
        style_text: str
            Contains concatenated SVG style information
            such as `fill`, `stroke` and `stroke-width`.
        """
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
        """Extracts all the relevant SVG details from an XML tag in the SVG.

        Parameters
        ----------
        tag_attributes: dict
            Dictionary derived from XML structure
            containing SVG parameters.
        """
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
        """Extracts and then replaces equation with evaluated version using regular expression.

        See: https://stackoverflow.com/questions/38734335/python-regex-replace-bracketed-text-with-contents-of-brackets

        Parameters
        ----------
        svg_text: str
            SVG text containing unsubstituted values.
        parameters: dict
            Contains parameter values to be substituted
            into `svg_text` for evaluation.
        """
        return re.sub(r"{([^{}]+)}", lambda m: str(eval(m.group()[1:-1], parameters)), svg_text)

    def __flip_position_rotate_glyph(self, path, baseline_y, position, rotation):
        """Flips paths into matplotlib default orientation and position, and rotates paths.

        Parameters
        ----------
        path: Matplotlib Path object - https://matplotlib.org/stable/api/path_api.html
            Path to be transformed.
        baseline_y: float
            y value of the baseline.
        position: tuple
            Path position, format (x,y).
        rotation: float
            Rotation value in radians.
        """
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
        """Calculates the bounding box from a set of paths.

        Parameters
        ----------
        paths: list
           List containing Matplotlib Path objects.
        """
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
        """Loads glyph information from an SVG file.

        Parameters
        ----------
        filename: str
            Absolute file path of SVG file.
        """
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

    def load_package_glyphs(self):
        """Finds the directory with packaged glyphs and loads them.
        """
        d = os.path.dirname(sys.modules[__name__].__file__)
        path = os.path.join(d, 'glyphs')
        return self.load_glyphs_from_path(path)

    def load_glyphs_from_path(self, path):
        """Loads glyph information from SVG files in a directory.

        Parameters
        ----------
        path: str
            Absolute file path of directory containing glyphs.
        """
        glyphs_library = {}
        glyph_soterm_map = {}
        for infile in glob.glob( os.path.join(path, '*.svg') ):
            glyph_type, glyph_soterms, glyph_data = self.load_glyph(infile)
            glyphs_library[glyph_type] = glyph_data
            for soterm in glyph_soterms:
                glyph_soterm_map[soterm] = glyph_type
        return glyphs_library, glyph_soterm_map

    def draw_glyph(self, ax, glyph_type, position, rotation=0.0, user_parameters=None, user_style=None):
        """Draws a glyph to Matploblib Axes.

        Parameters
        ----------
        ax: Ax object
            https://matplotlib.org/stable/api/axes_api.html
        glyph_type: str
            Name of the glyph being drawn.
        position: tuple
            Position to draw to, format (x,y).
        rotation: float, optional
            Rotation of glyph in radians.
        user_parameters: dict, optional
            Dictionary containing sizing/label parameters of glyph.
        user_style: dict, optional
            Dictionary containing style parameters of glyph.
        """
        try:
        # Check glyph type exists	
            glyph = self.glyphs_library[glyph_type]	
        except:	
            class Invalid_glyph_type(Exception):	
                pass	
            raise Invalid_glyph_type(f"""'{glyph_type}' is not a valid glyph.""")
        merged_parameters = glyph['defaults'].copy()
        if user_parameters is not None:
            # Find label
            label_parameters = None
            if 'label_parameters' in user_parameters:
                label_parameters = user_parameters['label_parameters']
            # Find rotation in user_parameters (keyword arg takes priority)
            if rotation == 0.0 and 'rotation' in user_parameters:
                rotation = user_parameters['rotation']
            # Collate parameters (user parameters take priority)
            for key in user_parameters.keys():
                if key not in glyph['defaults'] and key != 'label_parameters' and key != 'rotation' and key != 'y_offset':
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
                # Call to svgpath2mpl
                paths_to_draw.append([parse_path(svg_text), merged_style])
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
            if label_parameters is not None:
                # Draw label
                ax.text(**self.process_label_params(label_parameters, all_y_flipped_paths), ha='center', va='center')
        return self.__bounds_from_paths_to_draw(all_y_flipped_paths), self.get_baseline_end(glyph_type, position, rotation=rotation, user_parameters=user_parameters)

    def process_label_params(self, label_parameters, paths):
        """Formats and completes label parameters.

        Parameters
        ----------
        label_parameters: dict
            Dictionary containing label parameters.
        paths: list
            List of paths composing the glyph.
        """
        color = (0,0,0)
        xy_skew = (0,0)
        rotation = 0.0
        finalfont = font_manager.FontProperties()
        # Collate parameters (user parameters take priority)
        if 'color' in label_parameters:
            color = label_parameters['color']
        if 'xy_skew' in label_parameters:
            xy_skew = label_parameters['xy_skew']
        if 'rotation' in label_parameters:
            # Convert to degrees
            rotation = (180/pi) * label_parameters['rotation']
        if 'userfont' in label_parameters:
            finalfont = font_manager.FontProperties(**label_parameters['userfont'])        
        all_path_vertices = []
        for path in paths:
            # Find vertices of each path
            path_vertices = path[0].vertices.copy()
            all_path_vertices.append(path_vertices)
        textpos_x, textpos_y = self.calculate_centroid_of_paths(all_path_vertices, xy_skew)
        return {'x':textpos_x, 'y':textpos_y, 's':label_parameters['text'], 'color':color, 'fontproperties':finalfont, 'rotation':rotation}

    def calculate_centroid_of_paths(self, all_path_vertices, xy_skew):
        """Calculates central point of paths provided.

        Parameters
        ----------
        all_path_vertices: list
            Contains vertices of every path.
        xy_skew: tuple
            Skew of centroid in x and y
            directions, format (x,y).
        """
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
        """Returns bounds of glyph.

        Parameters
        ----------
        glyph_type: str
            Type of glyph.
        position: tuple
            Position of glyph, format (x,y).
        rotation: float, optional
            Rotation of glyph in radians.
        user_parameters: dict, optional
            Dictionary containing sizing/label parameters of glyph.
        """
        return self.draw_glyph(None, glyph_type, position, rotation=rotation, user_parameters=user_parameters)

    def get_baseline_end(self, glyph_type, position, rotation=0.0, user_parameters=None):
        """Finds the point following a glyph from which the baseline should end.

        Parameters
        ----------
        glyph_type: str
            Type of glyph.
        position: tuple
            Position of glyph, format (x,y).
        rotation: float, optional
            Rotation of glyph in radians.
        user_parameters: dict, optional
            Dictionary containing sizing/label parameters of glyph.
        """
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
                # Call to svgpath2mpl
                baseline_path = parse_path(svg_text)
                break
        if baseline_path is not None:
            # Draw glyph to the axis with correct styling parameters
            baseline_y = glyph['defaults']['baseline_y']
            y_flipped_path = self.__flip_position_rotate_glyph(baseline_path, baseline_y, position, rotation)
            return (y_flipped_path.vertices[1,0], y_flipped_path.vertices[1,1])
        else:
            return None

def __find_bound_of_bounds (bounds_list):
    """Find the bounding box of a list of bounds.

    Parameters
    ----------
    bounds_list: list
        List containing bounds to find bounding box of.
    """
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

class Construct(object):
    """A modifiable construct consisting of
       SBOL glyphs, interactions and modules.
       
       NOTE: Attributes below lacking
       description are documented in the
       __init__ docstring of this class.

       Attributes
       ----------
       bounds: tuple
           Represents the bounds of the
           construct, formatted as ((x1,y1), (x2,y2))
           where (x1,y1) are the coordinates of the
           lower left vertex and (x2, y2) are the
           coordinates of the top right vertex.
       part_list: list
       renderer: object
       padding: float
       fig: object
       ax: object
       start_position: tuple
       additional_bounds_list: list
       interaction_list: list
       module_list: list
       rotation: float
    """

    def __init__ (self, part_list, renderer, padding=0.2, fig=None, ax=None, start_position=(0, 0), additional_bounds_list=None, interaction_list=None, module_list=None, rotation=0.0):
        """
        Parameters
        ----------
        part_list: list
            Contains all glyphs in the
            construct. Each glyph is represented
            by a list containing three elements:
            [0] Glyph type, represented by a string,
            [1] the user_parameters dictionary, and
            [2] the style_parameters dictionary. 
        renderer: object
            ParaSB0Lv GlyphRenderer object defined
            above.
        padding: float, optional
            Scale of the space added to axis limits.
        fig: object, optional
            Matplotlib Figure object.
        ax: object, optional
            Matplotlib Axes object.
        start_position: tuple, optional
            Represents the origin of the construct,
            format (x, y).
        additional_bounds_list: list, optional
            Contains additional bounds to be
            incorporated into the construct
            bounds when using self.draw()
            and self.update_bounds().
        interaction_list: list, optional
            Specifies interactions between
            construct glyphs. Each interaction
            is represented by a list containing
            four elements: [0] The origin glyph
            of the interaction, represented by
            the glyph's index, [1] the receiving
            glyph of the interaction, represented
            similarly, [2] the interaction type
            string, and [3] the interaction_parameters
            dictionary.
        module_list: list, optional
            Specifies modules within the construct.
            Each module is represented by a list
            containing four elements: [0] The first
            glyph within the module, represented by
            the index of the glyph, [1] the final glyph
            of the module, represented similarly, [2]
            x_stretch, an integer to strech/squash the
            module in the x direction, [3] y_strech,
            identical but in the y direction.
        rotation: float, optional
            Float representing the rotation of
            the construct in radians.
        """
        self.renderer = renderer
        self.padding = padding
        self.fig = fig
        self.ax = ax
        if self.fig is None or self.ax is  None:
            self.fig, self.ax = plt.subplots()
        self.start_position = start_position
        self.additional_bounds_list = additional_bounds_list
        
        # Data structure
        self.part_list = part_list
        self.interaction_list = interaction_list
        self.module_list = module_list
        self._rotation = 0.0
        self.rotation = rotation # Radians
        self.bounds = None
        self.update_bounds()

    # Automatically update construct rotation
    @property
    def rotation(self):
        return self._rotation
    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self.set_rotation(value)
    
    def set_rotation (self, rotation):
        """Sets the rotation of the construct.

        NOTE: the self.rotation attribute
        should be modified instead of directly
        calling this method.

        Parameters
        ----------
        rotation: float
            Rotation value in radians to be applied
            to the construct.
        """
        part_list = self.part_list
        for glyph in part_list:
            user_parameters = glyph[1]
            if user_parameters is None:
                user_parameters = {}
                glyph[1] = user_parameters
            if 'rotation' in user_parameters:
                user_parameters['rotation'] = rotation
            elif 'rotation' not in user_parameters:
                user_parameters['rotation'] = rotation
        self.part_list = part_list

    def reverse_interactions (self):
        """Reverses the side interactions are drawn on.
        """
        if self.interaction_list is not None:
            for interaction in self.interaction_list:
                if interaction[3] is None:
                    interaction[3] = {}
                if 'direction' in interaction[3]:
                    if interaction[3]['direction'] == 'forward':
                        interaction[3]['direction'] = 'reverse'
                    elif interaction[3]['direction'] == 'reverse':
                        interaction[3]['direction'] = 'forward'
                if 'direction' not in interaction[3]:
                    interaction[3]['direction'] = 'reverse'

    def update_bounds (self):
        """Updates the bounds of the constuct.
        """
        self.bounds = self.draw(draw_for_bounds = True)[4]
        self.bounds = ((self.bounds[0], self.bounds[1]))

    def draw (self, draw_for_bounds = False):
        """Draws the construct using Matplotlib.

        Parameters
        ----------
        draw_for_bounds: bool, optional
            Indicates if the construct is being
            drawn to update the self.bounds 
            attribute.
        """
        # Draw the construct
        bounds_to_add = []
        if self.additional_bounds_list is not None:
            # Include additional bounds
            for additional_bounds in self.additional_bounds_list:
                bounds_to_add.append(additional_bounds)
        if draw_for_bounds == False:
            fig, ax, baseline_start, baseline_end, bounds = render_part_list(self.part_list, self.renderer, padding=self.padding, fig=self.fig, ax=self.ax, rotation = self.rotation, start_position=self.start_position, additional_bounds_list = bounds_to_add, interaction_list=self.interaction_list, module_list=self.module_list)
            return fig, ax, baseline_start, baseline_end, bounds
        elif draw_for_bounds == True:
            # Temporary rendering pathway to generate bounds
            temp_fig, temp_ax = plt.subplots()
            fig, ax, baseline_start, baseline_end, bounds = render_part_list(self.part_list, self.renderer, padding=self.padding, fig=temp_fig, ax=temp_ax, rotation = self.rotation, start_position=self.start_position, additional_bounds_list = bounds_to_add, interaction_list=self.interaction_list, module_list=self.module_list)
            plt.close()
            return fig, ax, baseline_start, baseline_end, bounds


def render_part_list (part_list, renderer, padding=0.2, fig = None, ax = None, rotation = 0.0, start_position=(0, 0), additional_bounds_list = None, interaction_list=None, module_list=None):
    """Renders multiple glyphs in sequence.

    NOTE: See parameters of the __init__
    method within the Construct class 
    for parameter descriptions.

    Parameters
    ----------
    part_list: list
    renderer: object
    padding: float, optional
    fig: object, optional
    ax: object, optional
    rotation: float, optional
    start_position: tuple, optional
    additional_bounds_list: list, optional
    interaction_list: list, optional
    module_list: list, optional
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    part_position = start_position
    bounds_list = []
    for part in part_list:
        # Draw glyphs
        if part[1] is not None and 'y_offset' in part[1]:
            pre_part_position = part_position
            part_position = (part_position[0], part_position[1] + part[1]['y_offset'])
            bounds, part_position = renderer.draw_glyph(ax, part[0], part_position, user_parameters=part[1], user_style=part[2])
            bounds_list.append(bounds)
            # Correct part_position to remove y_offset
            part_position = (part_position[0], pre_part_position[1])
        else:
            bounds, part_position = renderer.draw_glyph(ax, part[0], part_position, user_parameters=part[1], user_style=part[2])
            bounds_list.append(bounds)
    interaction_bounds_list = []
    if interaction_list is not None:
        interaction_types = ['control','degradation','inhibition','process','stimulation']
        for interaction in interaction_list:
            if interaction[2] in interaction_types:
                # Find bounds of glyphs
                n = 0
                for part in part_list:
                    if part is interaction[0]:
                        sending_bounds = bounds_list[n]
                        break
                    n += 1
                n = 0
                for part in part_list:
                    if part is interaction[1]:
                        receiving_bounds = bounds_list[n]
                        break
                    n += 1
                # Draw interactions
                bounds = draw_interaction(ax, sending_bounds, receiving_bounds, interaction[2], interaction[3], rotation = rotation)
                interaction_bounds_list.append(bounds)
            else:
                warnings.warn(f"""'{interaction[2]}' is not a valid interaction type.""")
    module_bounds_list = []
    if module_list is not None:
        for module in module_list:
            start_glyph = module[0]
            end_glyph = module[1]
            '''
            # Check if plot is flipped, then correct
            if 'rotation' in part_list[start_glyph][1] and 'rotation' in part_list[end_glyph][1]:
                if part_list[start_glyph][1]['rotation'] == pi and part_list[end_glyph][1]['rotation'] == pi:
                    start_glyph = module[1]
                    end_glyph = module[0]
            '''
            # Find bounds of glyphs
            n = 0
            for part in part_list:
                if part is start_glyph:
                    start_bounds = bounds_list[n]
                    break
                n += 1
            n = 0
            for part in part_list:
                if part is end_glyph:
                    end_bounds = bounds_list[n]
                    break
                n += 1
            # Draw modules
            bounds = draw_module(ax, start_bounds, end_bounds, module[2], module[3])
            module_bounds_list.append(bounds)
    # Unify interaction, module, and additional bounds with glyph bounds
    for interaction_bounds in interaction_bounds_list:
        bounds_list.append(interaction_bounds)
    for module_bounds in module_bounds_list:
        bounds_list.append(module_bounds)
    for additional_bounds in additional_bounds_list:
        bounds_list.append(additional_bounds)
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
    return fig, ax, start_position, part_position, final_bounds

def draw_module (ax, start_bounds, end_bounds, x_strech, y_strech):
    """Draws a module bounding at least two glyphs in a construct.

    Parameters
    ----------
    ax: object
        Matplotlib Axes object.
    start_bounds: tuple
        Bounds of the starting glyph of the module,
        format ((x1,y1), (x2,y2)), where (x1,y1)
        is the bottom left vertex and (x2,y2) the
        top right.
    end_bounds: tuple
        Bounds of the ending glyph of the module,
        formatted identically.
    x_strech: float
        Strech value in x direction to be applied
        to the module.
    y_strech: float
        Strech value in y direction to be applied
        to the module.
    """
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


def draw_interaction (ax, sending_bounds, receiving_bounds, interaction_type, parameters, rotation = 0.0):
    """Draws an interaction between two glyphs in a construct.

    Parameters
    ----------
    ax: object
        Matplotlib Axes object.
    sending_bounds: tuple
        Bounds of the sending glyph of the
        interaction, format ((x1,y1), (x2,y2)),
        where (x1,y1) is the bottom left vertex
        and (x2,y2) the top right.
    receiving_bounds: tuple
        Bounds of the receiving glyph of the
        interaction, formatted identically.
    interaction_type: string
        Type of interaction being drawn, from
        'control', 'degradation', 'inhibition',
        'process', 'stimulation'.
    parameters: dict
        Contains parameters for the interaction.
        See docstring for the function
        `process_interaction_params` for details.
    rotation: float, optional
        Rotation, in radians, of construct that
        interactions are to be drawn to.
    """
    parameters = process_interaction_params(parameters)
    # Convert to degrees
    rotation = (180/pi) * rotation
    if parameters['direction'] == 'reverse':
        # Flip side to draw interaction on
        rotation += 180
    # Assign pad height
    initial_distance = parameters['heightskew'] * 1.5
    y_pad = parameters['heightskew'] * 2
    if interaction_type == 'degradation': # Degradation is bigger than the other interactions
        initial_distance = parameters['heightskew'] * 3 
    # Find centroid of glyph bounds
    origin_cent = (sending_bounds[0][0] + (sending_bounds[1][0] - sending_bounds[0][0])/2, sending_bounds[0][1] + (sending_bounds[1][1] - sending_bounds[0][1])/2)
    end_cent = (receiving_bounds[0][0] + (receiving_bounds[1][0] - receiving_bounds[0][0])/2, receiving_bounds[0][1] + (receiving_bounds[1][1] - receiving_bounds[0][1])/2)        
    # Find interaction origin and endpoint - (h + rsin(a), k + rcos(a))
    rotation = rotation % 360
    bearing = 360 - rotation
    int_origin_x = (origin_cent[0] + initial_distance*sin(bearing * pi/180)) + parameters['sending_xy_skew'][0]
    int_origin_y = (origin_cent[1] + initial_distance*cos(bearing * pi/180)) + parameters['sending_xy_skew'][1]
    int_end_x = (end_cent[0] + initial_distance*sin(bearing * pi/180)) + parameters['receiving_xy_skew'][0]
    int_end_y = (end_cent[1] + initial_distance*cos(bearing * pi/180)) + parameters['sending_xy_skew'][1]
    # Determine max/min height
    int_origin_max = (int_origin_x + y_pad*sin(bearing * pi/180), int_origin_y + y_pad*cos(bearing * pi/180))
    int_end_max = (int_end_x + y_pad*sin(bearing * pi/180), int_end_y + y_pad*cos(bearing * pi/180))
    max_height = 3
    # Draw headless interaction
    plt.plot([int_origin_x,
              int_origin_max[0],
              int_end_max[0],
              int_end_x],
             [int_origin_y,
              int_origin_max[1],
              int_end_max[1],
              int_end_y],
            color = parameters['color'],
            lw = parameters['linewidth'],
            zorder = parameters['zorder'] - 5) # Slightly lower zorder than head to prevent overlap
    # Control
    if interaction_type == 'control':
        draw_control(ax, int_end_x, int_end_y, parameters, rotation = rotation)
    # Degradation
    elif interaction_type == 'degradation':
        draw_degradation(ax, int_end_x, int_end_y, parameters, rotation = rotation)
    # Inhibition
    elif interaction_type == 'inhibition':
        draw_inhibition(ax, int_end_x, int_end_y, parameters, rotation = rotation)
    # Process
    elif interaction_type == 'process':
        draw_process(ax, int_end_x, int_end_y, parameters, rotation = rotation)
    # Stimulation
    elif interaction_type == 'stimulation':
        draw_stimulation(ax, int_end_x, int_end_y, parameters, rotation = rotation)
    # Find bounds of interaction
    xcoords = [int_origin_max[0], int_end_max[0], int_origin_x, int_end_x]
    ycoords = [int_origin_max[1], int_end_max[1], int_origin_y, int_end_y]
    minbounds = (min(xcoords),min(ycoords))
    maxbounds = (max(xcoords),max(ycoords))
    return (minbounds, maxbounds)

def draw_control(ax, int_end_x, int_end_y, parameters, rotation = 0.0):
    """Draws the head of a control interaction.

    Parameters
    ----------
    ax: object
        Matplotlib Axes object.
    int_end_x: float
        x value for the point at the end of
        the interaction.
    int_end_y: float
        y value for the point at the end of
        the interaction.
    parameters: dict
        Contains parameters for the interaction.
        See docstring for the function
        `process_interaction_params` for details.
    rotation: float, optional
        Rotation of the construct the interaction
        is being drawn to.
    """
    if parameters['headheight'] > parameters['headheight']:
        parameters['headwidth'] = parameters['headheight']
    bearing1 = ((360 - (2 * rotation)) / 2) - 45
    bearing2 = ((360 - (2 * rotation)) / 2) + 45
    point1 = (int_end_x + (parameters['headwidth'] / 2) * sin(bearing1*pi/180), int_end_y + (parameters['headwidth'] / 2) * cos(bearing1*pi/180))
    point2 = (point1[0] + (parameters['headwidth'] / 2) * sin(bearing2*pi/180), point1[1] + (parameters['headwidth'] / 2) * cos(bearing2*pi/180)) 
    point3 = (int_end_x + (parameters['headwidth'] / 2) * sin(bearing2*pi/180), int_end_y + (parameters['headwidth'] / 2) * cos(bearing2*pi/180))
    # Draw
    plt.plot([int_end_x,
              point1[0],
              point2[0],
              point3[0],
              int_end_x],
             [int_end_y,
              point1[1],
              point2[1],
              point3[1],
              int_end_y],
              color = parameters['color'],
              lw = parameters['linewidth'],
              zorder = parameters['zorder'])

def draw_degradation(ax, int_end_x, int_end_y, parameters, rotation = 0.0):
    """Draws the head of a degradation interaction.

    Parameters
    ----------
    ax: object
        Matplotlib Axes object.
    int_end_x: float
        x value for the point at the end of
        the interaction.
    int_end_y: float
        y value for the point at the end of
        the interaction.
    parameters: dict
        Contains parameters for the interaction.
        See docstring for the function
        `process_interaction_params` for details.
    rotation: float, optional
        Rotation of the construct the interaction
        is being drawn to.
    """
    bearing1 = 90 - rotation
    bearing2 = ((360 - (2 * bearing1)) / 2) + (bearing1 * 2)
    bearing3 = ((360 - (2 * rotation)) / 2)
    base1 = (int_end_x + (parameters['headwidth'] / 2) * sin(bearing1*pi/180), int_end_y + (parameters['headwidth'] / 2) * cos(bearing1*pi/180))
    base2 = (int_end_x + (parameters['headwidth'] / 2) * sin(bearing2*pi/180), int_end_y + (parameters['headwidth'] / 2) * cos(bearing2*pi/180))
    point = (int_end_x + (parameters['headheight']) * sin(bearing3*pi/180), int_end_y + (parameters['headheight']) * cos(bearing3*pi/180))
    # Arrow
    path = Path([[int_end_x, int_end_y],
                [base1[0], base1[1]],
                [point[0], point[1]],
                [base2[0], base2[1]]],
                [1,2,2,2])
    patch = patches.PathPatch(path,
                              facecolor=parameters['color'],
                              edgecolor = parameters['color'],
                              lw = parameters['linewidth'],
                              zorder = parameters['zorder'])
    ax.add_patch(patch)
    # Circle
    origin = (int_end_x + (parameters['headheight']*2 + parameters['headwidth']/2) * sin(bearing3*pi/180), int_end_y + (parameters['headheight']*2 + parameters['headwidth']/2) * cos(bearing3*pi/180))
    r = parameters['headwidth'] / 2
    patch = patches.Circle((origin[0], origin[1]),
                            radius = r,
                            facecolor='white',
                            edgecolor = parameters['color'],
                            lw = parameters['linewidth'],
                            zorder = parameters['zorder'])
    ax.add_patch(patch)
    # Line within circle
    bearing1 = (360 - rotation) + 45
    bearing2 = (360 - rotation) + 225
    end1 = (origin[0] + (parameters['headwidth'] / 2) * sin(bearing1*pi/180), origin[1] + (parameters['headwidth'] / 2) * cos(bearing1*pi/180))
    end2 = (origin[0] + (parameters['headwidth'] / 2) * sin(bearing2*pi/180), origin[1] + (parameters['headwidth'] / 2) * cos(bearing2*pi/180))
    plt.plot([end1[0], end2[0]],
             [end1[1], end2[1]],
             color = parameters['color'],
             lw = parameters['linewidth'],
             zorder = parameters['zorder'] + 500)

def draw_inhibition(ax, int_end_x, int_end_y, parameters, rotation = 0.0):
    """Draws the head of an inhibition interaction.

    Parameters
    ----------
    ax: object
        Matplotlib Axes object.
    int_end_x: float
        x value for the point at the end of
        the interaction.
    int_end_y: float
        y value for the point at the end of
        the interaction.
    parameters: dict
        Contains parameters for the interaction.
        See docstring for the function
        `process_interaction_params` for details.
    rotation: float, optional
        Rotation of the construct the interaction
        is being drawn to.
    """
    bearing1 = 90 - rotation
    bearing2 = ((360 - (2 * bearing1)) / 2) + (bearing1 * 2)
    base1 = (int_end_x + (parameters['headwidth'] / 2) * sin(bearing1*pi/180), int_end_y + (parameters['headwidth'] / 2) * cos(bearing1*pi/180))
    base2 = (int_end_x + (parameters['headwidth'] / 2) * sin(bearing2*pi/180), int_end_y + (parameters['headwidth'] / 2) * cos(bearing2*pi/180))
    # Draw
    plt.plot([base1[0],
              base2[0]],
             [base1[1],
              base2[1]],
             color = parameters['color'],
             lw = parameters['linewidth'],
             zorder = parameters['zorder'])

def draw_process(ax, int_end_x, int_end_y, parameters, rotation = 0.0):
    """Draws the head of a process interaction.

    Parameters
    ----------
    ax: object
        Matplotlib Axes object.
    int_end_x: float
        x value for the point at the end of
        the interaction.
    int_end_y: float
        y value for the point at the end of
        the interaction.
    parameters: dict
        Contains parameters for the interaction.
        See docstring for the function
        `process_interaction_params` for details.
    rotation: float, optional
        Rotation of the construct the interaction
        is being drawn to.
    """
    bearing1 = 90 - rotation
    bearing2 = ((360 - (2 * bearing1)) / 2) + (bearing1 * 2)
    bearing3 = ((360 - (2 * rotation)) / 2)
    base1 = (int_end_x + (parameters['headwidth'] / 2) * sin(bearing1*pi/180), int_end_y + (parameters['headwidth'] / 2) * cos(bearing1*pi/180))
    base2 = (int_end_x + (parameters['headwidth'] / 2) * sin(bearing2*pi/180), int_end_y + (parameters['headwidth'] / 2) * cos(bearing2*pi/180))
    point = (int_end_x + (parameters['headheight']) * sin(bearing3*pi/180), int_end_y + (parameters['headheight']) * cos(bearing3*pi/180))
    # Draw
    path = Path([[int_end_x, int_end_y],
                [base1[0], base1[1]],
                [point[0], point[1]],
                [base2[0], base2[1]]],
                [1,2,2,2])
    patch = patches.PathPatch(path,
                              facecolor=parameters['color'],
                              edgecolor = parameters['color'],
                              lw = parameters['linewidth'],
                              zorder = parameters['zorder'])
    ax.add_patch(patch)

def draw_stimulation(ax, int_end_x, int_end_y, parameters, rotation = 0.0):
    """Draws the head of a stimulation interaction.

    Parameters
    ----------
    ax: object
        Matplotlib Axes object.
    int_end_x: float
        x value for the point at the end of
        the interaction.
    int_end_y: float
        y value for the point at the end of
        the interaction.
    parameters: dict
        Contains parameters for the interaction.
        See docstring for the function
        `process_interaction_params` for details.
    rotation: float, optional
        Rotation of the construct the interaction
        is being drawn to.
    """
    bearing1 = 90 - rotation
    bearing2 = ((360 - (2 * bearing1)) / 2) + (bearing1 * 2)
    bearing3 = ((360 - (2 * rotation)) / 2)
    base1 = (int_end_x + (parameters['headwidth'] / 2) * sin(bearing1*pi/180), int_end_y + (parameters['headwidth'] / 2) * cos(bearing1*pi/180))
    base2 = (int_end_x + (parameters['headwidth'] / 2) * sin(bearing2*pi/180), int_end_y + (parameters['headwidth'] / 2) * cos(bearing2*pi/180))
    point = (int_end_x + (parameters['headheight']) * sin(bearing3*pi/180), int_end_y + (parameters['headheight']) * cos(bearing3*pi/180))
    # Draw
    path = Path([[int_end_x, int_end_y],
                [base1[0], base1[1]],
                [point[0], point[1]],
                [base2[0], base2[1]],
                [int_end_x, int_end_y]],
                [1,2,2,2,2])
    patch = patches.PathPatch(path,
                              facecolor='white',
                              edgecolor = parameters['color'],
                              lw = parameters['linewidth'],
                              zorder = parameters['zorder'])
    ax.add_patch(patch)

def process_interaction_params(parameters):
    """Formats and completes parameters to draw an interaction.

    Parameters
    ----------
    parameters: dict
        Contains mutable interaction parameters:
            color: tuple
                Format (r,g,b).
            heightskew: float
                Skews the height of interaction
                from the construct.
            headheight: float
                Height of interaction head.
            headwidth: float
                Width of interaction head.
            zorder: int
                Matplotlib zorder value of
                the interaction.
            direction: string
                Determines what side of the construct
                the interaction is drawn on; 'forward'
                or 'reverse'.
            linewidth: float
                Determines the width of lines
                used to draw the interaction.
            sending_xy_skew: tuple
                Skews the point from which the
                interaction originates, format (x,y).
            receiving_xy_skew: tuple
                Skews the point at which the
                interaction ends, format (x,y).
    """
    final_parameters = {'color': (0,0,0),
                        'heightskew': 10.0,
                        'headheight': 7.0,
                        'headwidth': 7.0,
                        'zorder': 0,
                        'direction': 'forward',
                        'linewidth': 1.0,
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
