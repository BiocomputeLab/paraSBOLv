#!/usr/bin/env python

################################################################################
# Author: Thomas Gorochowski, Biocompute Lab <tom@chofski.co.uk>
# Last Updated: 10/03/2020
################################################################################
# All drawing is done in SVG frame of reference so (0, 0) is top left increasing 
# downwards and to right). This will make it SVG compliant, but some 
# manipulation in Python is required for other tools like DNAplotlib to use
# these where bottom left is (0, 0).
################################################################################

import re
import math

# Default width for SVG file
svg_width = 100
svg_height = 100

# Default baseline start position
baseline_x = 0
baseline_y = 0

# Standard styling used for major component types
style_text = {}
style_text['bounding-box'] = 'fill:none;stroke:rgb(150,150,150);stroke-opacity:0.5;stroke-width:1pt;stroke-linecap:butt;stroke-linejoin:miter;stroke-dasharray:1.5,0.8'
style_text['baseline'] = 'fill:none;stroke:black;stroke-width:1pt'
style_text['unfilled-path'] = 'fill:none;stroke:black;stroke-width:1pt;stroke-linejoin:round;stroke-linecap:round'
style_text['filled-path'] = 'fill:rgb(230,230,230);fill-rule:nonzero;stroke:black;stroke-width:1pt;stroke-linejoin:miter;stroke-linecap:butt'
style_text['filled-background-path'] = 'fill:rgb(255,255,255);fill-rule:nonzero;stroke:none'

def params_to_text (parametric_defaults):
	param_text = []
	for k in sorted(parametric_defaults.keys()):
		param_text.append(k + '=' + str(parametric_defaults[k]))
	return ';'.join(param_text)

def eval_parameterised_path(parameterised_path_text, params):
	# Use regular expression to extract and then replace with evaluated version
	# https://stackoverflow.com/questions/38734335/python-regex-replace-bracketed-text-with-contents-of-brackets
	path_text = re.sub(r"{([^{}]+)}", lambda m: str(eval(m.group()[1:-1], params)), parameterised_path_text)
	return path_text

def svg_header (glyphtype, soterms, parametric_defaults={}, width=100, height=100):
	parametric_defaults_text = params_to_text(parametric_defaults)
	output = ''
	output += '<svg  version="1.1"\n'
	output += '      xmlns="http://www.w3.org/2000/svg"\n'
	output += '      xmlns:parametric="//parametric-svg.js.org/v1"\n'
	output += '      width="' + str(width) + '"\n'
	output += '      height="' + str(height) + '"\n'
	output += '      glyphtype="' + glyphtype + '"\n'
	output += '      soterms="' + soterms + '"\n'
	output += '      parametric:defaults="' + parametric_defaults_text + '">\n'
	return output

def bounding_box (x, y, width, height, params, style=style_text['bounding-box']):
	if INCLUDE_BOUNDING_BOX:
		output = ''
		output += '\n<rect class="bounding-box"\n'
		output += '      id="bounding-box"\n'
		output += '      parametric:x="' + x + '"\n'
		output += '      x="' + eval_parameterised_path(x, params) + '"\n'
		output += '      parametric:y="' + y + '"\n'
		output += '      y="' + eval_parameterised_path(y, params) + '"\n'
		output += '      parametric:width="' + width + '"\n'
		output += '      width="' + eval_parameterised_path(width, params) + '"\n'
		output += '      parametric:height="' + height + '"\n'
		output += '      height="' + eval_parameterised_path(height, params) + '"\n'
		output += '      style="' + style + '"/>\n\n'
		return output
	else:
		return ''

def baseline (x, y, width, params, style=style_text['baseline']):
	if INCLUDE_BASELINE:
		svg_str = 'M{x},{y+(height/2)} L{x+width},{y+(height/2)}'
		output = ''
		output += '<path class="baseline"\n'
		output += '      id="baseline"\n'
		output += '      parametric:d="' + svg_str + '"\n'
		output += '      d="' + eval_parameterised_path(svg_str, params) + '"\n'
		output += '      parametric:y="' + '{y+(height/2)}' + '"\n'
		output += '      style="' + style + '"/>\n'
		return output
	else:
		return ''

def write_glyph_svg (filename, header_text, glyph_paths):
	f_out = open(filename, 'w')
	f_out.write(header_text + '\n')
	for i in range(len(glyph_paths)):
		cur_path = glyph_paths[i]
		f_out.write('<path ')
		x = 0
		for k in cur_path.keys():
			el = cur_path[k]
			if x > 0:
				f_out.write("\n      ")
			x += 1
			f_out.write(k + '="' + cur_path[k] + '" ')
		f_out.write('/>\n\n')
	f_out.write('</svg>')
	f_out.close()

###############################################################################
# Functions to create list of elements for each glyph
###############################################################################

