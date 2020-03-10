#!/usr/bin/env python
"""
Example of how parametric SVG can be rendered in Python using matplotlib as 
a canvas. This is precisely the same approach and code used by DNAplotlib 
to parse, parameterise and render the SVG files for genetic designs.
"""

import svgpath2mpl as svg2mpl
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
    """ Class to load and render the parametric SVG glyphs.
    """

    def __init__(self, glyph_path='glyphs/', global_defaults=None):
        self.glyphs_library, self.glyph_soterm_map = self.load_glyphs_from_path(glyph_path)
    
    def extract_tag_details(self, tag_attributes):
        tag_details = {}
        tag_details['glyphtype'] = None
        tag_details['soterms'] = []
        tag_details['type'] = None
        tag_details['defaults'] = None
        tag_details['d'] = None
        # Pull out the relevant details
        for key in tag_attributes.keys():
            if key == 'glyphtype':
                tag_details['glyphtype'] = tag_attributes[key]
            if key == 'soterms':
                tag_details['soterms'] = tag_attributes[key].split(';')
            if key == 'class':
                tag_details['type'] = tag_attributes[key]
            if 'parametric' in key and key.endswith('}d'):
                tag_details['d'] = tag_attributes[key]
            if 'parametric' in key and key.endswith('}defaults'):
                split_defaults_text = tag_attributes[key].split(';')
                defaults = {}
                for element in split_defaults_text:
                    key_value = element.split('=')
                    defaults[key_value[0].strip()] = float(key_value[1].strip())
                tag_details['defaults'] = defaults
        return tag_details

    def eval_svg_data(self, svg_text, parameters):
        # Use regular expression to extract and then replace with evaluated version
        # https://stackoverflow.com/questions/38734335/python-regex-replace-bracketed-text-with-contents-of-brackets
        return re.sub(r"{([^{}]+)}", lambda m: str(eval(m.group()[1:-1], parameters)), svg_text)

    def load_glyph(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        root_attributes = self.extract_tag_details(root.attrib)
        glyph_type = root_attributes['glyphtype']
        glyph_soterms = root_attributes['soterms']
        glyph_data = {}
        glyph_data['paths'] = []
        glyph_data['defaults'] = root_attributes['defaults']
        for child in root:
            # Cycle through and find all paths
            if child.tag.endswith('path'):
                glyph_data['paths'].append(self.extract_tag_details(child.attrib))
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

    def draw_glyph(self, ax, glyph_type, position, user_parameters=None):
        glyph = self.glyphs_library[glyph_type]
        merged_parameters = glyph['defaults'].copy()
        if user_parameters is not None:
            # Collate parameters (user parameters take priority) 
            for key in user_parameters.keys():
                merged_parameters[key] = user_parameters[key]
        paths_to_draw = []
        for path in glyph['paths']:
            if path['type'] not in ['baseline', 'bounding-box']:
                svg_text = self.eval_svg_data(path['d'], merged_parameters)
                paths_to_draw.append(svg2mpl.parse_path(svg_text))
        # Draw glyph to the axis
        # TODO - PARAMETERS
        for path in paths_to_draw:
            patch = patches.PathPatch(path, facecolor='white', edgecolor='black', lw=8)
            ax.add_patch(patch)

###############################################################################
# Testing
###############################################################################

renderer = GlyphRenderer(glyph_path='../glyphs/')
print(renderer.glyphs_library)
print('------------')
print(renderer.glyph_soterm_map)

user_parameters = {}
fig = plt.figure(figsize=(6,6))
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], frameon=False, aspect=1)

user_parameters['arrowbody_width'] = 50
renderer.draw_glyph(ax, 'CDS', (0.5, 0.5), user_parameters)

user_parameters['arrowbody_width'] = 20
user_parameters['baseline_offset'] = -20
renderer.draw_glyph(ax, 'CDS', (0.5, 30), user_parameters)

ax.set_ylim([0,100])
ax.set_xlim([0,100])
plt.show()