def rbs_svg ():
	params = {}
	# General parameters
	params['x'] = 0
	params['y'] = 0
	params['width'] = 26
	params['height'] = 60
	params['pad_left'] = 0
	params['pad_right'] = 0
	params['pad_top'] = 0
	params['pad_bottom'] = 0
	# RBS specific parameters
	params['glyph_pad_top'] = 12
	#params['glyph_pad_bottom'] = 30
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('RibosomeEntrySite', 'SO:0000139', parametric_defaults=params, width=params['width'], height=params['height'])
	header_text += bounding_box('{x}', '{y}', '{width}', '{height}', params, style=style_text['bounding-box'])
	header_text += baseline('{x}', '{y}', '{width}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	rbs_path = {}
	rbs_path['class'] = 'filled-path'
	rbs_path['id'] = 'rbs'
	rbs_path['parametric:d'] = 'M{(x+pad_left)},{y+(height/2)} C{(x+pad_left)},{(y+pad_top)+glyph_pad_top} {x+width-pad_right},{(y+pad_top)+glyph_pad_top} {x+width-pad_right},{y+(height/2)} Z'
	#L{baseline_x+pad_before},{(baseline_y-baseline_offset)}
	rbs_path['d'] = eval_parameterised_path(rbs_path['parametric:d'], params)
	rbs_path['style'] = style_text['filled-path']
	glyph_paths.append(rbs_path)
	return header_text, glyph_paths

def promoter_svg ():
	params = {}
	# General parameters
	params['x'] = 0
	params['y'] = 0
	params['width'] = 25
	params['height'] = 60
	params['pad_left'] = 0
	params['pad_right'] = 0
	params['pad_top'] = 0
	# Promoter specific parameters
	params['glyph_pad_top'] = 0
	params['glyph_arrowhead_height'] = 5
	params['glyph_arrowhead_width'] = 5
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('Promoter', 'SO:0000167', parametric_defaults=params, width=params['width'], height=params['height'])
	header_text += bounding_box('{x}', '{y}', '{width}', '{height}', params, style=style_text['bounding-box'])
	header_text += baseline('{x}', '{y}', '{width}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	promoter_body_path = {}
	promoter_body_path['class'] = 'unfilled-path'
	promoter_body_path['id'] = 'promoter-body'
	promoter_body_path['parametric:d'] = 'M{x+pad_left},{y+(height/2)} L{x+pad_left},{y+pad_top+glyph_pad_top+glyph_arrowhead_height} L{x+width-pad_right},{y+pad_top+glyph_pad_top+glyph_arrowhead_height}'
	promoter_body_path['d'] = eval_parameterised_path(promoter_body_path['parametric:d'], params)
	promoter_body_path['style'] = style_text['unfilled-path']
	glyph_paths.append(promoter_body_path)
	promoter_head_path = {}
	promoter_head_path['class'] = 'unfilled-path'
	promoter_head_path['id'] = 'promoter-head'
	promoter_head_path['parametric:d'] = 'M{x+width-pad_right-glyph_arrowhead_width},{y+pad_top+glyph_pad_top} L{x+width-pad_right},{y+pad_top+glyph_pad_top+glyph_arrowhead_height} L{x+width-pad_right-glyph_arrowhead_width},{y+pad_top+glyph_pad_top+(glyph_arrowhead_height*2)}'
	promoter_head_path['d'] = eval_parameterised_path(promoter_head_path['parametric:d'], params)
	promoter_head_path['style'] = style_text['unfilled-path']
	glyph_paths.append(promoter_head_path)
	return header_text, glyph_paths

def terminator_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['x'] = 0
	params['y'] = 0
	params['width'] = 16
	params['height'] = 60
	params['pad_left'] = 0
	params['pad_right'] = 0
	params['pad_top'] = 0
	# Promoter specific parameters
	params['glyph_pad_top'] = 12
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('Terminator', 'SO:0000141', parametric_defaults=params, width=params['width'], height=params['height'])
	header_text += bounding_box('{x}', '{y}', '{width}', '{height}', params, style=style_text['bounding-box'])
	header_text += baseline('{x}', '{y}', '{width}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	terminator_body_path = {}
	terminator_body_path['class'] = 'unfilled-path'
	terminator_body_path['id'] = 'terminator-body'
	terminator_body_path['parametric:d'] = 'M{x+pad_left+((width-x-pad_left-pad_right)/2)},{y+(height/2)} L{x+pad_left+((width-x-pad_left-pad_right)/2)},{y+pad_top+glyph_pad_top}'
	terminator_body_path['d'] = eval_parameterised_path(terminator_body_path['parametric:d'], params)
	terminator_body_path['style'] = style_text['unfilled-path']
	glyph_paths.append(terminator_body_path)
	terminator_head_path = {}
	terminator_head_path['class'] = 'unfilled-path'
	terminator_head_path['id'] = 'terminator-head'
	terminator_head_path['parametric:d'] = 'M{x+pad_left},{y+(pad_top+glyph_pad_top)} L{x+width-pad_right},{y+pad_top+glyph_pad_top}'
	terminator_head_path['d'] = eval_parameterised_path(terminator_head_path['parametric:d'], params)
	terminator_head_path['style'] = style_text['unfilled-path']
	glyph_paths.append(terminator_head_path)
	return header_text, glyph_paths

def cds_svg ():
	params = {}
	# General parameters
	params['x'] = 0
	params['y'] = 0
	params['width'] = 60
	params['height'] = 60
	params['pad_left'] = 0
	params['pad_right'] = 0
	params['pad_top'] = 0
	params['pad_bottom'] = 0
	# CDS specific parameters
	params['glyph_pad_top'] = 16
	params['glyph_pad_bottom'] = 16
	params['glyph_arrowhead_length'] = 15
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('CDS', 'SO:0000316', parametric_defaults=params, width=params['width'], height=params['height'])
	header_text += bounding_box('{x}', '{y}', '{width}', '{height}', params, style=style_text['bounding-box'])
	header_text += baseline('{x}', '{y}', '{width}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	cds_path = {}
	cds_path['class'] = 'filled-path'
	cds_path['id'] = 'cds'
	cds_path['parametric:d'] = 'M{(x+pad_left)},{(y+pad_top)+glyph_pad_top} L{(x+width-pad_right)-glyph_arrowhead_length},{(y+pad_top)+glyph_pad_top} L{(x+width-pad_right)},{(y+pad_top)+((height-pad_top-pad_bottom)/2)} L{(x+width-pad_right)-glyph_arrowhead_length},{(y+height-pad_bottom)-glyph_pad_bottom} L{(x+pad_left)},{(y+height-pad_bottom)-glyph_pad_bottom} Z'
	cds_path['d'] = eval_parameterised_path(cds_path['parametric:d'], params)
	cds_path['style'] = style_text['filled-path']
	glyph_paths.append(cds_path)
	return header_text, glyph_paths

def primer_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 3
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Primer specific parameters
	params['arrowbody_width'] = 10
	params['arrowhead_width'] = 3
	params['arrowhead_height'] = 3
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('PrimerBindingSite', 'SO:0005850', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-arrowhead_height-pad_top}', '{pad_before+arrowbody_width+pad_after}', '{pad_top+arrowhead_height+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+arrowbody_width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	primer_path = {}
	primer_path['class'] = 'unfilled-path'
	primer_path['id'] = 'primer-binding-site'
	primer_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)} L{baseline_x+pad_before+arrowbody_width},{(baseline_y-baseline_offset)} L{baseline_x+pad_before+arrowbody_width-arrowhead_width},{(baseline_y-baseline_offset)-arrowhead_height}'
	primer_path['d'] = eval_parameterised_path(primer_path['parametric:d'], params)
	primer_path['style'] = style_text['unfilled-path']
	glyph_paths.append(primer_path)
	return header_text, glyph_paths

def origin_of_replication_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Promoter specific parameters
	params['width'] = 20
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('OriginOfReplication', 'SO:0000296', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(width/2.0)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+width+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	ori_path = {}
	ori_path['class'] = 'filled-path'
	ori_path['id'] = 'origin-of-replication'
	ori_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)} C{baseline_x+pad_before},{(baseline_y-baseline_offset)-(width/1.5)} {baseline_x+pad_before+width},{(baseline_y-baseline_offset)-(width/1.5)} {baseline_x+pad_before+width},{(baseline_y-baseline_offset)} C{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(width/1.5)} {baseline_x+pad_before},{(baseline_y-baseline_offset)+(width/1.5)} {baseline_x+pad_before},{(baseline_y-baseline_offset)} Z'
	ori_path['d'] = eval_parameterised_path(ori_path['parametric:d'], params)
	ori_path['style'] = style_text['filled-path']
	glyph_paths.append(ori_path)
	return header_text, glyph_paths

def unspecified_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 15
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('Unspecified', 'SO:0000110', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(width/2.0)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+width+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	unspecified_path = {}
	unspecified_path['class'] = 'filled-path'
	unspecified_path['id'] = 'unspecified-boundry'
	unspecified_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)} L{baseline_x+pad_before+(width/2.0)},{(baseline_y-baseline_offset)-(width/2.0)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)} L{baseline_x+pad_before+(width/2.0)},{(baseline_y-baseline_offset)+(width/2.0)} Z'
	unspecified_path['d'] = eval_parameterised_path(unspecified_path['parametric:d'], params)
	unspecified_path['style'] = style_text['filled-path']
	glyph_paths.append(unspecified_path)
	question_path = {}
	question_path['class'] = 'unfilled-path'
	question_path['id'] = 'unspecified-question-mark'
	question_path['parametric:d'] = 'M{baseline_x+pad_before+(width*0.35)},{(baseline_y-baseline_offset)-(width*0.06)} C{baseline_x+pad_before+(width*0.35)},{(baseline_y-baseline_offset)-(width*0.23)} {baseline_x+pad_before+width-(width*0.25)},{(baseline_y-baseline_offset)-(width*0.23)} {baseline_x+pad_before+width-(width*0.35)},{(baseline_y-baseline_offset)+(width*0.01)} C{baseline_x+pad_before+width-(width*0.35)},{(baseline_y-baseline_offset)+(width*0.05)} {baseline_x+pad_before+(width*0.5)},{(baseline_y-baseline_offset)+(width*0.01)} {baseline_x+pad_before+(width*0.5)},{(baseline_y-baseline_offset)+(width*0.15)}'
	question_path['d'] = eval_parameterised_path(question_path['parametric:d'], params)
	question_path['style'] = style_text['unfilled-path']
	glyph_paths.append(question_path)
	point_path = {}
	point_path['class'] = 'unfilled-path'
	point_path['id'] = 'unspecified-question-mark-point'
	point_path['parametric:d'] = 'M{baseline_x+pad_before+(width*0.5)},{(baseline_y-baseline_offset)+(width*0.27)} L{baseline_x+pad_before+(width*0.5)},{(baseline_y-baseline_offset)+(width*0.27)}'
	point_path['d'] = eval_parameterised_path(point_path['parametric:d'], params)
	point_path['style'] = style_text['unfilled-path']
	glyph_paths.append(point_path)
	return header_text, glyph_paths

def omitted_detail_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 15
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('Omitted Detail', '', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	bg_path = {}
	bg_path['class'] = 'filled-background-path'
	bg_path['id'] = 'omitted-detail-background'
	bg_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(pad_top*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-(pad_top*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(pad_top*0.5)} L{baseline_x+pad_before},{(baseline_y-baseline_offset)+(pad_bottom*0.5)} Z}'
	bg_path['d'] = eval_parameterised_path(bg_path['parametric:d'], params)
	bg_path['style'] = style_text['filled-background-path']
	glyph_paths.append(bg_path)
	point1_path = {}
	point1_path['class'] = 'unfilled-path'
	point1_path['id'] = 'omitted-detail-point1'
	point1_path['parametric:d'] = 'M{baseline_x+pad_before+(width*0.5)},{(baseline_y-baseline_offset)} L{baseline_x+pad_before+(width*0.5)},{(baseline_y-baseline_offset)}'
	point1_path['d'] = eval_parameterised_path(point1_path['parametric:d'], params)
	point1_path['style'] = style_text['unfilled-path']
	glyph_paths.append(point1_path)
	point2_path = {}
	point2_path['class'] = 'unfilled-path'
	point2_path['id'] = 'omitted-detail-point1'
	point2_path['parametric:d'] = 'M{baseline_x+pad_before+(width*0.25)},{(baseline_y-baseline_offset)} L{baseline_x+pad_before+(width*0.25)},{(baseline_y-baseline_offset)}'
	point2_path['d'] = eval_parameterised_path(point2_path['parametric:d'], params)
	point2_path['style'] = style_text['unfilled-path']
	glyph_paths.append(point2_path)
	point3_path = {}
	point3_path['class'] = 'unfilled-path'
	point3_path['id'] = 'omitted-detail-point1'
	point3_path['parametric:d'] = 'M{baseline_x+pad_before+(width*0.75)},{(baseline_y-baseline_offset)} L{baseline_x+pad_before+(width*0.75)},{(baseline_y-baseline_offset)}'
	point3_path['d'] = eval_parameterised_path(point3_path['parametric:d'], params)
	point3_path['style'] = style_text['unfilled-path']
	glyph_paths.append(point3_path)
	return header_text, glyph_paths

def recombination_site_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 10
	params['height'] = 15
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('Recombination Site', '', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(height*0.5)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+height+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	recombination_site_path = {}
	recombination_site_path['class'] = 'filled-path'
	recombination_site_path['id'] = 'recombination-site'
	recombination_site_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)} {baseline_x+pad_before},{(baseline_y-baseline_offset)+(height*0.5)} Z'
	recombination_site_path['d'] = eval_parameterised_path(recombination_site_path['parametric:d'], params)
	recombination_site_path['style'] = style_text['filled-path']
	glyph_paths.append(recombination_site_path)
	return header_text, glyph_paths

def no_glyph_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 8
	params['height'] = 15
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('No Glyph', '', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(height*0.5)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+height+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	bg_path = {}
	bg_path['class'] = 'filled-background-path'
	bg_path['id'] = 'operator-background'
	bg_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-pad_top-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before},{(baseline_y-baseline_offset)+(height*0.5)} Z}'
	bg_path['d'] = eval_parameterised_path(bg_path['parametric:d'], params)
	bg_path['style'] = style_text['filled-background-path']
	glyph_paths.append(bg_path)
	no_glyph_path1 = {}
	no_glyph_path1['class'] = 'unfilled-path'
	no_glyph_path1['id'] = 'no-glyph-path1'
	no_glyph_path1['parametric:d'] = 'M{baseline_x+pad_before+(width*0.3)},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before+(width*0.3)},{(baseline_y-baseline_offset)+(height*0.5)}'
	no_glyph_path1['d'] = eval_parameterised_path(no_glyph_path1['parametric:d'], params)
	no_glyph_path1['style'] = style_text['unfilled-path']
	glyph_paths.append(no_glyph_path1)
	no_glyph_path2 = {}
	no_glyph_path2['class'] = 'unfilled-path'
	no_glyph_path2['id'] = 'no-glyph-path1'
	no_glyph_path2['parametric:d'] = 'M{baseline_x+pad_before+(width*0.7)},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before+(width*0.7)},{(baseline_y-baseline_offset)+(height*0.5)}'
	no_glyph_path2['d'] = eval_parameterised_path(no_glyph_path2['parametric:d'], params)
	no_glyph_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(no_glyph_path2)
	return header_text, glyph_paths

def operator_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 7
	params['height'] = 7
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('Operator', 'SO:0000057,SO:0000409', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(height*0.5)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+height+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	bg_path = {}
	bg_path['class'] = 'filled-background-path'
	bg_path['id'] = 'operator-background'
	bg_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-pad_top-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before},{(baseline_y-baseline_offset)+(height*0.5)} Z}'
	bg_path['d'] = eval_parameterised_path(bg_path['parametric:d'], params)
	bg_path['style'] = style_text['filled-background-path']
	glyph_paths.append(bg_path)
	operator_path = {}
	operator_path['class'] = 'unfilled-path'
	operator_path['id'] = 'operator-path'
	operator_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-(height*0.5)}'
	operator_path['d'] = eval_parameterised_path(operator_path['parametric:d'], params)
	operator_path['style'] = style_text['unfilled-path']
	glyph_paths.append(operator_path)
	return header_text, glyph_paths

def assembly_scar_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 15
	params['height'] = 5
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('Assembly Scar', 'SO:0001953', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(height*0.5)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+height+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	bg_path = {}
	bg_path['class'] = 'filled-background-path'
	bg_path['id'] = 'assembly-scar-background'
	bg_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-pad_top-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before},{(baseline_y-baseline_offset)+(height*0.5)} Z}'
	bg_path['d'] = eval_parameterised_path(bg_path['parametric:d'], params)
	bg_path['style'] = style_text['filled-background-path']
	glyph_paths.append(bg_path)
	assembly_scar_path1 = {}
	assembly_scar_path1['class'] = 'unfilled-path'
	assembly_scar_path1['id'] = 'assembly-scar-path1'
	assembly_scar_path1['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-(height*0.5)}'
	assembly_scar_path1['d'] = eval_parameterised_path(assembly_scar_path1['parametric:d'], params)
	assembly_scar_path1['style'] = style_text['unfilled-path']
	glyph_paths.append(assembly_scar_path1)
	assembly_scar_path2 = {}
	assembly_scar_path2['class'] = 'unfilled-path'
	assembly_scar_path2['id'] = 'assembly-scar-path1'
	assembly_scar_path2['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(height*0.5)}'
	assembly_scar_path2['d'] = eval_parameterised_path(assembly_scar_path2['parametric:d'], params)
	assembly_scar_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(assembly_scar_path2)
	return header_text, glyph_paths

def blunt_restriction_site_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 8
	params['height'] = 15
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('Blunt Restriction Site', 'SO:0001691', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(height*0.5)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+height+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	bg_path = {}
	bg_path['class'] = 'filled-background-path'
	bg_path['id'] = 'blunt-restriction-site-background'
	bg_path['parametric:d'] = 'M{baseline_x+pad_before+(width*0.3)},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+(width*0.7)},{(baseline_y-baseline_offset)-pad_top-(height*0.5)} L{baseline_x+pad_before+(width*0.7)},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before+(width*0.3)},{(baseline_y-baseline_offset)+(height*0.5)} Z}'
	bg_path['d'] = eval_parameterised_path(bg_path['parametric:d'], params)
	bg_path['style'] = style_text['filled-background-path']
	glyph_paths.append(bg_path)
	blunt_restriction_site_path1 = {}
	blunt_restriction_site_path1['class'] = 'unfilled-path'
	blunt_restriction_site_path1['id'] = 'blunt-restriction-site-path1'
	blunt_restriction_site_path1['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+(width*0.3)},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+(width*0.3)},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before},{(baseline_y-baseline_offset)+(height*0.5)}'
	blunt_restriction_site_path1['d'] = eval_parameterised_path(blunt_restriction_site_path1['parametric:d'], params)
	blunt_restriction_site_path1['style'] = style_text['unfilled-path']
	glyph_paths.append(blunt_restriction_site_path1)
	blunt_restriction_site_path2 = {}
	blunt_restriction_site_path2['class'] = 'unfilled-path'
	blunt_restriction_site_path2['id'] = 'blunt-restriction-site-path1'
	blunt_restriction_site_path2['parametric:d'] = 'M{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+(width*0.7)},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+(width*0.7)},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(height*0.5)}'
	blunt_restriction_site_path2['d'] = eval_parameterised_path(blunt_restriction_site_path2['parametric:d'], params)
	blunt_restriction_site_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(blunt_restriction_site_path2)
	return header_text, glyph_paths

def engineered_region_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 30
	params['height'] = 15
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('Engineered Region', 'SO:0000804', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(height*0.5)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+height+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	engineered_region_path = {}
	engineered_region_path['class'] = 'filled-path'
	engineered_region_path['id'] = 'engineered-region-path'
	engineered_region_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(height*0.5)} {baseline_x+pad_before},{(baseline_y-baseline_offset)+(height*0.5)} Z'
	engineered_region_path['d'] = eval_parameterised_path(engineered_region_path['parametric:d'], params)
	engineered_region_path['style'] = style_text['filled-path']
	glyph_paths.append(engineered_region_path)
	return header_text, glyph_paths

def insulator_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 15
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('Insulator', 'SO:0000627', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(width*0.5)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+width+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	bg_path = {}
	bg_path['class'] = 'filled-background-path'
	bg_path['id'] = 'insulator-background'
	bg_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(width*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-(width*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(width*0.5)} L{baseline_x+pad_before},{(baseline_y-baseline_offset)+(width*0.5)} Z}'
	bg_path['d'] = eval_parameterised_path(bg_path['parametric:d'], params)
	bg_path['style'] = style_text['filled-background-path']
	glyph_paths.append(bg_path)
	insulator_outer_path = {}
	insulator_outer_path['class'] = 'unfilled-path'
	insulator_outer_path['id'] = 'insulator-outer-path'
	insulator_outer_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(width*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-(width*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(width*0.5)} L{baseline_x+pad_before},{(baseline_y-baseline_offset)+(width*0.5)} Z'
	insulator_outer_path['d'] = eval_parameterised_path(insulator_outer_path['parametric:d'], params)
	insulator_outer_path['style'] = style_text['unfilled-path']
	glyph_paths.append(insulator_outer_path)
	insulator_inner_path = {}
	insulator_inner_path['class'] = 'filled-path'
	insulator_inner_path['id'] = 'insulator-inner-path'
	insulator_inner_path['parametric:d'] = 'M{baseline_x+pad_before+(width*0.2)},{(baseline_y-baseline_offset)-(width*0.3)} L{baseline_x+pad_before+width-(width*0.2)},{(baseline_y-baseline_offset)-(width*0.3)} L{baseline_x+pad_before+width-(width*0.2)},{(baseline_y-baseline_offset)+(width*0.3)} L{baseline_x+pad_before+(width*0.2)},{(baseline_y-baseline_offset)+(width*0.3)} Z'
	insulator_inner_path['d'] = eval_parameterised_path(insulator_inner_path['parametric:d'], params)
	insulator_inner_path['style'] = style_text['filled-path']
	glyph_paths.append(insulator_inner_path)
	return header_text, glyph_paths

def origin_of_transfer_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Promoter specific parameters
	params['width'] = 20
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('OriginOfTransfer', 'SO:0000724', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(width/2.0)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+width+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	ort_path = {}
	ort_path['class'] = 'filled-path'
	ort_path['id'] = 'origin-of-transfer'
	ort_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)} C{baseline_x+pad_before},{(baseline_y-baseline_offset)-(width/1.5)} {baseline_x+pad_before+width},{(baseline_y-baseline_offset)-(width/1.5)} {baseline_x+pad_before+width},{(baseline_y-baseline_offset)} C{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(width/1.5)} {baseline_x+pad_before},{(baseline_y-baseline_offset)+(width/1.5)} {baseline_x+pad_before},{(baseline_y-baseline_offset)} Z'
	ort_path['d'] = eval_parameterised_path(ort_path['parametric:d'], params)
	ort_path['style'] = style_text['filled-path']
	glyph_paths.append(ort_path)
	ort_arrowbody_path = {}
	ort_arrowbody_path['class'] = 'unfilled-path'
	ort_arrowbody_path['id'] = 'origin-of-transfer-arrowbody'
	ort_arrowbody_path['parametric:d'] = 'M{baseline_x+pad_before+(width*0.5)},{(baseline_y-baseline_offset)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-(width*0.5)}'
	ort_arrowbody_path['d'] = eval_parameterised_path(ort_arrowbody_path['parametric:d'], params)
	ort_arrowbody_path['style'] = style_text['unfilled-path']
	glyph_paths.append(ort_arrowbody_path)
	ort_arrowhead_path = {}
	ort_arrowhead_path['class'] = 'unfilled-path'
	ort_arrowhead_path['id'] = 'origin-of-transfer-arrowhead'
	ort_arrowhead_path['parametric:d'] = 'M{baseline_x+pad_before+(width*0.85)},{(baseline_y-baseline_offset)-(width*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-(width*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-(width*0.35)}'
	ort_arrowhead_path['d'] = eval_parameterised_path(ort_arrowhead_path['parametric:d'], params)
	ort_arrowhead_path['style'] = style_text['unfilled-path']
	glyph_paths.append(ort_arrowhead_path)
	return header_text, glyph_paths

def sticky_restriction_site_5_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 15
	params['height'] = 8
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('5\' Sticky Restriction Site', 'SO:0001975', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(height*0.5)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+height+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	bg_path = {}
	bg_path['class'] = 'filled-background-path'
	bg_path['id'] = 'sticky-restriction-site-background'
	bg_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-pad_top-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before},{(baseline_y-baseline_offset)+(height*0.5)} Z}'
	bg_path['d'] = eval_parameterised_path(bg_path['parametric:d'], params)
	bg_path['style'] = style_text['filled-background-path']
	glyph_paths.append(bg_path)
	sticky_restriction_site_path = {}
	sticky_restriction_site_path['class'] = 'unfilled-path'
	sticky_restriction_site_path['id'] = 'sticky-restriction-site-path'
	sticky_restriction_site_path['parametric:d'] = 'M{baseline_x+pad_before+(width*0.15)},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+(width*0.15)},{(baseline_y-baseline_offset)} L{baseline_x+pad_before+(width*0.85)},{(baseline_y-baseline_offset)} L{baseline_x+pad_before+(width*0.85)},{(baseline_y-baseline_offset)+(height*0.5)}'
	sticky_restriction_site_path['d'] = eval_parameterised_path(sticky_restriction_site_path['parametric:d'], params)
	sticky_restriction_site_path['style'] = style_text['unfilled-path']
	glyph_paths.append(sticky_restriction_site_path)
	return header_text, glyph_paths

def sticky_restriction_site_3_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 15
	params['height'] = 8
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('3\' Sticky Restriction Site', 'SO:0001976', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(height*0.5)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+height+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	bg_path = {}
	bg_path['class'] = 'filled-background-path'
	bg_path['id'] = 'sticky-restriction-site-background'
	bg_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-pad_top-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before},{(baseline_y-baseline_offset)+(height*0.5)} Z}'
	bg_path['d'] = eval_parameterised_path(bg_path['parametric:d'], params)
	bg_path['style'] = style_text['filled-background-path']
	glyph_paths.append(bg_path)
	sticky_restriction_site_path = {}
	sticky_restriction_site_path['class'] = 'unfilled-path'
	sticky_restriction_site_path['id'] = 'sticky-restriction-site-path'
	sticky_restriction_site_path['parametric:d'] = 'M{baseline_x+pad_before+(width*0.15)},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before+(width*0.15)},{(baseline_y-baseline_offset)} L{baseline_x+pad_before+(width*0.85)},{(baseline_y-baseline_offset)} L{baseline_x+pad_before+(width*0.85)},{(baseline_y-baseline_offset)-(height*0.5)}'
	sticky_restriction_site_path['d'] = eval_parameterised_path(sticky_restriction_site_path['parametric:d'], params)
	sticky_restriction_site_path['style'] = style_text['unfilled-path']
	glyph_paths.append(sticky_restriction_site_path)
	return header_text, glyph_paths

def overhang_site_5_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 15
	params['height'] = 5
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('5\' Overhang Site', 'SO:0001932', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(height*0.5)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+height+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	bg_path = {}
	bg_path['class'] = 'filled-background-path'
	bg_path['id'] = 'overhang_site-background'
	bg_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-pad_top-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before},{(baseline_y-baseline_offset)+(height*0.5)} Z}'
	bg_path['d'] = eval_parameterised_path(bg_path['parametric:d'], params)
	bg_path['style'] = style_text['filled-background-path']
	glyph_paths.append(bg_path)
	overhang_scar_path1 = {}
	overhang_scar_path1['class'] = 'unfilled-path'
	overhang_scar_path1['id'] = 'overhang_site-path1'
	overhang_scar_path1['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-(height*0.5)}'
	overhang_scar_path1['d'] = eval_parameterised_path(overhang_scar_path1['parametric:d'], params)
	overhang_scar_path1['style'] = style_text['unfilled-path']
	glyph_paths.append(overhang_scar_path1)
	overhang_scar_path2 = {}
	overhang_scar_path2['class'] = 'unfilled-path'
	overhang_scar_path2['id'] = 'overhang_site-path1'
	overhang_scar_path2['parametric:d'] = 'M{baseline_x+pad_before+(width*0.4)},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(height*0.5)}'
	overhang_scar_path2['d'] = eval_parameterised_path(overhang_scar_path2['parametric:d'], params)
	overhang_scar_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(overhang_scar_path2)
	return header_text, glyph_paths

def overhang_site_3_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 15
	params['height'] = 5
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('3\' Overhang Site', 'SO:0001933', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(height*0.5)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+height+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	bg_path = {}
	bg_path['class'] = 'filled-background-path'
	bg_path['id'] = 'overhang_site-background'
	bg_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-pad_top-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before},{(baseline_y-baseline_offset)+(height*0.5)} Z}'
	bg_path['d'] = eval_parameterised_path(bg_path['parametric:d'], params)
	bg_path['style'] = style_text['filled-background-path']
	glyph_paths.append(bg_path)
	overhang_scar_path1 = {}
	overhang_scar_path1['class'] = 'unfilled-path'
	overhang_scar_path1['id'] = 'overhang_site-path1'
	overhang_scar_path1['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(height*0.5)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-(height*0.5)}'
	overhang_scar_path1['d'] = eval_parameterised_path(overhang_scar_path1['parametric:d'], params)
	overhang_scar_path1['style'] = style_text['unfilled-path']
	glyph_paths.append(overhang_scar_path1)
	overhang_scar_path2 = {}
	overhang_scar_path2['class'] = 'unfilled-path'
	overhang_scar_path2['id'] = 'overhang_site-path1'
	overhang_scar_path2['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)+(height*0.5)} L{baseline_x+pad_before+width-(width*0.4)},{(baseline_y-baseline_offset)+(height*0.5)}'
	overhang_scar_path2['d'] = eval_parameterised_path(overhang_scar_path2['parametric:d'], params)
	overhang_scar_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(overhang_scar_path2)
	return header_text, glyph_paths

def signature_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 20
	params['height'] = 10
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('Signature', 'SO:0001978', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-height-pad_top}', '{pad_before+width+pad_after}', '{pad_top+height+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	signature_path1 = {}
	signature_path1['class'] = 'filled-path'
	signature_path1['id'] = 'signature-box-path'
	signature_path1['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-height} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-height} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)} {baseline_x+pad_before},{(baseline_y-baseline_offset)} Z'
	signature_path1['d'] = eval_parameterised_path(signature_path1['parametric:d'], params)
	signature_path1['style'] = style_text['filled-path']
	glyph_paths.append(signature_path1)
	signature_path2 = {}
	signature_path2['class'] = 'unfilled-path'
	signature_path2['id'] = 'signature-cross-path1'
	signature_path2['parametric:d'] = 'M{baseline_x+pad_before+(height*0.3)},{(baseline_y-baseline_offset)-height+(height*0.3)} L{baseline_x+pad_before+(height*0.7)},{(baseline_y-baseline_offset)-height+(height*0.7)}'
	signature_path2['d'] = eval_parameterised_path(signature_path2['parametric:d'], params)
	signature_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(signature_path2)
	signature_path3 = {}
	signature_path3['class'] = 'unfilled-path'
	signature_path3['id'] = 'signature-cross-path2'
	signature_path3['parametric:d'] = 'M{baseline_x+pad_before+(height*0.3)},{(baseline_y-baseline_offset)-(height*0.3)} L{baseline_x+pad_before+(height*0.7)},{(baseline_y-baseline_offset)-(height*0.7)}'
	signature_path3['d'] = eval_parameterised_path(signature_path3['parametric:d'], params)
	signature_path3['style'] = style_text['unfilled-path']
	glyph_paths.append(signature_path3)
	signature_path4 = {}
	signature_path4['class'] = 'unfilled-path'
	signature_path4['id'] = 'signature-line-path'
	signature_path4['parametric:d'] = 'M{baseline_x+pad_before+height},{(baseline_y-baseline_offset)-(height*0.3)} L{baseline_x+pad_before+width-(height*0.3)},{(baseline_y-baseline_offset)-(height*0.3)}'
	signature_path4['d'] = eval_parameterised_path(signature_path4['parametric:d'], params)
	signature_path4['style'] = style_text['unfilled-path']
	glyph_paths.append(signature_path4)
	return header_text, glyph_paths

def poly_a_site_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 20
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('PolyA Site', 'SO:0000553', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(width*0.3)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+(width*0.3)+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	bg_path = {}
	bg_path['class'] = 'filled-background-path'
	bg_path['id'] = 'poly-a-site-background'
	bg_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(width*0.3)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)-pad_top-(width*0.3)} L{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(width*0.3)} L{baseline_x+pad_before},{(baseline_y-baseline_offset)+(width*0.3)} Z}'
	bg_path['d'] = eval_parameterised_path(bg_path['parametric:d'], params)
	bg_path['style'] = style_text['filled-background-path']
	glyph_paths.append(bg_path)
	polu_a_site_path1 = {}
	polu_a_site_path1['class'] = 'unfilled-path'
	polu_a_site_path1['id'] = 'poly-a-site-path1'
	polu_a_site_path1['parametric:d'] = 'M{(baseline_x+pad_before)},{(baseline_y-baseline_offset)} L{(baseline_x+pad_before)+(width*(1.0/6.0))},{(baseline_y-baseline_offset)-(width*0.3)} L{(baseline_x+pad_before)+(width*0.333333)},{(baseline_y-baseline_offset)} L{(baseline_x+pad_before)+(width*(3.0/6.0))},{(baseline_y-baseline_offset)-(width*0.3)} L{(baseline_x+pad_before)+(width*0.66666)},{(baseline_y-baseline_offset)} L{(baseline_x+pad_before)+(width*(5.0/6.0))},{(baseline_y-baseline_offset)-(width*0.3)} L{(baseline_x+pad_before)+(width*1.0)},{(baseline_y-baseline_offset)}'
	polu_a_site_path1['d'] = eval_parameterised_path(polu_a_site_path1['parametric:d'], params)
	polu_a_site_path1['style'] = style_text['unfilled-path']
	glyph_paths.append(polu_a_site_path1)
	polu_a_site_path2 = {}
	polu_a_site_path2['class'] = 'unfilled-path'
	polu_a_site_path2['id'] = 'poly-a-site-path2'
	polu_a_site_path2['parametric:d'] = 'M{(baseline_x+pad_before)+(width*(0.7/12.0))},{(baseline_y-baseline_offset)-(width*0.3*0.3)} L{(baseline_x+pad_before)+(width*(3.3/12.0))},{(baseline_y-baseline_offset)-(width*0.3*0.3)}'
	polu_a_site_path2['d'] = eval_parameterised_path(polu_a_site_path2['parametric:d'], params)
	polu_a_site_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(polu_a_site_path2)
	polu_a_site_path3 = {}
	polu_a_site_path3['class'] = 'unfilled-path'
	polu_a_site_path3['id'] = 'poly-a-site-path3'
	polu_a_site_path3['parametric:d'] = 'M{(baseline_x+pad_before)+(width*(4.7/12.0))},{(baseline_y-baseline_offset)-(width*0.3*0.3)} L{(baseline_x+pad_before)+(width*(7.3/12.0))},{(baseline_y-baseline_offset)-(width*0.3*0.3)}'
	polu_a_site_path3['d'] = eval_parameterised_path(polu_a_site_path3['parametric:d'], params)
	polu_a_site_path3['style'] = style_text['unfilled-path']
	glyph_paths.append(polu_a_site_path3)
	polu_a_site_path4 = {}
	polu_a_site_path4['class'] = 'unfilled-path'
	polu_a_site_path4['id'] = 'poly-a-site-path3'
	polu_a_site_path4['parametric:d'] = 'M{(baseline_x+pad_before)+(width*(8.7/12.0))},{(baseline_y-baseline_offset)-(width*0.3*0.3)} L{(baseline_x+pad_before)+(width*(11.3/12.0))},{(baseline_y-baseline_offset)-(width*0.3*0.3)}'
	polu_a_site_path4['d'] = eval_parameterised_path(polu_a_site_path4['parametric:d'], params)
	polu_a_site_path4['style'] = style_text['unfilled-path']
	glyph_paths.append(polu_a_site_path4)
	return header_text, glyph_paths

def dna_location_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['top_width'] = 6
	params['stem_height'] = 10
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('DNA Location', 'SO:0001236,SO:0000699', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-stem_height-top_width-pad_top}', '{pad_before+top_width+pad_after}', '{pad_top+stem_height+top_width+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+top_width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	location_top_path = {}
	location_top_path['class'] = 'filled-path'
	location_top_path['id'] = 'location-top-path'
	location_top_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-(stem_height+(top_width*0.5))} C{baseline_x+pad_before},{(baseline_y-baseline_offset)-(stem_height+(top_width*0.5))-(top_width/1.5)} {baseline_x+pad_before+top_width},{(baseline_y-baseline_offset)-(stem_height+(top_width*0.5))-(top_width/1.5)} {baseline_x+pad_before+top_width},{(baseline_y-baseline_offset)-(stem_height+(top_width*0.5))} C{baseline_x+pad_before+top_width},{(baseline_y-baseline_offset)-(stem_height+(top_width*0.5))+(top_width/1.5)} {baseline_x+pad_before},{(baseline_y-baseline_offset)-(stem_height+(top_width*0.5))+(top_width/1.5)} {baseline_x+pad_before},{(baseline_y-baseline_offset)-(stem_height+(top_width*0.5))} Z'
	location_top_path['d'] = eval_parameterised_path(location_top_path['parametric:d'], params)
	location_top_path['style'] = style_text['filled-path']
	glyph_paths.append(location_top_path)
	location_stem_path = {}
	location_stem_path['class'] = 'unfilled-path'
	location_stem_path['id'] = 'location-stem-path'
	location_stem_path['parametric:d'] = 'M{baseline_x+pad_before+(top_width*0.5)},{(baseline_y-baseline_offset)} L{baseline_x+pad_before+(top_width*0.5)},{(baseline_y-baseline_offset)-stem_height}'
	location_stem_path['d'] = eval_parameterised_path(location_stem_path['parametric:d'], params)
	location_stem_path['style'] = style_text['unfilled-path']
	glyph_paths.append(location_stem_path)
	return header_text, glyph_paths

def dna_cleavage_site_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['top_width'] = 6
	params['stem_height'] = 10
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('DNA Cleavage Site', 'SO:0001688,SO:0001687', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-stem_height-top_width-pad_top}', '{pad_before+top_width+pad_after}', '{pad_top+stem_height+top_width+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+top_width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	location_top_path1 = {}
	location_top_path1['class'] = 'unfilled-path'
	location_top_path1['id'] = 'location-top-path'
	location_top_path1['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-stem_height-top_width} L{baseline_x+pad_before+top_width},{(baseline_y-baseline_offset)-stem_height}'
	location_top_path1['d'] = eval_parameterised_path(location_top_path1['parametric:d'], params)
	location_top_path1['style'] = style_text['unfilled-path']
	glyph_paths.append(location_top_path1)
	location_top_path2 = {}
	location_top_path2['class'] = 'unfilled-path'
	location_top_path2['id'] = 'location-top-path'
	location_top_path2['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-stem_height} L{baseline_x+pad_before+top_width},{(baseline_y-baseline_offset)-stem_height-top_width}'
	location_top_path2['d'] = eval_parameterised_path(location_top_path2['parametric:d'], params)
	location_top_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(location_top_path2)
	location_stem_path = {}
	location_stem_path['class'] = 'unfilled-path'
	location_stem_path['id'] = 'location-stem-path'
	location_stem_path['parametric:d'] = 'M{baseline_x+pad_before+(top_width*0.5)},{(baseline_y-baseline_offset)} L{baseline_x+pad_before+(top_width*0.5)},{(baseline_y-baseline_offset)-stem_height-(top_width*0.5)}'
	location_stem_path['d'] = eval_parameterised_path(location_stem_path['parametric:d'], params)
	location_stem_path['style'] = style_text['unfilled-path']
	glyph_paths.append(location_stem_path)
	return header_text, glyph_paths

def dna_stability_element_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['top_width'] = 6
	params['stem_height'] = 10
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('DNA Cleavage Site', 'SO:0001688,SO:0001687', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-stem_height-top_width-pad_top}', '{pad_before+top_width+pad_after}', '{pad_top+stem_height+top_width+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+top_width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	location_top_path = {}
	location_top_path['class'] = 'filled-path'
	location_top_path['id'] = 'location-top-path'
	location_top_path['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)-stem_height-top_width} L{baseline_x+pad_before+top_width},{(baseline_y-baseline_offset)-stem_height-top_width} L{baseline_x+pad_before+top_width},{(baseline_y-baseline_offset)-stem_height-(top_width*0.3)} L{baseline_x+pad_before+(top_width*0.5)},{(baseline_y-baseline_offset)-stem_height} L{baseline_x+pad_before},{(baseline_y-baseline_offset)-stem_height-(top_width*0.3) } Z'
	location_top_path['d'] = eval_parameterised_path(location_top_path['parametric:d'], params)
	location_top_path['style'] = style_text['filled-path']
	glyph_paths.append(location_top_path)
	location_stem_path = {}
	location_stem_path['class'] = 'unfilled-path'
	location_stem_path['id'] = 'location-stem-path'
	location_stem_path['parametric:d'] = 'M{baseline_x+pad_before+(top_width*0.5)},{(baseline_y-baseline_offset)} L{baseline_x+pad_before+(top_width*0.5)},{(baseline_y-baseline_offset)-stem_height}'
	location_stem_path['d'] = eval_parameterised_path(location_stem_path['parametric:d'], params)
	location_stem_path['style'] = style_text['unfilled-path']
	glyph_paths.append(location_stem_path)
	return header_text, glyph_paths

def spacer_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 10
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('Spacer', 'SO:0000031', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(width*0.5)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+width+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	spacer_path1 = {}
	spacer_path1['class'] = 'filled-path'
	spacer_path1['id'] = 'spacer-circle-path'
	spacer_path1['parametric:d'] = 'M{baseline_x+pad_before},{(baseline_y-baseline_offset)} C{baseline_x+pad_before},{(baseline_y-baseline_offset)-(width/1.5)} {baseline_x+pad_before+width},{(baseline_y-baseline_offset)-(width/1.5)} {baseline_x+pad_before+width},{(baseline_y-baseline_offset)} C{baseline_x+pad_before+width},{(baseline_y-baseline_offset)+(width/1.5)} {baseline_x+pad_before},{(baseline_y-baseline_offset)+(width/1.5)} {baseline_x+pad_before},{(baseline_y-baseline_offset)} Z'
	spacer_path1['d'] = eval_parameterised_path(spacer_path1['parametric:d'], params)
	spacer_path1['style'] = style_text['filled-path']
	glyph_paths.append(spacer_path1)
	# Calculate the angles using basic trig
	angle = 40.0
	sin_angle = str(math.sin(angle))
	cos_angle = str(math.cos(angle))
	spacer_path2 = {}
	spacer_path2['class'] = 'unfilled-path'
	spacer_path2['id'] = 'spacer-cross1-path'
	spacer_path2['parametric:d'] = 'M{(baseline_x+pad_before)+((width*0.5)-((width*0.5)*' + cos_angle +'))},{(baseline_y-baseline_offset)-((width*0.5)*' + sin_angle +')} L{(baseline_x+pad_before)+(width*0.5)+((width*0.5)*' + cos_angle +')},{(baseline_y-baseline_offset)+((width*0.5)*' + sin_angle +')}'
	spacer_path2['d'] = eval_parameterised_path(spacer_path2['parametric:d'], params)
	spacer_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(spacer_path2)
	spacer_path3 = {}
	spacer_path3['class'] = 'unfilled-path'
	spacer_path3['id'] = 'spacer-cross2-path'
	spacer_path3['parametric:d'] = 'M{(baseline_x+pad_before)+((width*0.5)-((width*0.5)*' + cos_angle +'))},{(baseline_y-baseline_offset)+((width*0.5)*' + sin_angle +')} L{(baseline_x+pad_before)+(width*0.5)+((width*0.5)*' + cos_angle +')},{(baseline_y-baseline_offset)-((width*0.5)*' + sin_angle +')}'
	spacer_path3['d'] = eval_parameterised_path(spacer_path3['parametric:d'], params)
	spacer_path3['style'] = style_text['unfilled-path']
	glyph_paths.append(spacer_path3)
	return header_text, glyph_paths

def aptamer_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component  parameters
	params['width'] = 18
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('Aptamer', '', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-width-pad_top}', '{pad_before+width+pad_after}', '{pad_top+width+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	aptamer_path = {}
	aptamer_path['class'] = 'filled-path'
	aptamer_path['id'] = 'aptamer-path'
	aptamer_path['parametric:d'] = 'M{(baseline_x+pad_before)+(width*0.35)},{(baseline_y-baseline_offset)} L{(baseline_x+pad_before)+(width*0.35)},{(baseline_y-baseline_offset)-(width*0.3)} C{(baseline_x+pad_before)+(width*0.0)},{(baseline_y-baseline_offset)-(width*0.4)} {(baseline_x+pad_before)+(width*0.3)},{(baseline_y-baseline_offset)-(width*0.9)} {(baseline_x+pad_before)+(width*0.55)},{(baseline_y-baseline_offset)-(width*0.65)} L{(baseline_x+pad_before)+(width*0.75)},{(baseline_y-baseline_offset)-(width*0.8)} C{(baseline_x+pad_before)+(width*0.72)},{(baseline_y-baseline_offset)-(width*0.95)} {(baseline_x+pad_before)+(width*0.9)},{(baseline_y-baseline_offset)-(width*1.0)} {(baseline_x+pad_before)+(width*0.97)},{(baseline_y-baseline_offset)-(width*0.92)} C{(baseline_x+pad_before)+(width*1.05)},{(baseline_y-baseline_offset)-(width*0.72)} {(baseline_x+pad_before)+(width*0.9)},{(baseline_y-baseline_offset)-(width*0.7)} {(baseline_x+pad_before)+(width*0.82)},{(baseline_y-baseline_offset)-(width*0.68)} L{(baseline_x+pad_before)+(width*0.6)},{(baseline_y-baseline_offset)-(width*0.5)} C{(baseline_x+pad_before)+(width*0.63)},{(baseline_y-baseline_offset)-(width*0.37)} {(baseline_x+pad_before)+(width*0.5)},{(baseline_y-baseline_offset)-(width*0.35)} {(baseline_x+pad_before)+(width*0.5)},{(baseline_y-baseline_offset)-(width*0.3)} L{(baseline_x+pad_before)+(width*0.5)},{(baseline_y-baseline_offset)} Z'
	aptamer_path['d'] = eval_parameterised_path(aptamer_path['parametric:d'], params)
	aptamer_path['style'] = style_text['filled-path']
	glyph_paths.append(aptamer_path)
	return header_text, glyph_paths

def non_coding_rna_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component parameters
	params['height'] = 12
	params['width'] = 20
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('Non-coding RNA', '', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-height-pad_top}', '{pad_before+width+pad_after}', '{pad_top+height+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	non_coding_rna_path = {}
	non_coding_rna_path['class'] = 'filled-path'
	non_coding_rna_path['id'] = 'non-coding-rna-path'
	non_coding_rna_path['parametric:d'] = 'M{(baseline_x+pad_before)},{(baseline_y-baseline_offset)} L{(baseline_x+pad_before)},{(baseline_y-baseline_offset)-(height*0.7)} C{(baseline_x+pad_before)+(width*0.15)},{(baseline_y-baseline_offset)-(height*1.2)} {(baseline_x+pad_before)+(width*0.18)},{(baseline_y-baseline_offset)-(height*0.1)} {(baseline_x+pad_before)+(width*(5.0/15.0))},{(baseline_y-baseline_offset)-(height*0.7)} C{(baseline_x+pad_before)+(width*(0.15+(5.0/15.0)))},{(baseline_y-baseline_offset)-(height*1.2)} {(baseline_x+pad_before)+(width*(0.18+(5.0/15.0)))},{(baseline_y-baseline_offset)-(height*0.1)} {(baseline_x+pad_before)+(width*(10.0/15.0))},{(baseline_y-baseline_offset)-(height*0.7)} C{(baseline_x+pad_before)+(width*(0.15+(10.0/15.0)))},{(baseline_y-baseline_offset)-(height*1.2)} {(baseline_x+pad_before)+(width*(0.18+(10.0/15.0)))},{(baseline_y-baseline_offset)-(height*0.1)} {(baseline_x+pad_before)+(width*(15.0/15.0))},{(baseline_y-baseline_offset)-(height*0.7)} L{(baseline_x+pad_before)+width},{(baseline_y-baseline_offset)} Z'
	non_coding_rna_path['d'] = eval_parameterised_path(non_coding_rna_path['parametric:d'], params)
	non_coding_rna_path['style'] = style_text['filled-path']
	glyph_paths.append(non_coding_rna_path)
	return header_text, glyph_paths

def nucleic_acid_one_strand_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component parameters
	params['height'] = 12
	params['width'] = 20
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('Nucleic Acid 1 Strand', '', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-(height*0.5)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+height+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	nucleic_path = {}
	nucleic_path['class'] = 'unfilled-path'
	nucleic_path['id'] = 'nucleic-acid-path'
	nucleic_path['parametric:d'] = 'M{(baseline_x+pad_before)},{(baseline_y-baseline_offset)} C{(baseline_x+pad_before)+(width*0.15)},{(baseline_y-baseline_offset)-(height*0.5)} {(baseline_x+pad_before)+(width*0.18)},{(baseline_y-baseline_offset)+(height*0.5)} {(baseline_x+pad_before)+(width*(5.0/15.0))},{(baseline_y-baseline_offset)} C{(baseline_x+pad_before)+(width*(0.15+(5.0/15.0)))},{(baseline_y-baseline_offset)-(height*0.5)} {(baseline_x+pad_before)+(width*(0.18+(5.0/15.0)))},{(baseline_y-baseline_offset)+(height*0.5)} {(baseline_x+pad_before)+(width*(10.0/15.0))},{(baseline_y-baseline_offset)} C{(baseline_x+pad_before)+(width*(0.15+(10.0/15.0)))},{(baseline_y-baseline_offset)-(height*0.5)} {(baseline_x+pad_before)+(width*(0.18+(10.0/15.0)))},{(baseline_y-baseline_offset)+(height*0.5)} {(baseline_x+pad_before)+(width*(15.0/15.0))},{(baseline_y-baseline_offset)}'
	nucleic_path['d'] = eval_parameterised_path(nucleic_path['parametric:d'], params)
	nucleic_path['style'] = style_text['unfilled-path']
	glyph_paths.append(nucleic_path)
	return header_text, glyph_paths

def composite_svg (baseline_x=baseline_x, baseline_y=baseline_y):
	params = {}
	# General parameters
	params['baseline_x'] = baseline_x
	params['baseline_y'] = baseline_y
	params['baseline_offset'] = 0
	params['pad_before'] = 2
	params['pad_after'] = 2
	params['pad_top'] = 3
	params['pad_bottom'] = 3
	# Unspecified component parameters
	params['height'] = 12
	params['width'] = 40
	# Make the header text (SVG, bounding box, and baseline elements)
	header_text = svg_header('Composite', '', parametric_defaults=params, width=svg_width, height=svg_height)
	header_text += bounding_box('{baseline_x}', '{(baseline_y-baseline_offset)-pad_top}', '{pad_before+width+pad_after}', '{pad_top+height+pad_bottom}', params, style=style_text['bounding-box'])
	header_text += baseline('{baseline_x}', '{baseline_y}', '{pad_before+width+pad_after}', params, style=style_text['baseline'])
	# Hold the individual paths for the glyph
	glyph_paths = []
	# Generate the paths for the glyph and add to list of paths
	bg_path = {}
	bg_path['class'] = 'filled-background-path'
	bg_path['id'] = 'composite-background'
	bg_path['parametric:d'] = 'M{(baseline_x+pad_before)+(width*0.15)},{(baseline_y-baseline_offset)} L{(baseline_x+pad_before)+(width*0.15)},{(baseline_y-baseline_offset)-pad_top} L{(baseline_x+pad_before)+width-(width*0.15)},{(baseline_y-baseline_offset)-pad_top} L{(baseline_x+pad_before)+width-(width*0.15)},{(baseline_y-baseline_offset)} L{(baseline_x+pad_before)+width},{(baseline_y-baseline_offset)+height} L{(baseline_x+pad_before)},{(baseline_y-baseline_offset)+height} Z}'
	bg_path['d'] = eval_parameterised_path(bg_path['parametric:d'], params)
	bg_path['style'] = style_text['filled-background-path']
	glyph_paths.append(bg_path)
	composite_path1 = {}
	composite_path1['class'] = 'unfilled-path'
	composite_path1['id'] = 'composite-path'
	composite_path1['parametric:d'] = 'M{(baseline_x+pad_before)},{(baseline_y-baseline_offset)+height} L{(baseline_x+pad_before)+(width*0.37)},{(baseline_y-baseline_offset)+height}'
	composite_path1['d'] = eval_parameterised_path(composite_path1['parametric:d'], params)
	composite_path1['style'] = style_text['unfilled-path']
	glyph_paths.append(composite_path1)
	composite_path2 = {}
	composite_path2['class'] = 'unfilled-path'
	composite_path2['id'] = 'composite-path'
	composite_path2['parametric:d'] = 'M{(baseline_x+pad_before)+width-(width*0.37)},{(baseline_y-baseline_offset)+height} L{(baseline_x+pad_before)+width},{(baseline_y-baseline_offset)+height}'
	composite_path2['d'] = eval_parameterised_path(composite_path2['parametric:d'], params)
	composite_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(composite_path2)
	composite_path2 = {}
	composite_path2['class'] = 'unfilled-path'
	composite_path2['id'] = 'composite-path'
	composite_path2['parametric:d'] = 'M{(baseline_x+pad_before)+((width*0.15)*(10.0/10.0))},{(baseline_y-baseline_offset)+height-(height*(10.0/10.0))} L{(baseline_x+pad_before)+((width*0.15)*(8.0/10.0))},{(baseline_y-baseline_offset)+height-(height*(8.0/10.0))}'
	composite_path2['d'] = eval_parameterised_path(composite_path2['parametric:d'], params)
	composite_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(composite_path2)
	composite_path2 = {}
	composite_path2['class'] = 'unfilled-path'
	composite_path2['id'] = 'composite-path'
	composite_path2['parametric:d'] = 'M{(baseline_x+pad_before)+((width*0.15)*(6.0/10.0))},{(baseline_y-baseline_offset)+height-(height*(6.0/10.0))} L{(baseline_x+pad_before)+((width*0.15)*(4.0/10.0))},{(baseline_y-baseline_offset)+height-(height*(4.0/10.0))}'
	composite_path2['d'] = eval_parameterised_path(composite_path2['parametric:d'], params)
	composite_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(composite_path2)
	composite_path2 = {}
	composite_path2['class'] = 'unfilled-path'
	composite_path2['id'] = 'composite-path'
	composite_path2['parametric:d'] = 'M{(baseline_x+pad_before)+((width*0.15)*(2.0/10.0))},{(baseline_y-baseline_offset)+height-(height*(2.0/10.0))} L{(baseline_x+pad_before)+((width*0.15)*(0.0/10.0))},{(baseline_y-baseline_offset)+height-(height*(0.0/10.0))}'
	composite_path2['d'] = eval_parameterised_path(composite_path2['parametric:d'], params)
	composite_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(composite_path2)
	composite_path2 = {}
	composite_path2['class'] = 'unfilled-path'
	composite_path2['id'] = 'composite-path'
	composite_path2['parametric:d'] = 'M{(baseline_x+pad_before)+width-((width*0.15)*(10.0/10.0))},{(baseline_y-baseline_offset)+height-(height*(10.0/10.0))} L{(baseline_x+pad_before)+width-((width*0.15)*(8.0/10.0))},{(baseline_y-baseline_offset)+height-(height*(8.0/10.0))}'
	composite_path2['d'] = eval_parameterised_path(composite_path2['parametric:d'], params)
	composite_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(composite_path2)
	composite_path2 = {}
	composite_path2['class'] = 'unfilled-path'
	composite_path2['id'] = 'composite-path'
	composite_path2['parametric:d'] = 'M{(baseline_x+pad_before)+width-((width*0.15)*(6.0/10.0))},{(baseline_y-baseline_offset)+height-(height*(6.0/10.0))} L{(baseline_x+pad_before)+width-((width*0.15)*(4.0/10.0))},{(baseline_y-baseline_offset)+height-(height*(4.0/10.0))}'
	composite_path2['d'] = eval_parameterised_path(composite_path2['parametric:d'], params)
	composite_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(composite_path2)
	composite_path2 = {}
	composite_path2['class'] = 'unfilled-path'
	composite_path2['id'] = 'composite-path'
	composite_path2['parametric:d'] = 'M{(baseline_x+pad_before)+width-((width*0.15)*(2.0/10.0))},{(baseline_y-baseline_offset)+height-(height*(2.0/10.0))} L{(baseline_x+pad_before)+width-((width*0.15)*(0.0/10.0))},{(baseline_y-baseline_offset)+height-(height*(0.0/10.0))}'
	composite_path2['d'] = eval_parameterised_path(composite_path2['parametric:d'], params)
	composite_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(composite_path2)
	composite_path2 = {}
	composite_path2['class'] = 'unfilled-path'
	composite_path2['id'] = 'composite-path'
	composite_path2['parametric:d'] = 'M{(baseline_x+pad_before)+(width*0.43)},{(baseline_y-baseline_offset)+height} L{(baseline_x+pad_before)+(width*0.47)},{(baseline_y-baseline_offset)+height}'
	composite_path2['d'] = eval_parameterised_path(composite_path2['parametric:d'], params)
	composite_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(composite_path2)
	composite_path2 = {}
	composite_path2['class'] = 'unfilled-path'
	composite_path2['id'] = 'composite-path'
	composite_path2['parametric:d'] = 'M{(baseline_x+pad_before)+(width*0.53)},{(baseline_y-baseline_offset)+height} L{(baseline_x+pad_before)+(width*0.57)},{(baseline_y-baseline_offset)+height}'
	composite_path2['d'] = eval_parameterised_path(composite_path2['parametric:d'], params)
	composite_path2['style'] = style_text['unfilled-path']
	glyph_paths.append(composite_path2)
	return header_text, glyph_paths

###############################################################################
# Generate complete set of SVG files
###############################################################################
 
# Add new glyphs in here until whole set is present
glyphs_to_process = [
	['RibosomeEntrySite.svg', rbs_svg],
	['Promoter.svg', promoter_svg],
	['Terminator.svg', terminator_svg],
	['CDS.svg', cds_svg],
	['Primer.svg', primer_svg],
	['OriginOfReplication.svg', origin_of_replication_svg],
	['Unspecified.svg', unspecified_svg],
	['OmittedDetail.svg', omitted_detail_svg],
	['RecombinationSite.svg', recombination_site_svg],
	['NoGlyph.svg', no_glyph_svg],
	['Operator.svg', operator_svg],
	['AssemblyScar.svg', assembly_scar_svg],
	['BluntRestrictionSite.svg', blunt_restriction_site_svg],
	['EngineeredRegion.svg', engineered_region_svg],
	['Insulator.svg', insulator_svg],
	['OriginOfTransfer.svg', origin_of_transfer_svg],
	['StickyEndRestrictionEnzymeCleavageSite5.svg', sticky_restriction_site_5_svg],
	['StickyEndRestrictionEnzymeCleavageSite3.svg', sticky_restriction_site_3_svg],
	['OverhangSite5.svg', overhang_site_5_svg],
	['OverhangSite3.svg', overhang_site_3_svg],
	['Signature.svg', signature_svg],
	['PolyASite.svg', poly_a_site_svg],
	['DNALocation.svg', dna_location_svg],
	['DNACleavageSite.svg', dna_cleavage_site_svg],
	['DNAStabilityElement.svg', dna_stability_element_svg],
	['Spacer.svg', spacer_svg],
	['Aptamer.svg', aptamer_svg],
	['NonCodingRNA.svg', non_coding_rna_svg],
	['NucleicAcidOneStrand.svg', nucleic_acid_one_strand_svg],
	['Composite.svg', composite_svg]]

# Final glyphs saved here with details (e.g. baseline and bounding box)
OUTPUT_PREFIX_FULL = './glyphs_2.0/'
INCLUDE_BOUNDING_BOX = True
INCLUDE_BASELINE = True

glyphs_to_process = [['Terminator.svg', terminator_svg],
                     ['Promoter.svg', promoter_svg],
                     ['RibosomeEntrySite.svg', rbs_svg],
                     ['CDS.svg', cds_svg]]

for el in glyphs_to_process:
	header_text, glyph_paths = el[1]()
	write_glyph_svg(OUTPUT_PREFIX_FULL+el[0], header_text, glyph_paths)
